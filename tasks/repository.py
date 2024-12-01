from datetime import timedelta, datetime
from typing import Optional, List

from django.db.models import QuerySet
from django.utils.timezone import now

from tasks.enum import TaskStatus
from tasks.models import Task
from users.models import User


class TaskRepository:
    @staticmethod
    def get_tasks_by_user(
            user: User,
            is_active_filter: Optional[bool] = True,
            status_filter: Optional[TaskStatus] = None
    ) -> QuerySet:
        """
        Fetch tasks for a user with optional filters.

        :param user: The owner of the tasks.
        :param is_active_filter: A boolean indicating whether to fetch active tasks.
        :param status_filter: The status of the task (e.g., 'TODO', 'IN_PROGRESS', 'DONE').
        :return: A QuerySet of tasks.
        """
        tasks = Task.objects.filter(owner=user)

        if is_active_filter is not None:
            tasks = tasks.filter(active=is_active_filter)

        if status_filter:
            tasks = tasks.filter(status=status_filter)

        return tasks

    @staticmethod
    def get_task_by_id(task_id: int) -> Optional[Task]:
        """
        Fetch a task by ID, including inactive tasks.
        """
        return Task.objects.filter(id=task_id).first()

    @staticmethod
    def create_task(
            owner: User,
            title: str,
            description: str,
            status: TaskStatus = TaskStatus.CREATED.value,
            expires_at: datetime = None
    ) -> Task:
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
        Fetch tasks that are set to expire within the next `hours`, excluding tasks
        with a status of DONE, EXPIRED or CANCELLED.
        """
        three_hours_later = now() + timedelta(hours=hours)
        return Task.objects.filter(
            expires_at__lte=three_hours_later,
            expires_at__gt=now(),
        ).exclude(
            status__in=[TaskStatus.DONE.value, TaskStatus.EXPIRED.value, TaskStatus.CANCELLED.value]
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
