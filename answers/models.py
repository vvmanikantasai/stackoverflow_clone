from django.db import models
from django.contrib.auth.models import User
from questions.models import Question


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers')
    content = models.TextField()
    vote_count = models.IntegerField(default=0)
    is_accepted = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'answers'
        ordering = ['-is_accepted', '-vote_count', 'created_at']

    def __str__(self):
        return f'Answer by {self.author.username} on {self.question.title}'
