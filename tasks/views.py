from typing import Optional

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from tasks.serializers import TaskSerializer, TaskCreateSerializer, TaskUpdateSerializer
from tasks.service import TaskService


class TaskListView(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(
        self,
        task_service: Optional[TaskService] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.task_service = task_service or TaskService()

    def get(self, request):
        """
        Get all tasks for the authenticated user.
        """
        tasks = self.task_service.get_tasks(user=request.user)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Create a new task for the authenticated user.
        """
        serializer = TaskCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = self.task_service.create_task(serializer.validated_data, user=request.user)
        return Response(TaskSerializer(task).data, status=status.HTTP_201_CREATED)


class TaskDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(
        self,
        task_service: Optional[TaskService] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.task_service = task_service or TaskService()

    def get(self, request, task_id):
        """
        Get task details for the authenticated user.
        """
        task = self.task_service.get_task_details(task_id, user=request.user)
        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, task_id):
        """
        Update task details for the authenticated user.
        """
        serializer = TaskUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = self.task_service.update_task(task_id, serializer.validated_data, user=request.user)
        return Response(TaskSerializer(task).data, status=status.HTTP_200_OK)

    def delete(self, request, task_id):
        """
        Delete a task for the authenticated user (soft delete by default).
        """
        hard_delete = request.query_params.get("hard_delete", "false").lower() == "true"
        self.task_service.delete_task(task_id, user=request.user, hard_delete=hard_delete)
        return Response(status=status.HTTP_204_NO_CONTENT)
