from django.db import models
from django.conf import settings
from django.db.models import Count

class Message(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='sent_messages'
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='received_messages'
    )
    subject = models.CharField(max_length=255)
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    priority = models.CharField(
        max_length=50, 
        blank=True,
        null=False,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')]
    )
    read = models.BooleanField(default=False)

    def __str__(self):
        return self.subject

    @classmethod
    def get_unread_count(cls, user):
        return cls.objects.filter(recipient=user, read=False).count()
