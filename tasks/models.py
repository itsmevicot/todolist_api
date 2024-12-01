from django.db import models

from tasks.enum import TaskStatus


class Task(models.Model):
    owner = models.ForeignKey("users.User", on_delete=models.PROTECT, related_name="tasks")
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=12, choices=TaskStatus.choices(), default=TaskStatus.CREATED.value)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"

    def __str__(self):
        return self.title

    def delete(self, hard_delete=False, *args, **kwargs):
        """
        Overwrite the delete method to implement soft delete.
        """
        if hard_delete:
            super().delete(*args, **kwargs)
        else:
            self.active = False
            self.save()
