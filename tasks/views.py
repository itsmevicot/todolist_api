from typing import Optional

from drf_yasg import openapi
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema

from tasks.serializers import (
    TaskResponseSerializer,
    TaskCreateSerializer,
    TaskUpdateSerializer,
    TaskDetailSerializer,
    TaskFilterSerializer,
)
from tasks.service import TaskService


class TaskListView(APIView):
    """
    API view to handle task listing and creation.
    """
    permission_classes = [IsAuthenticated]

    def __init__(
        self,
        task_service: Optional[TaskService] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.task_service = task_service or TaskService()

    @swagger_auto_schema(
        operation_summary="List tasks",
        operation_description="Retrieve tasks for the authenticated user based on optional filters.",
        query_serializer=TaskFilterSerializer,
        responses={
            200: TaskResponseSerializer(many=True)
        },
    )
    def get(self, request):
        """
        Get tasks for the authenticated user based on filters.
        """
        filter_serializer = TaskFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)

        is_active = filter_serializer.validated_data.get("is_active")
        task_status = filter_serializer.validated_data.get("status")

        tasks = self.task_service.get_tasks(user=request.user, is_active_filter=is_active, status_filter=task_status)
        serializer = TaskResponseSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Create a task",
        operation_description="Create a new task for the authenticated user.",
        request_body=TaskCreateSerializer,
        responses={
            201: TaskResponseSerializer
        },
    )
    def post(self, request):
        """
        Create a new task for the authenticated user.
        """
        serializer = TaskCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = self.task_service.create_task(serializer.validated_data, user=request.user)
        return Response(TaskResponseSerializer(task).data, status=status.HTTP_201_CREATED)


class TaskDetailView(APIView):
    """
    API view to handle task details, updates, and deletions.
    """
    permission_classes = [IsAuthenticated]

    def __init__(
        self,
        task_service: Optional[TaskService] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.task_service = task_service or TaskService()

    @swagger_auto_schema(
        operation_summary="Get task details",
        operation_description="Retrieve details of a specific task for the authenticated user.",
        responses={
            200: TaskDetailSerializer
        },
    )
    def get(self, request, task_id):
        """
        Get task details for the authenticated user.
        """
        task = self.task_service.get_task_details(task_id, user=request.user)
        serializer = TaskDetailSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Update a task",
        operation_description="Update task details for the authenticated user. Allows partial updates.",
        request_body=TaskUpdateSerializer,
        responses={
            200: TaskDetailSerializer
        },
    )
    def put(self, request, task_id):
        """
        Update task details for the authenticated user. Allows partial updates.
        """
        serializer = TaskUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        task = self.task_service.update_task(task_id, serializer.validated_data, user=request.user)
        return Response(TaskDetailSerializer(task).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Delete a task",
        operation_description="Delete a task for the authenticated user. Supports soft or hard deletion.",
        manual_parameters=[
            openapi.Parameter(
                "hard_delete",
                openapi.IN_QUERY,
                description="Set to true for hard delete, otherwise it defaults to soft delete.",
                type=openapi.TYPE_BOOLEAN,
            ),
        ],
        responses={
            204: "Task deleted successfully."
        },
    )
    def delete(self, request, task_id):
        """
        Delete a task for the authenticated user (soft delete by default).
        """
        hard_delete = request.query_params.get("hard_delete", "false").lower() == "true"
        self.task_service.delete_task(task_id, user=request.user, hard_delete=hard_delete)
        return Response(status=status.HTTP_204_NO_CONTENT)
