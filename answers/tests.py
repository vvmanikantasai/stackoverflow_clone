from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import ReputationHistory
from notifications.models import Notification
from questions.models import Question

from .models import Answer
from .views import ACCEPTED_ANSWER_POINTS, ACCEPTING_ANSWER_POINTS, SELF_ACCEPT_WAIT


class AcceptAnswerViewTests(TestCase):
    def setUp(self):
        self.question_author = User.objects.create_user(
            'question-author',
            password='Pass12345',
        )
        self.first_author = User.objects.create_user(
            'first-answerer',
            password='Pass12345',
        )
        self.second_author = User.objects.create_user(
            'second-answerer',
            password='Pass12345',
        )
        self.question = Question.objects.create(
            title='How do accepted answers work?',
            content='I need a complete example.',
            author=self.question_author,
        )
        self.first_answer = Answer.objects.create(
            question=self.question,
            author=self.first_author,
            content='The first answer.',
        )
        self.second_answer = Answer.objects.create(
            question=self.question,
            author=self.second_author,
            content='The second answer.',
        )
        self.client.force_login(self.question_author)

    def accept(self, answer):
        return self.client.post(reverse('accept_answer', kwargs={'pk': answer.pk}))

    def test_question_author_can_accept_an_answer_and_award_reputation(self):
        response = self.accept(self.first_answer)

        self.assertRedirects(response, self.question.get_absolute_url())
        self.first_answer.refresh_from_db()
        self.first_author.profile.refresh_from_db()
        self.question_author.profile.refresh_from_db()
        self.assertTrue(self.first_answer.is_accepted)
        self.assertEqual(
            self.first_author.profile.reputation,
            ACCEPTED_ANSWER_POINTS,
        )
        self.assertEqual(
            self.question_author.profile.reputation,
            ACCEPTING_ANSWER_POINTS,
        )
        self.assertTrue(
            ReputationHistory.objects.filter(
                user=self.first_author,
                answer=self.first_answer,
                points=ACCEPTED_ANSWER_POINTS,
            ).exists()
        )
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.first_author,
                actor=self.question_author,
            ).exists()
        )

    def test_switching_acceptance_transfers_the_reputation_award(self):
        self.accept(self.first_answer)
        self.accept(self.second_answer)

        self.first_answer.refresh_from_db()
        self.second_answer.refresh_from_db()
        self.first_author.profile.refresh_from_db()
        self.second_author.profile.refresh_from_db()
        self.question_author.profile.refresh_from_db()
        self.assertFalse(self.first_answer.is_accepted)
        self.assertTrue(self.second_answer.is_accepted)
        self.assertEqual(self.first_author.profile.reputation, 0)
        self.assertEqual(
            self.second_author.profile.reputation,
            ACCEPTED_ANSWER_POINTS,
        )
        self.assertEqual(
            self.question_author.profile.reputation,
            ACCEPTING_ANSWER_POINTS,
        )
        self.assertEqual(self.question.answers.filter(is_accepted=True).count(), 1)

    def test_non_author_cannot_accept_an_answer(self):
        self.client.force_login(self.first_author)

        response = self.accept(self.second_answer)

        self.assertRedirects(response, self.question.get_absolute_url())
        self.second_answer.refresh_from_db()
        self.second_author.profile.refresh_from_db()
        self.assertFalse(self.second_answer.is_accepted)
        self.assertEqual(self.second_author.profile.reputation, 0)

    def test_accept_endpoint_rejects_get(self):
        response = self.client.get(
            reverse('accept_answer', kwargs={'pk': self.first_answer.pk})
        )

        self.assertEqual(response.status_code, 405)

    def test_question_page_shows_accept_action_only_to_question_author(self):
        response = self.client.get(self.question.get_absolute_url())

        self.assertContains(response, 'Accept this answer', count=2)
        self.assertContains(response, '+15 reputation', count=2)

        self.client.force_login(self.first_author)
        response = self.client.get(self.question.get_absolute_url())
        self.assertNotContains(response, 'Accept this answer')

    def test_question_page_marks_the_accepted_answer(self):
        self.accept(self.first_answer)

        response = self.client.get(self.question.get_absolute_url())

        self.assertContains(response, 'Accepted answer')
        self.assertContains(response, 'Selected by the question author')
        self.assertContains(
            response,
            'class="answer-block accepted-answer"',
            count=1,
        )

    def test_own_answer_cannot_be_accepted_during_first_48_hours(self):
        own_answer = Answer.objects.create(
            question=self.question,
            author=self.question_author,
            content='I found the solution myself.',
        )

        response = self.accept(own_answer)

        self.assertRedirects(response, self.question.get_absolute_url())
        own_answer.refresh_from_db()
        self.question_author.profile.refresh_from_db()
        self.assertFalse(own_answer.is_accepted)
        self.assertEqual(self.question_author.profile.reputation, 0)

        page = self.client.get(self.question.get_absolute_url())
        self.assertContains(page, 'Accept your answer')
        self.assertContains(page, 'Available')
        self.assertContains(page, 'disabled')

    def test_own_answer_can_be_accepted_after_48_hours_without_reputation(self):
        old_created_at = timezone.now() - SELF_ACCEPT_WAIT - timedelta(minutes=1)
        Question.objects.filter(pk=self.question.pk).update(
            created_at=old_created_at
        )
        self.question.refresh_from_db()
        own_answer = Answer.objects.create(
            question=self.question,
            author=self.question_author,
            content='I found the solution myself.',
        )

        response = self.accept(own_answer)

        self.assertRedirects(response, self.question.get_absolute_url())
        own_answer.refresh_from_db()
        self.question_author.profile.refresh_from_db()
        self.assertTrue(own_answer.is_accepted)
        self.assertEqual(self.question_author.profile.reputation, 0)
        self.assertFalse(
            ReputationHistory.objects.filter(
                user=self.question_author,
                answer=own_answer,
            ).exists()
        )

    def test_deleting_accepted_answer_revokes_reputation(self):
        self.accept(self.first_answer)
        self.client.force_login(self.first_author)

        response = self.client.post(
            reverse('delete_answer', kwargs={'pk': self.first_answer.pk})
        )

        self.assertRedirects(response, self.question.get_absolute_url())
        self.first_answer.refresh_from_db()
        self.first_author.profile.refresh_from_db()
        self.question_author.profile.refresh_from_db()
        self.assertTrue(self.first_answer.is_deleted)
        self.assertFalse(self.first_answer.is_accepted)
        self.assertEqual(self.first_author.profile.reputation, 0)
        self.assertEqual(self.question_author.profile.reputation, 0)
