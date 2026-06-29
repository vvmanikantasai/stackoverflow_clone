from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from questions.models import Question


class VoteViewTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user('author', password='Pass12345')
        self.voter = User.objects.create_user('voter', password='Pass12345')
        self.question = Question.objects.create(
            title='A test question',
            content='A complete test question body.',
            author=self.author,
        )
        self.client.force_login(self.voter)

    def test_question_can_be_downvoted(self):
        response = self.client.post(
            reverse(
                'vote',
                kwargs={
                    'content_type': 'question',
                    'object_id': self.question.pk,
                    'value': -1,
                },
            ),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        self.assertEqual(response.status_code, 200)
        self.question.refresh_from_db()
        self.assertEqual(self.question.vote_count, -1)
        self.assertEqual(response.json()['user_vote'], -1)

    def test_vote_endpoint_rejects_get(self):
        response = self.client.get(
            reverse(
                'vote',
                kwargs={
                    'content_type': 'question',
                    'object_id': self.question.pk,
                    'value': 1,
                },
            )
        )
        self.assertEqual(response.status_code, 405)
