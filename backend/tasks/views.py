import json
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .models import Task, SubTask


MAX_SUBTASK = 255


def task_to_dict(task):
    return {
        "id": task.id,
        "content": task.content,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat(),
        "subtasks": [{"id": s.id, "content": s.content} for s in task.subtasks.all()],
    }


def parse_body(request):
    try:
        data = json.loads(request.body)
        content = data["content"].strip()
        subtasks = data.get("subtasks")
        if subtasks is not None:
            subtasks = [s["content"].strip() for s in subtasks]
    except (ValueError, KeyError, TypeError, AttributeError):
        return None

    if not content:
        return None
    if subtasks is not None and any(not c or len(c) > MAX_SUBTASK for c in subtasks):
        return None
    return content, subtasks

@method_decorator(csrf_exempt, name="dispatch")
class TaskListView(View):
    def get(self, request):
        tasks = Task.objects.prefetch_related("subtasks")
        return JsonResponse([task_to_dict(t) for t in tasks], safe=False)

    def post(self, request):
        parsed = parse_body(request)
        if parsed is None:
            return JsonResponse({"error": "Invalid request data. 'content' is required."}, status=400)
        content, subtasks = parsed

        task = Task.objects.create(content=content)
        SubTask.objects.bulk_create(
            [SubTask(task=task, content=c) for c in (subtasks or [])]
        )
        return JsonResponse(task_to_dict(task), status=201)

@method_decorator(csrf_exempt, name="dispatch")
class TaskDetailView(View):
    def get(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        return JsonResponse(task_to_dict(task))

    def put(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        parsed = parse_body(request)
        if parsed is None:
            return JsonResponse({"error": "Invalid request data. 'content' is required."}, status=400)
        content, subtasks = parsed

        task.content = content
        task.save()
        if subtasks is not None:
            task.subtasks.all().delete()
            SubTask.objects.bulk_create([SubTask(task=task, content=c) for c in subtasks])
        return JsonResponse(task_to_dict(task))

    def delete(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        task.delete()
        return HttpResponse(status=204)