from rest_framework import serializers

from apps.accounts.serializers import AuthorSerializer

from .models import Solution, SolutionPart, Vote


class SolutionPartSerializer(serializers.ModelSerializer):
    subtask_id = serializers.IntegerField()

    class Meta:
        model = SolutionPart
        fields = ["id", "subtask_id", "content"]


class SolutionSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    parts = SolutionPartSerializer(many=True, read_only=True)
    score = serializers.IntegerField(help_text="Sum of all votes.")
    my_vote = serializers.IntegerField(allow_null=True, help_text="Current user's vote: 1, -1 or null.")

    class Meta:
        model = Solution
        fields = ["id", "author", "content", "parts", "score", "my_vote", "created_at", "updated_at"]


class VoteSerializer(serializers.ModelSerializer):
    user = AuthorSerializer(read_only=True)

    class Meta:
        model = Vote
        fields = ["id", "user", "value", "created_at"]


class StrictIntegerField(serializers.IntegerField):
    def to_internal_value(self, data):
        if isinstance(data, bool) or not isinstance(data, int):
            self.fail("invalid")
        return super().to_internal_value(data)


class SolutionPartWriteSerializer(serializers.Serializer):
    subtask_id = StrictIntegerField()
    content = serializers.CharField()


class SolutionWriteSerializer(serializers.Serializer):
    content = serializers.CharField(required=False, allow_blank=True, default="")
    parts = SolutionPartWriteSerializer(many=True, required=False, allow_null=True)

    def validate(self, data):
        parts = data.get("parts") or []
        subtask_ids = set(self.context["task"].subtasks.values_list("id", flat=True))

        if subtask_ids:
            ids = [p["subtask_id"] for p in parts]
            if len(set(ids)) != len(ids) or set(ids) != subtask_ids:
                raise serializers.ValidationError(
                    {"parts": "Exactly one part is required for every subtask of the task."}
                )
        else:
            if parts:
                raise serializers.ValidationError({"parts": "This task has no subtasks."})
            if not data["content"]:
                raise serializers.ValidationError({"content": "This field is required."})

        data["parts"] = parts
        return data


class VoteWriteSerializer(serializers.Serializer):
    value = StrictIntegerField(help_text="1 (up) or -1 (down)")

    def validate_value(self, value):
        if value not in Vote.Value.values:
            raise serializers.ValidationError("Must be 1 or -1.")
        return value