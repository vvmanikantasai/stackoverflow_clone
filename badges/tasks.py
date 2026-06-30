from celery import shared_task
from django.contrib.auth.models import User

from .utils import check_and_award_badges


@shared_task
def award_badges(user_id):
    try:
        user = User.objects.select_related('profile').get(pk=user_id)
    except User.DoesNotExist:
        return []

    awarded = check_and_award_badges(user)
    return [badge.name for badge in awarded]
