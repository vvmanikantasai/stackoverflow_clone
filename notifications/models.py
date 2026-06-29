from django.db import models
from django.contrib.auth.models import User


class Notification(models.Model):
    TYPE_CHOICES = [
        ('new_answer', 'New Answer'),
        ('new_comment', 'New Comment'),
        ('mention', 'Mention'),
        ('answer_accepted', 'Answer Accepted'),
        ('upvote', 'Upvote'),
        ('badge', 'Badge Awarded'),
    ]
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_notifications',
    )
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    message = models.TextField()
    url = models.CharField(max_length=500, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f'Notification for {self.recipient.username}: {self.notification_type}'
