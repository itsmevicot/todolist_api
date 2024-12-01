import pytest
from rest_framework import status
from tasks.models import Task
from tasks.enum import TaskStatus


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
