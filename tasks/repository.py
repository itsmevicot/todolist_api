from typing import Optional, List

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
