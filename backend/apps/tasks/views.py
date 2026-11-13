from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import SubTask, Task
from .serializers import TaskDetailSerializer, TaskSummarySerializer, TaskWriteSerializer


def create_subtasks(task, subtasks):
    SubTask.objects.bulk_create(
        [SubTask(task=task, content=s["content"], position=i) for i, s in enumerate(subtasks)]
    )


def get_own_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if task.author_id != request.user.id:
        raise PermissionDenied("Only the author can modify this task.")
    return task


class TaskListView(APIView):
    required_scopes = {"GET": ["tasks:read"], "POST": ["tasks:write"]}

    @extend_schema(responses=TaskSummarySerializer(many=True))
    def get(self, request):
        tasks = Task.objects.select_related("author")
        return Response(TaskSummarySerializer(tasks, many=True).data)

    @extend_schema(request=TaskWriteSerializer, responses={201: TaskDetailSerializer})
    def post(self, request):
        serializer = TaskWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        with transaction.atomic():
            task = Task.objects.create(
                title=data["title"], content=data["content"], author=request.user
            )
            create_subtasks(task, data.get("subtasks") or [])
        return Response(TaskDetailSerializer(task).data, status=201)


class TaskDetailView(APIView):
    required_scopes = {"GET": ["tasks:read"], "PUT": ["tasks:write"], "DELETE": ["tasks:write"]}

    @extend_schema(responses=TaskDetailSerializer)
    def get(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        return Response(TaskDetailSerializer(task).data)

    @extend_schema(request=TaskWriteSerializer, responses=TaskDetailSerializer)
    def put(self, request, pk):
        task = get_own_task(request, pk)
        serializer = TaskWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        with transaction.atomic():
            task.title = data["title"]
            task.content = data["content"]
            task.save()
            if data.get("subtasks") is not None:
                task.subtasks.all().delete()
                create_subtasks(task, data["subtasks"])
        return Response(TaskDetailSerializer(task).data)

    @extend_schema(responses={204: None})
    def delete(self, request, pk):
        get_own_task(request, pk).delete()
        return Response(status=204)