from django.urls import reverse

from .models import Badge, UserBadge
from notifications.utils import create_notification


def user_qualifies_for_badge(
    badge_name,
    question_count,
    answer_count,
    reputation,
):
    if badge_name == 'First Question':
        return question_count >= 1
    if badge_name == 'First Answer':
        return answer_count >= 1
    if badge_name == '100 Reputation':
        return reputation >= 100
    if badge_name == '1000 Reputation':
        return reputation >= 1000
    if badge_name == 'Prolific Questioner':
        return question_count >= 10
    if badge_name == 'Top Answerer':
        return answer_count >= 10

    return False


def check_and_award_badges(user):
    badge_names = [
        'First Question',
        'First Answer',
        '100 Reputation',
        '1000 Reputation',
        'Prolific Questioner',
        'Top Answerer',
    ]
    question_count = user.questions.filter(is_deleted=False).count()
    answer_count = user.answers.filter(is_deleted=False).count()
    reputation = user.profile.reputation

    for badge_name in badge_names:
        badge = Badge.objects.filter(name=badge_name).first()
        if not badge:
            continue

        already_awarded = UserBadge.objects.filter(
            user=user,
            badge=badge,
        ).exists()
        if already_awarded:
            continue

        qualifies = user_qualifies_for_badge(
            badge_name,
            question_count,
            answer_count,
            reputation,
        )
        if not qualifies:
            continue

        UserBadge.objects.create(user=user, badge=badge)
        create_notification(
            recipient=user,
            sender=None,
            notification_type='badge',
            message=f'You earned the "{badge_name}" badge!',
            url=reverse('badges'),
        )
