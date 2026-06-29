from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Vote(models.Model):
    VOTE_CHOICES = [(1, 'Upvote'), (-1, 'Downvote')]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    value = models.SmallIntegerField(choices=VOTE_CHOICES)
    # Votes can point to questions, answers, or comments.
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'votes'
        unique_together = ['user', 'content_type', 'object_id']

    def __str__(self):
        return f'{self.user.username} voted {self.value} on {self.content_object}'
