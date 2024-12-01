import logging
from typing import Optional, List, Dict

from django.db import transaction

from tasks.models import Task
from tasks.repository import TaskRepository
from users.models import User
from utils.exceptions import TaskNotFoundException, TaskUnauthorizedAccessException

logger = logging.getLogger(__name__)


class TaskService:
    def __init__(
        self,
        task_repository: Optional[TaskRepository] = None,
    ):
        self.task_repository = task_repository or TaskRepository()

    def get_tasks(self, user: User) -> List[Task]:
        logger.info(f"Fetching all tasks for user ID: {user.id}.")
        return self.task_repository.get_tasks_by_user(user)

    def get_task_details(self, task_id: int, user: User) -> Task:
        logger.info(f"Fetching task with ID: {task_id} for user ID: {user.id}.")
        task = self.task_repository.get_task_by_id(task_id)
        if not task:
            logger.error(f"Task with ID {task_id} not found.")
            raise TaskNotFoundException(task_id)
        if task.owner != user:
            logger.error(f"Unauthorized access to task ID {task_id} by user ID {user.id}.")
            raise TaskUnauthorizedAccessException()
        return task

    @transaction.atomic
    def create_task(self, data: Dict, user) -> Task:
        """
        Create a new task for the authenticated user.
        """
        try:
            logger.info(f"Creating task for user ID {user.id} with data: {data}")
            data["owner"] = user
            task = self.task_repository.create_task(**data)
            logger.info(f"Successfully created task ID {task.id} for user ID {user.id}")
            return task
        except Exception as e:
            logger.error(f"Failed to create task for user ID {user.id}: {str(e)}")
            raise

    @transaction.atomic
    def update_task(self, task_id: int, data: Dict, user: User) -> Task:
        """
        Update an existing task for the authenticated user.
        """
        try:
            task = self.get_task_details(task_id, user)
            logger.info(f"Updating task ID {task_id} for user ID {user.id} with data: {data}")
            updated_task = self.task_repository.update_task(task, **data)
            logger.info(f"Successfully updated task ID {task_id} for user ID {user.id}")
            return updated_task
        except TaskNotFoundException:
            logger.error(f"Task with ID {task_id} not found for update.")
            raise
        except TaskUnauthorizedAccessException:
            logger.error(f"Unauthorized update attempt for task ID {task_id} by user ID {user.id}.")
            raise
        except Exception as e:
            logger.error(f"Failed to update task ID {task_id} for user ID {user.id}: {str(e)}")
            raise

    @transaction.atomic
    def delete_task(self, task_id: int, user: User, hard_delete: bool = False):
        """
        Delete a task. Perform a hard delete if `hard_delete` is True.
        """
        task = self.get_task_details(task_id, user)
        if hard_delete:
            logger.info(f"Hard deleting task with ID {task_id} for user ID: {user.id}.")
            task.delete(hard_delete=True)
        else:
            logger.info(f"Soft deleting task with ID {task_id} for user ID: {user.id}.")
            task.delete()
