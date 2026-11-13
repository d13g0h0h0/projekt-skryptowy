from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.accounts.serializers import AuthorSerializer

from .models import SubTask, Task


class SubTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTask
        fields = ["id", "content"]


class TaskSummarySerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Task
        fields = ["id", "title", "author", "created_at", "updated_at"]


class TaskDetailSerializer(TaskSummarySerializer):
    subtasks = serializers.SerializerMethodField()

    class Meta(TaskSummarySerializer.Meta):
        fields = [*TaskSummarySerializer.Meta.fields, "content", "subtasks"]

    @extend_schema_field(SubTaskSerializer(many=True))
    def get_subtasks(self, task):
        return SubTaskSerializer(task.subtasks.order_by("position"), many=True).data



class SubTaskWriteSerializer(serializers.Serializer):
    content = serializers.CharField(max_length=255)


class TaskWriteSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    content = serializers.CharField()
    subtasks = SubTaskWriteSerializer(many=True, required=False, allow_null=True)