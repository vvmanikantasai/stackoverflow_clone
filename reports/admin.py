from django.contrib import admin
from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['reporter', 'reason', 'status', 'created_at']
    list_filter = ['reason', 'status']
    actions = ['mark_resolved', 'mark_dismissed']

    def mark_resolved(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='resolved', resolved_by=request.user, resolved_at=timezone.now())
    mark_resolved.short_description = 'Mark selected as resolved'

    def mark_dismissed(self, request, queryset):
        queryset.update(status='dismissed')
    mark_dismissed.short_description = 'Dismiss selected reports'
