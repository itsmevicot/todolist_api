from rest_framework import serializers
from tasks.models import Task
from tasks.enum import TaskStatus


class TaskResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["id", "title", "status", "expires_at"]


class TaskDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["id", "title", "description", "status", "expires_at"]


class TaskFilterSerializer(serializers.Serializer):
    is_active = serializers.BooleanField(required=False, default=True)
    status = serializers.ChoiceField(choices=TaskStatus.choices(), required=False)


class TaskCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField()
    status = serializers.ChoiceField(choices=TaskStatus.choices(), required=False)
    expires_at = serializers.DateTimeField(required=False, allow_null=True)

    def validate_status(self, value):
        if value not in [status.value for status in TaskStatus]:
            raise serializers.ValidationError(f"Invalid status value: {value}")
        return value


class TaskUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False)
    status = serializers.ChoiceField(choices=TaskStatus.choices(), required=False)
    expires_at = serializers.DateTimeField(required=False, allow_null=True)

    def validate_status(self, value):
        if value not in [status.value for status in TaskStatus]:
            raise serializers.ValidationError(f"Invalid status value: {value}")
        return value
