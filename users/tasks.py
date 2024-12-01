from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task
def send_welcome_email(user_email, name):
    """
    Task to send a welcome email to a newly created user.
    """
    send_mail(
        subject="Welcome to Turivius To Do List",
        message=f"Hello {name},"
                f"\n\nThank you for signing up! We're excited to have you on board.\n\nBest regards,\nThe Team",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
    )
