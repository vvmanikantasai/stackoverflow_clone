from django.db import models
from django.contrib.auth.models import User


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_tags',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tags'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def usage_count(self):
        return self.questions.count()
