from celery import shared_task
from django.contrib.auth.models import User

from notifications.services import create_notification

from .utils import check_and_award_badges


@shared_task
def award_badges(user_id):
    try:
        user = User.objects.select_related('profile').get(pk=user_id)
    except User.DoesNotExist:
        return []

    awarded = check_and_award_badges(user)
    for badge in awarded:
        create_notification(
            recipient=user,
            actor=None,
            message=f'You earned the {badge.name} badge.',
            target_url='/badges/',
        )
    return [badge.name for badge in awarded]
