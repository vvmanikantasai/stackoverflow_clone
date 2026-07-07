from django.test import SimpleTestCase
from django.urls import resolve, reverse

from .views import home_view, questions_view


class QuestionRouteTests(SimpleTestCase):
    def test_home_has_its_own_route(self):
        self.assertEqual(reverse('home'), '/')
        self.assertEqual(resolve('/').func, home_view)

    def test_questions_have_their_own_route(self):
        self.assertEqual(reverse('questions'), '/questions/')
        self.assertEqual(resolve('/questions/').func, questions_view)
