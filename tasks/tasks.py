import logging
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from tasks.enum import TaskStatus
from tasks.repository import TaskRepository

logger = logging.getLogger(__name__)


@shared_task
def send_expiry_reminder():
    """
    Task to send reminders for tasks expiring soon.
    """
    try:
        logger.info("Starting task: send_expiry_reminder")
        tasks_to_remind = TaskRepository.get_tasks_expiring_soon(hours=3)
        logger.info(f"Found {len(tasks_to_remind)} tasks expiring soon.")

        for task in tasks_to_remind:
            try:
                send_mail(
                    subject="Task Expiry Reminder",
                    message=f"Your task '{task.title}' is set to expire at {task.expires_at}.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[task.owner.email],
                )
                logger.info(f"Reminder sent for task ID {task.id} to {task.owner.email}")
            except Exception as e:
                logger.error(f"Failed to send email for task ID {task.id}: {e}")

    except Exception as e:
        logger.error(f"An error occurred in send_expiry_reminder: {e}")


@shared_task
def mark_expired_tasks():
    """
    Task to mark tasks as expired.
    """
    try:
        logger.info("Starting task: mark_expired_tasks")
        expired_tasks = TaskRepository.get_expired_tasks()
        logger.info(f"Found {len(expired_tasks)} tasks to mark as expired.")

        for task in expired_tasks:
            try:
                TaskRepository.update_task_status(task, TaskStatus.EXPIRED.value)
                logger.info(f"Task ID {task.id} marked as expired.")
            except Exception as e:
                logger.error(f"Failed to mark task ID {task.id} as expired: {e}")

    except Exception as e:
        logger.error(f"An error occurred in mark_expired_tasks: {e}")
