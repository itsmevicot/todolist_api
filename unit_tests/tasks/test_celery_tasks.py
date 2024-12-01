from datetime import datetime, timezone

import pytest
from unittest.mock import patch, MagicMock
from tasks.tasks import send_expiry_reminder, mark_expired_tasks
from tasks.enum import TaskStatus


@pytest.mark.django_db
@patch("tasks.tasks.TaskRepository.get_tasks_expiring_soon")
@patch("tasks.tasks.send_mail")
@patch("tasks.tasks.settings.DEFAULT_FROM_EMAIL", "test@example.com")
@patch("tasks.tasks.localtime")
def test_send_expiry_reminder(mock_localtime, mock_send_mail, mock_get_tasks_expiring_soon):
    mock_task = MagicMock()
    mock_task.title = "Mock Task"
    mock_task.expires_at = datetime(2024, 12, 1, 15, 0, tzinfo=timezone.utc)
    mock_task.owner.email = "test@example.com"

    mock_get_tasks_expiring_soon.return_value = [mock_task]

    mock_localtime.return_value = datetime(2024, 12, 1, 15, 0)

    send_expiry_reminder()

    mock_get_tasks_expiring_soon.assert_called_once_with(hours=3)
    mock_send_mail.assert_called_once_with(
        subject="Task Expiry Reminder",
        message='Your task "Mock Task" is set to expire on December 01, 2024, at 03:00 PM. ⏰',
        from_email="test@example.com",
        recipient_list=[mock_task.owner.email],
    )


@pytest.mark.django_db
@patch("tasks.tasks.TaskRepository.get_tasks_expiring_soon")
@patch("tasks.tasks.logger")
def test_send_expiry_reminder_logs_error(mock_logger, mock_get_tasks_expiring_soon):
    mock_task = MagicMock()
    mock_task.title = "Mock Task"
    mock_task.expires_at = datetime(2024, 12, 1, 15, 0, tzinfo=timezone.utc)
    mock_task.owner.email = "test@example.com"

    mock_get_tasks_expiring_soon.return_value = [mock_task]

    with patch("tasks.tasks.send_mail", side_effect=Exception("Email failure")):
        send_expiry_reminder()

    mock_logger.error.assert_called_with(
        f"Failed to send email for task ID {mock_task.id}: Email failure"
    )


@pytest.mark.django_db
@patch("tasks.tasks.TaskRepository.get_expired_tasks")
@patch("tasks.tasks.TaskRepository.update_task_status")
def test_mark_expired_tasks(mock_update_task_status, mock_get_expired_tasks):
    mock_task = MagicMock()
    mock_task.id = 1

    mock_get_expired_tasks.return_value = [mock_task]

    mark_expired_tasks()

    mock_get_expired_tasks.assert_called_once()
    mock_update_task_status.assert_called_once_with(mock_task, TaskStatus.EXPIRED.value)


@pytest.mark.django_db
@patch("tasks.tasks.TaskRepository.get_expired_tasks")
@patch("tasks.tasks.logger")
def test_mark_expired_tasks_logs_error(mock_logger, mock_get_expired_tasks):
    mock_task = MagicMock()
    mock_task.id = 1

    mock_get_expired_tasks.return_value = [mock_task]

    with patch("tasks.tasks.TaskRepository.update_task_status", side_effect=Exception("Update failure")):
        mark_expired_tasks()

    mock_logger.error.assert_called_with(f"Failed to mark task ID {mock_task.id} as expired: Update failure")


@pytest.mark.django_db
@patch("tasks.tasks.TaskRepository.get_tasks_expiring_soon",
       side_effect=Exception("Outer exception in send_expiry_reminder"))
@patch("tasks.tasks.logger")
def test_send_expiry_reminder_outer_exception(mock_logger, mock_get_tasks_expiring_soon):
    """
    Test handling of an outer exception in send_expiry_reminder.
    """
    send_expiry_reminder()

    mock_logger.error.assert_called_with(
        "An error occurred in send_expiry_reminder: Outer exception in send_expiry_reminder"
    )


@pytest.mark.django_db
@patch("tasks.tasks.TaskRepository.get_expired_tasks", side_effect=Exception("Outer exception in mark_expired_tasks"))
@patch("tasks.tasks.logger")
def test_mark_expired_tasks_outer_exception(mock_logger, mock_get_expired_tasks):
    """
    Test handling of an outer exception in mark_expired_tasks.
    """
    mark_expired_tasks()

    mock_logger.error.assert_called_with(
        "An error occurred in mark_expired_tasks: Outer exception in mark_expired_tasks"
    )
