import json

from django.db import transaction
from django.db.models import OuterRef, Sum, Subquery
from django.db.models.functions import Coalesce
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .models import Solution, SolutionPart, Vote
from apps.tasks.models import Task
from apps.tasks.views import author_to_dict, get_default_author

INVALID_SOLUTION = {
    "error": "Invalid request data. If the task has subtasks, 'parts' must contain exactly one "
             "non-empty {'subtask_id', 'content'} for every subtask; otherwise 'content' is required."
}
INVALID_VOTE = {"error": "Invalid request data. 'value' must be 1 or -1."}


def solutions_qs(user):
    """Solutions with author and parts loaded, vote score and `voted` (did `user` vote) annotated."""
    return (
        Solution.objects
        .select_related("author")
        .prefetch_related("parts")
        .annotate(
            score=Coalesce(Sum("votes__value"), 0),
            my_vote=Subquery( Vote.objects.filter(solution=OuterRef("pk"), user=user).values("value")[:1] ),
        )
    )


def solution_to_dict(solution):
    return {
        "id": solution.id,
        "author": author_to_dict(solution.author),
        "content": solution.content,
        "parts": [
            {"id": p.id, "subtask_id": p.subtask_id, "content": p.content}
            for p in solution.parts.all()
        ],
        "score": solution.score,
        "my_vote": solution.my_vote,
        "created_at": solution.created_at.isoformat(),
        "updated_at": solution.updated_at.isoformat(),
    }


def vote_to_dict(vote):
    return {
        "id": vote.id,
        "user": author_to_dict(vote.user),
        "value": vote.value,
        "created_at": vote.created_at.isoformat(),
    }


def parse_solution_body(request, task):
    try:
        data = json.loads(request.body)
        content = data.get("content", "").strip()
        parts = data.get("parts")
        if parts is not None:
            parts = [
                {"subtask_id": p["subtask_id"], "content": p["content"].strip()}
                for p in parts
            ]
    except (ValueError, KeyError, TypeError, AttributeError):
        return None

    task_subtask_ids = set(task.subtasks.values_list("id", flat=True))

    if task_subtask_ids:
        # task with subtasks: exactly one non-empty part per subtask
        if not parts:
            return None
        ids = [p["subtask_id"] for p in parts]
        if any(not isinstance(i, int) or isinstance(i, bool) for i in ids):
            return None
        if len(set(ids)) != len(ids) or set(ids) != task_subtask_ids:
            return None
        if any(not p["content"] for p in parts):
            return None
    else:
        # task without subtasks: plain content only
        if parts or not content:
            return None
        parts = []

    return content, parts


def parse_vote_body(request):
    try:
        value = json.loads(request.body)["value"]
    except (ValueError, KeyError, TypeError):
        return None
    if isinstance(value, bool) or value not in Vote.Value.values:
        return None
    return value


def create_parts(solution, parts):
    SolutionPart.objects.bulk_create(
        [SolutionPart(solution=solution, subtask_id=p["subtask_id"], content=p["content"])
         for p in parts]
    )


@method_decorator(csrf_exempt, name="dispatch")
class SolutionListView(View):

    def get(self, request, task_pk):
        task = get_object_or_404(Task, pk=task_pk)
        solutions = (
            solutions_qs(get_default_author())
            .filter(task=task)
            .order_by("-score", "-created_at")
        )
        return JsonResponse([solution_to_dict(s) for s in solutions], safe=False)

    def post(self, request, task_pk):
        task = get_object_or_404(Task, pk=task_pk)
        parsed = parse_solution_body(request, task)
        if parsed is None:
            return JsonResponse(INVALID_SOLUTION, status=400)
        content, parts = parsed

        with transaction.atomic():
            solution = Solution.objects.create(
                task=task, content=content, author=get_default_author()
            )
            create_parts(solution, parts)
        solution = solutions_qs(get_default_author()).get(pk=solution.pk)
        return JsonResponse(solution_to_dict(solution), status=201)


@method_decorator(csrf_exempt, name="dispatch")
class SolutionDetailView(View):
    # only put and delete - reading in the solutions list

    def put(self, request, pk):
        solution = get_object_or_404(Solution, pk=pk)
        parsed = parse_solution_body(request, solution.task)
        if parsed is None:
            return JsonResponse(INVALID_SOLUTION, status=400)
        content, parts = parsed

        with transaction.atomic():
            solution.content = content
            solution.save()
            solution.parts.all().delete()
            create_parts(solution, parts)
        solution = solutions_qs(get_default_author()).get(pk=pk)
        return JsonResponse(solution_to_dict(solution))

    def delete(self, request, pk):
        solution = get_object_or_404(Solution, pk=pk)
        solution.delete()
        return HttpResponse(status=204)


@method_decorator(csrf_exempt, name="dispatch")
class SolutionVoteView(View):
    # current user's vote state is in the solution list as `voted`

    def put(self, request, solution_pk):  # created a vote or change the existing value
        solution = get_object_or_404(Solution, pk=solution_pk)
        value = parse_vote_body(request)
        if value is None:
            return JsonResponse(INVALID_VOTE, status=400)

        vote, created = Vote.objects.update_or_create(
            user=get_default_author(), solution=solution, defaults={"value": value}
        )
        return JsonResponse(vote_to_dict(vote), status=201 if created else 200)

    def delete(self, request, solution_pk):
        vote = get_object_or_404(Vote, solution_id=solution_pk, user=get_default_author())
        vote.delete()
        return HttpResponse(status=204)