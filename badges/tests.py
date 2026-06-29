from django.contrib.auth.models import User
from django.test import TestCase

from notifications.models import Notification
from questions.models import Question

from .models import Badge, UserBadge
from .tasks import award_badges


class BadgeTaskTests(TestCase):
    def test_task_awards_badge_and_creates_notification(self):
        user = User.objects.create_user('asker', password='Pass12345')
        Question.objects.create(
            title='First question',
            content='A complete first question body.',
            author=user,
        )
        Badge.objects.create(
            name='First Question',
            description='Asked a first question',
            tier='bronze',
        )

        result = award_badges.run(user.pk)

        self.assertEqual(result, ['First Question'])
        self.assertTrue(
            UserBadge.objects.filter(user=user, badge__name='First Question').exists()
        )
        self.assertTrue(
            Notification.objects.filter(
                recipient=user,
                message__contains='First Question',
            ).exists()
        )
