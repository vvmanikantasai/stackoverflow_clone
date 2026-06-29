def notification_summary(request):
    if not request.user.is_authenticated:
        return {}

    unread = request.user.notifications.filter(is_read=False)
    return {
        'unread_notification_count': unread.count(),
        'recent_notifications': request.user.notifications.select_related('actor')[:6],
    }
