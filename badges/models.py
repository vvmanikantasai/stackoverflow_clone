from django.db import models
from django.contrib.auth.models import User


class Badge(models.Model):
    TIER_CHOICES = [('bronze', 'Bronze'), ('silver', 'Silver'), ('gold', 'Gold')]
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    tier = models.CharField(max_length=10, choices=TIER_CHOICES)
    icon = models.CharField(max_length=50, default='', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'badges'
        ordering = ['tier', 'name']

    def __str__(self):
        return f'{self.tier.title()} - {self.name}'


class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_badges'
        unique_together = ['user', 'badge']

    def __str__(self):
        return f'{self.user.username} - {self.badge.name}'
