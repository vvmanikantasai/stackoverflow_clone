from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, override_settings
from django.urls import reverse

from answers.models import Answer
from comments.models import Comment
from questions.models import Question

from .models import Notification


@override_settings(SECURE_SSL_REDIRECT=False)
class NotificationTriggerTests(TestCase):
    def setUp(self):
        self.asker = User.objects.create_user(
            username='asker',
            password='test-password',
        )
        self.answerer = User.objects.create_user(
            username='answerer',
            password='test-password',
        )
        self.third_user = User.objects.create_user(
            username='third',
            password='test-password',
        )
        self.question = Question.objects.create(
            title='How do notifications work?',
            content='I want to understand notification systems.',
            author=self.asker,
        )

    def test_new_answer_notifies_question_author(self):
        self.client.force_login(self.answerer)
        self.client.post(
            reverse('post_answer', args=[self.question.pk]),
            {'content': 'This answer is long enough to pass validation.'},
        )

        notification = Notification.objects.get(recipient=self.asker)
        answer = Answer.objects.get(question=self.question)
        self.assertEqual(notification.actor, self.answerer)
        self.assertEqual(notification.kind, Notification.Kind.ANSWER)
        self.assertEqual(
            notification.target_url,
            f'{self.question.get_absolute_url()}#answer-{answer.pk}',
        )

    def test_users_do_not_receive_notifications_for_their_own_actions(self):
        self.client.force_login(self.asker)
        self.client.post(
            reverse('post_answer', args=[self.question.pk]),
            {'content': 'This is my own sufficiently detailed answer.'},
        )
        self.client.post(
            reverse('add_comment', args=['question', self.question.pk]),
            {'content': 'My own comment'},
        )

        self.assertFalse(Notification.objects.filter(recipient=self.asker).exists())

    def test_comment_reply_notifies_parent_and_post_authors_once(self):
        question_type = ContentType.objects.get_for_model(Question)
        parent = Comment.objects.create(
            author=self.answerer,
            content='This is a parent comment.',
            content_type=question_type,
            object_id=self.question.pk,
        )
        self.client.force_login(self.third_user)
        self.client.post(
            reverse('add_comment', args=['question', self.question.pk]),
            {'content': 'This is a useful reply.', 'parent_id': parent.pk},
        )

        self.assertTrue(Notification.objects.filter(
            recipient=self.answerer,
            kind=Notification.Kind.REPLY,
        ).exists())
        self.assertTrue(Notification.objects.filter(
            recipient=self.asker,
            kind=Notification.Kind.COMMENT,
        ).exists())
        self.assertEqual(Notification.objects.count(), 2)

    def test_accepting_answer_notifies_answer_author(self):
        answer = Answer.objects.create(
            question=self.question,
            author=self.answerer,
            content='An answer that can be accepted.',
        )
        self.client.force_login(self.asker)
        self.client.post(reverse('accept_answer', args=[answer.pk]))

        notification = Notification.objects.get(recipient=self.answerer)
        self.assertEqual(notification.kind, Notification.Kind.ACCEPTED)
        self.assertEqual(notification.actor, self.asker)

    def test_follow_notifies_followed_user(self):
        self.client.force_login(self.answerer)
        self.client.post(reverse('toggle_follow', args=[self.asker.username]))

        notification = Notification.objects.get(recipient=self.asker)
        self.assertEqual(notification.kind, Notification.Kind.FOLLOW)
        self.assertEqual(notification.actor, self.answerer)


@override_settings(SECURE_SSL_REDIRECT=False)
class NotificationViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='recipient',
            password='test-password',
        )
        self.other_user = User.objects.create_user(
            username='actor',
            password='test-password',
        )
        self.notification = Notification.objects.create(
            recipient=self.user,
            actor=self.other_user,
            kind=Notification.Kind.FOLLOW,
            message='actor started following you.',
            target_url=reverse('profile', args=[self.other_user.username]),
        )

    def test_notification_pages_require_login(self):
        response = self.client.get(reverse('notifications'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_notification_list_shows_items_and_unread_count(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('notifications'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.notification.message)
        self.assertEqual(response.context['unread_notification_count'], 1)

    def test_open_marks_notification_read_and_redirects(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('open_notification', args=[self.notification.pk]),
        )

        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)
        self.assertIsNotNone(self.notification.read_at)
        self.assertRedirects(
            response,
            reverse('profile', args=[self.other_user.username]),
            fetch_redirect_response=False,
        )

    def test_user_cannot_open_someone_elses_notification(self):
        self.client.force_login(self.other_user)
        response = self.client.get(
            reverse('open_notification', args=[self.notification.pk]),
        )
        self.assertEqual(response.status_code, 404)

    def test_mark_all_read_only_updates_current_user(self):
        other_notification = Notification.objects.create(
            recipient=self.other_user,
            actor=self.user,
            kind=Notification.Kind.FOLLOW,
            message='recipient started following you.',
        )
        self.client.force_login(self.user)
        self.client.post(reverse('mark_all_notifications_read'))

        self.notification.refresh_from_db()
        other_notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)
        self.assertFalse(other_notification.is_read)
