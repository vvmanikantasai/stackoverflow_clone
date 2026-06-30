import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db import DatabaseError

from accounts.models import Profile


logger = logging.getLogger(__name__)


def notification_summary(request):
    if not request.user.is_authenticated:
        return {}

    try:
        request.user.profile
    except ObjectDoesNotExist:
        Profile.objects.get_or_create(user=request.user)

    try:
        unread = request.user.notifications.filter(is_read=False)
        return {
            'unread_notification_count': unread.count(),
            'recent_notifications': request.user.notifications.select_related('actor')[:6],
        }
    except DatabaseError:
        logger.exception('Notifications are unavailable for user %s', request.user.pk)
        return {
            'unread_notification_count': 0,
            'recent_notifications': [],
        }
