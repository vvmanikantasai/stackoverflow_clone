from django.contrib.auth.models import User
from django.db import models


class Notification(models.Model):
    class Kind(models.TextChoices):
        ANSWER = 'answer', 'New answer'
        COMMENT = 'comment', 'New comment'
        REPLY = 'reply', 'Comment reply'
        ACCEPTED = 'accepted', 'Accepted answer'
        FOLLOW = 'follow', 'New follower'
        BADGE = 'badge', 'Badge awarded'
        UPVOTE = 'upvote', 'New upvote'

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    actor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications_sent',
    )
    kind = models.CharField(max_length=20, choices=Kind.choices)
    message = models.CharField(max_length=255)
    target_url = models.CharField(max_length=500, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(
                fields=['recipient', 'is_read', '-created_at'],
                name='notif_recipient_read_idx',
            ),
        ]

    def __str__(self):
        return f'{self.recipient.username}: {self.message}'
