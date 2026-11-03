import json
from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .models import Task, SubTask


MAX_TITLE = 255
MAX_SUBTASK = 255

def get_default_author():
    # TEMPORARY - after adding auth, replace with getting author from request
    User = get_user_model()
    user, created = User.objects.get_or_create(
        username="dev",
        defaults={"email": "dev@example.com"},
    )
    if created:
        user.set_unusable_password()
        user.save()
    return user

def author_to_dict(user):
    return {"id": user.id, "username": user.username}


def task_to_summary(task):
    return {
        "id": task.id,
        "title": task.title,
        "author": author_to_dict(task.author),
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat(),
    }


def task_to_detail(task):
    return {
        **task_to_summary(task),
        "content": task.content,
        "subtasks": [
            {"id": s.id, "content": s.content}
            for s in task.subtasks.order_by("position")
        ],
    }

def parse_body(request):
    try:
        data = json.loads(request.body)
        title = data["title"].strip()
        content = data["content"].strip()
        subtasks = data.get("subtasks")
        if subtasks is not None:
            subtasks = [s["content"].strip() for s in subtasks]
    except (ValueError, KeyError, TypeError, AttributeError):
        return None

    if not title or len(title) > MAX_TITLE or not content:
        return None
    if subtasks is not None and any(not c or len(c) > MAX_SUBTASK for c in subtasks):
        return None
    return title, content, subtasks


def create_subtasks(task, contents):
    SubTask.objects.bulk_create(
        [SubTask(task=task, content=c, position=i) for i, c in enumerate(contents)]
    )


INVALID = {"error": "Invalid request data. 'title' and 'content' are required."}


@method_decorator(csrf_exempt, name="dispatch")
class TaskListView(View):
    def get(self, request):
        tasks = Task.objects.prefetch_related("subtasks")
        return JsonResponse([task_to_summary(t) for t in tasks], safe=False)

    def post(self, request):
        parsed = parse_body(request)
        if parsed is None:
            return JsonResponse(INVALID, status=400)
        title, content, subtasks = parsed

        with transaction.atomic():
            task = Task.objects.create(
                title=title, content=content, author=get_default_author()
            )
            create_subtasks(task, subtasks or [])
        return JsonResponse(task_to_detail(task), status=201)


@method_decorator(csrf_exempt, name="dispatch")
class TaskDetailView(View):
    def get(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        return JsonResponse(task_to_detail(task))

    def put(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        parsed = parse_body(request)
        if parsed is None:
            return JsonResponse(INVALID, status=400)
        title, content, subtasks = parsed

        with transaction.atomic():
            task.title = title
            task.content = content
            task.save()
            if subtasks is not None:
                task.subtasks.all().delete()
                create_subtasks(task, subtasks)
        return JsonResponse(task_to_detail(task))

    def delete(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        task.delete()
        return HttpResponse(status=204)