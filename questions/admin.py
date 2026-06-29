from django.contrib import admin
from .models import Question, QuestionImage, Bookmark


class QuestionImageInline(admin.TabularInline):
    model = QuestionImage
    extra = 0


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'vote_count', 'answer_count', 'view_count', 'created_at', 'is_deleted']
    list_filter = ['is_deleted', 'is_closed', 'created_at']
    search_fields = ['title', 'content', 'author__username']
    inlines = [QuestionImageInline]
    readonly_fields = ['vote_count', 'view_count', 'answer_count']


admin.site.register(Bookmark)
