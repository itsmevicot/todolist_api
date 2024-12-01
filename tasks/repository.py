from datetime import timedelta
from typing import Optional, List

from django.utils.timezone import now

from tasks.enum import TaskStatus
from tasks.models import Task


class TaskRepository:
    @staticmethod
    def get_tasks_by_user(user) -> List[Task]:
        """
        Fetch all active tasks for a user.
        """
        return Task.objects.filter(owner=user)

    @staticmethod
    def get_task_by_id(task_id: int) -> Optional[Task]:
        """
        Fetch a task by ID, including inactive tasks.
        """
        return Task.objects.filter(id=task_id).first()

    @staticmethod
    def create_task(owner, title: str, description: str, status: str = "CREATED", expires_at=None) -> Task:
        """
        Create a new task.
        """
        return Task.objects.create(
            owner=owner, title=title, description=description, status=status, expires_at=expires_at
        )

    @staticmethod
    def update_task(task: Task, **kwargs) -> Task:
        """
        Update an existing task.
        """
        for key, value in kwargs.items():
            setattr(task, key, value)
        task.save()
        return task

    @staticmethod
    def get_tasks_expiring_soon(hours: int) -> List[Task]:
        """
        Fetch tasks that are set to expire within the next `hours`.
        """
        three_hours_later = now() + timedelta(hours=hours)
        return Task.objects.filter(
            expires_at__lte=three_hours_later,
            expires_at__gt=now(),
            status=TaskStatus.CREATED.value,
        )

    @staticmethod
    def get_expired_tasks() -> List[Task]:
        """
        Fetch tasks whose expiry date has passed and are still active.
        """
        return Task.objects.filter(
            expires_at__lt=now(),
            active=True
        ).exclude(status=TaskStatus.EXPIRED.value)

    @staticmethod
    def update_task_status(task: Task, status: TaskStatus) -> Task:
        """
        Update the status of a task and save it.
        """
        task.status = status
        task.save()
        return task
