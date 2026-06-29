from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.templatetags.static import static


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png', blank=True)
    bio = models.TextField(max_length=500, blank=True)
    reputation = models.IntegerField(default=0)
    joined_date = models.DateTimeField(auto_now_add=True)
    website = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, blank=True)
    password_reset_token = models.CharField(max_length=100, blank=True)
    password_reset_expires = models.DateTimeField(null=True, blank=True)
    dark_mode = models.BooleanField(default=False)

    class Meta:
        db_table = 'profiles'

    def __str__(self):
        return f'{self.user.username} Profile'

    @property
    def questions_count(self):
        return self.user.questions.count()

    @property
    def answers_count(self):
        return self.user.answers.count()

    @property
    def badges_count(self):
        return self.user.userbadge_set.count()

    def get_avatar_url(self):
        if self.avatar and hasattr(self.avatar, 'url'):
            try:
                if self.avatar.name and not self.avatar.storage.exists(self.avatar.name):
                    return static('images/default_avatar.svg')
                return self.avatar.url
            except Exception:
                pass
        return static('images/default_avatar.svg')


class ReputationHistory(models.Model):
    ACTION_CHOICES = [
        ('question_upvote', 'Question Upvote (+5)'),
        ('question_downvote', 'Question Downvote (-2)'),
        ('answer_upvote', 'Answer Upvote (+10)'),
        ('answer_downvote', 'Answer Downvote (-2)'),
        ('answer_accepted', 'Answer Accepted (+15)'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reputation_history')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    points = models.IntegerField()
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    question = models.ForeignKey('questions.Question', on_delete=models.SET_NULL, null=True, blank=True)
    answer = models.ForeignKey('answers.Answer', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'reputation_history'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username}: {self.action} ({self.points:+d})'


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_relationships')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower_relationships')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'follows'
        unique_together = ['follower', 'following']

    def __str__(self):
        return f'{self.follower.username} follows {self.following.username}'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
