from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from badges.models import Badge, UserBadge
from questions.models import Question


class ProfileViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('developer', password='Pass12345')
        self.user.profile.github_url = 'https://github.com/developer'
        self.user.profile.save()
        self.question = Question.objects.create(
            title='Profile question',
            content='Question shown in the profile activity.',
            author=self.user,
        )
        badge = Badge.objects.create(
            name='Profile Badge',
            description='A test badge',
            tier='bronze',
        )
        UserBadge.objects.create(user=self.user, badge=badge)

    def test_profile_stats_open_real_sections(self):
        for tab, expected in (
            ('questions', b'Profile question'),
            ('badges', b'Profile Badge'),
            ('reputation', b'Reputation activity'),
        ):
            response = self.client.get(
                reverse('profile', kwargs={'username': self.user.username}),
                {'tab': tab},
            )
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, expected)

    def test_profile_renders_github_link(self):
        response = self.client.get(
            reverse('profile', kwargs={'username': self.user.username})
        )
        self.assertContains(response, 'https://github.com/developer')

    def test_profile_renders_polished_about_summary(self):
        response = self.client.get(
            reverse('profile', kwargs={'username': self.user.username})
        )

        self.assertContains(response, 'About developer')
        self.assertContains(response, 'Reputation earned')
        self.assertContains(response, 'profile-about-contributions')

    def test_edit_profile_calls_avatar_a_profile_image(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('edit_profile'))

        self.assertContains(response, 'Profile image')
        self.assertNotContains(response, '>Avatar<')
