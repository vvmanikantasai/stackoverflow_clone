from django.contrib import admin
from .models import Answer


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['author', 'question', 'vote_count', 'is_accepted', 'is_deleted', 'created_at']
    list_filter = ['is_accepted', 'is_deleted']
    search_fields = ['content', 'author__username']
