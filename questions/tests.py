from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from answers.models import Answer
from tags.models import Tag

from .models import Question


class SearchViewTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            'search-author',
            password='Pass12345',
        )
        self.answerer = User.objects.create_user(
            'search-answerer',
            password='Pass12345',
        )
        self.question = Question.objects.create(
            title='How to make Django search results better?',
            content='I need help improving a Django search result page.',
            author=self.author,
            view_count=12,
            answer_count=1,
        )
        self.django_tag = Tag.objects.create(name='django', slug='django')
        self.question.tags.add(self.django_tag)
        Answer.objects.create(
            question=self.question,
            author=self.answerer,
            content='Use a clear hierarchy and useful result metadata.',
            is_accepted=True,
        )

    def test_search_results_show_complete_question_metadata(self):
        response = self.client.get(reverse('search'), {'q': 'Django'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.question.title)
        self.assertContains(response, '12')
        self.assertContains(response, 'Solved')
        self.assertContains(response, self.author.username)
        self.assertContains(response, 'search-results-hero')

    def test_empty_search_has_helpful_empty_state(self):
        response = self.client.get(reverse('search'), {'q': 'no-match-here'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No questions matched')
        self.assertContains(response, 'Clear search')

    def test_bracket_syntax_searches_an_exact_tag(self):
        other_question = Question.objects.create(
            title='A Django word without the requested tag',
            content='This mentions Django but has no matching tag attached.',
            author=self.author,
        )

        response = self.client.get(reverse('search'), {'q': '[django]'})

        self.assertContains(response, self.question.title)
        self.assertNotContains(response, other_question.title)
        self.assertContains(response, 'Filtering by')

    def test_normal_search_does_not_match_a_tag_name_by_itself(self):
        tag_only_question = Question.objects.create(
            title='Understanding template context processors',
            content='How can context values be made available on every page?',
            author=self.author,
        )
        tag_only_question.tags.add(self.django_tag)

        response = self.client.get(reverse('search'), {'q': 'django'})

        self.assertContains(response, self.question.title)
        self.assertNotContains(response, tag_only_question.title)

    def test_tag_filter_can_be_combined_with_search_words(self):
        response = self.client.get(
            reverse('search'),
            {'q': '[django] results'},
        )

        self.assertContains(response, self.question.title)
        self.assertContains(response, '[django] forms')


class AskQuestionViewTests(TestCase):
    def test_title_field_uses_full_size_form_styling(self):
        user = User.objects.create_user('questioner', password='Pass12345')
        self.client.force_login(user)

        response = self.client.get(reverse('ask_question'))

        self.assertContains(
            response,
            'class="form-control question-title-input"',
        )
