from datetime import timedelta
from unittest.mock import patch

import pytest
from django.utils.timezone import now
from rest_framework import status

from tasks.enum import TaskStatus
from tasks.models import Task
from tasks.serializers import TaskCreateSerializer
from utils.exceptions import TaskNotFoundException, TaskUnauthorizedAccessException


@pytest.mark.django_db
def test_get_all_tasks(authenticated_client, test_user, sample_task):
    """
    Test retrieving all tasks for the authenticated user.
    """
    response = authenticated_client.get("/tasks/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["title"] == sample_task.title


@pytest.mark.django_db
def test_create_task(authenticated_client, test_user):
    """
    Test creating a new task for the authenticated user.
    """
    payload = {
        "title": "New Task",
        "description": "Description of the new task",
        "status": TaskStatus.IN_PROGRESS.value,
        "expires_at": "31/12/2024T23:59:59"
    }
    response = authenticated_client.post("/tasks/", payload)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["title"] == payload["title"]
    assert response.data["status"] == payload["status"]
    assert Task.objects.filter(owner=test_user, title=payload["title"]).exists()


@pytest.mark.django_db
def test_get_task_details(authenticated_client, sample_task):
    """
    Test retrieving details of a specific task.
    """
    response = authenticated_client.get(f"/tasks/{sample_task.id}/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["title"] == sample_task.title
    assert response.data["status"] == sample_task.status


@pytest.mark.django_db
def test_update_task(authenticated_client, sample_task):
    """
    Test updating a specific task.
    """
    payload = {"title": "Updated Task Title", "status": TaskStatus.DONE.value}
    response = authenticated_client.put(f"/tasks/{sample_task.id}/", payload)
    assert response.status_code == status.HTTP_200_OK
    sample_task.refresh_from_db()
    assert sample_task.title == payload["title"]
    assert sample_task.status == payload["status"]


@pytest.mark.django_db
def test_delete_task_soft(authenticated_client, sample_task):
    """
    Test soft-deleting a specific task.
    """
    response = authenticated_client.delete(f"/tasks/{sample_task.id}/")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    sample_task.refresh_from_db()
    assert sample_task.active is False


@pytest.mark.django_db
def test_delete_task_hard(authenticated_client, sample_task):
    """
    Test hard-deleting a specific task.
    """
    response = authenticated_client.delete(f"/tasks/{sample_task.id}/?hard_delete=true")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Task.objects.filter(id=sample_task.id).exists()


@pytest.mark.django_db
def test_get_tasks_expiring_soon(task_repository, sample_task):
    """
    Test fetching tasks that are expiring within the next X hours.
    """
    sample_task.expires_at = now() + timedelta(hours=2)
    sample_task.save()

    expiring_tasks = task_repository.get_tasks_expiring_soon(hours=3)
    assert len(expiring_tasks) == 1
    assert expiring_tasks[0] == sample_task


@pytest.mark.django_db
def test_get_expired_tasks(task_repository, sample_task):
    """
    Test fetching tasks whose expiry date has passed but are still active.
    """
    sample_task.expires_at = now() - timedelta(hours=1)
    sample_task.save()

    expired_tasks = task_repository.get_expired_tasks()
    assert len(expired_tasks) == 1
    assert expired_tasks[0] == sample_task


@pytest.mark.django_db
def test_update_task_status(task_repository, sample_task):
    """
    Test updating the status of a task.
    """
    task_repository.update_task_status(sample_task, TaskStatus.DONE.value)
    sample_task.refresh_from_db()
    assert sample_task.status == TaskStatus.DONE.value


@pytest.mark.django_db
def test_get_task_details_not_found(task_service, test_user):
    """
    Test fetching a task that doesn't exist raises TaskNotFoundException.
    """
    with pytest.raises(TaskNotFoundException):
        task_service.get_task_details(task_id=999, user=test_user)


@pytest.mark.django_db
def test_get_task_details_unauthorized(task_service, test_user, sample_task, another_user):
    """
    Test fetching a task not owned by the user raises TaskUnauthorizedAccessException.
    """
    sample_task.owner = another_user
    sample_task.save()

    with pytest.raises(TaskUnauthorizedAccessException):
        task_service.get_task_details(task_id=sample_task.id, user=test_user)


@pytest.mark.django_db
def test_task_model_str(sample_task):
    """
    Test the string representation of the Task model.
    """
    assert str(sample_task) == sample_task.title


@pytest.mark.django_db
def test_get_tasks_by_user_with_status_filter(task_repository, sample_task):
    """
    Test filtering tasks by user and status.
    """
    sample_task.status = TaskStatus.IN_PROGRESS.value
    sample_task.save()

    tasks = task_repository.get_tasks_by_user(
        user=sample_task.owner,
        status_filter=TaskStatus.IN_PROGRESS.value,
    )

    assert len(tasks) == 1
    assert tasks[0] == sample_task


def test_task_serializer_invalid_status():
    """
    Test the TaskCreateSerializer with an invalid status.
    """
    invalid_data = {
        "title": "Test Task",
        "description": "This is a test task.",
        "status": "INVALID_STATUS",
    }
    serializer = TaskCreateSerializer(data=invalid_data)
    assert not serializer.is_valid()
    assert "status" in serializer.errors

    assert "INVALID_STATUS" in str(serializer.errors["status"][0])


@pytest.mark.django_db
def test_create_task_exception(task_service, test_user):
    """
    Test exception handling during task creation.
    """
    invalid_data = {"title": "New Task"}

    with patch("tasks.service.TaskRepository.create_task",
               side_effect=Exception("Database error")) as mock_create_task, patch(
            "tasks.service.logger.error") as mock_logger:
        with pytest.raises(Exception, match="Database error"):
            task_service.create_task(data=invalid_data, user=test_user)

        mock_logger.assert_called_once_with(f"Failed to create task for user ID {test_user.id}: Database error")
        mock_create_task.assert_called_once()


@pytest.mark.django_db
def test_update_task_not_found(task_service, test_user):
    """
    Test exception handling when updating a non-existent task.
    """
    with patch("tasks.service.TaskService.get_task_details",
               side_effect=TaskNotFoundException(999)) as mock_get_details:
        with pytest.raises(TaskNotFoundException):
            task_service.update_task(task_id=999, data={"title": "Updated Task"}, user=test_user)

        mock_get_details.assert_called_once_with(999, test_user)


@pytest.mark.django_db
def test_update_task_unauthorized(task_service, test_user, sample_task, another_user):
    """
    Test exception handling when updating a task not owned by the user.
    """
    sample_task.owner = another_user
    sample_task.save()

    with patch("tasks.service.logger.error") as mock_logger:
        with pytest.raises(TaskUnauthorizedAccessException):
            task_service.update_task(task_id=sample_task.id, data={"title": "Updated Task"}, user=test_user)

        mock_logger.assert_called_once_with(
            f"Unauthorized access to task ID {sample_task.id} by user ID {test_user.id}."
        )


@pytest.mark.django_db
def test_update_task_general_exception(task_service, sample_task, test_user):
    """
    Test general exception handling during task update.
    """
    with (patch("tasks.service.TaskRepository.update_task",
                side_effect=Exception("Unexpected error")) as mock_update_task,
          patch("tasks.service.logger.error") as mock_logger):
        with pytest.raises(Exception, match="Unexpected error"):
            task_service.update_task(task_id=sample_task.id, data={"title": "Updated Task"}, user=test_user)

        mock_logger.assert_called_once_with(
            f"Failed to update task ID {sample_task.id} for user ID {test_user.id}: Unexpected error"
        )
        mock_update_task.assert_called_once()
