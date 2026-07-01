from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from tags.models import Tag

class Question(models.Model):
    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=350, unique=True, blank=True)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions')
    tags = models.ManyToManyField(Tag, related_name='questions', blank=True)
    vote_count = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)
    answer_count = models.IntegerField(default=0)
    is_closed = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'questions'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)[:300]
            slug = base_slug
            n = 1
            while Question.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('question_detail', kwargs={'slug': self.slug})

    @property
    def has_accepted_answer(self):
        return self.answers.filter(is_accepted=True).exists()

    @property
    def accepted_answer(self):
        return self.answers.filter(is_accepted=True).first()

class QuestionImage(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='question_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'question_images'

class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bookmarks'
        unique_together = ['user', 'question']

    def __str__(self):
        return f'{self.user.username} bookmarked {self.question.title}'

class RecentlyViewed(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recently_viewed')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='viewed_by')
    viewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'recently_viewed'
        unique_together = ['user', 'question']
        ordering = ['-viewed_at']
