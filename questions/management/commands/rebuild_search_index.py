from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from questions.models import Question
from questions.search import (
    QUESTION_INDEX_MAPPINGS,
    get_search_client,
    question_document,
)


class Command(BaseCommand):
    help = 'Recreate the Elasticsearch question index.'

    def handle(self, *args, **options):
        client = get_search_client()
        if client is None:
            raise CommandError(
                'Set ELASTICSEARCH_URL and install the elasticsearch package first.',
            )

        try:
            from elasticsearch.helpers import bulk

            if client.indices.exists(index=settings.ELASTICSEARCH_INDEX):
                client.indices.delete(index=settings.ELASTICSEARCH_INDEX)

            client.indices.create(
                index=settings.ELASTICSEARCH_INDEX,
                mappings=QUESTION_INDEX_MAPPINGS,
            )

            questions = Question.objects.prefetch_related('tags').iterator(
                chunk_size=500,
            )
            actions = (
                {
                    '_index': settings.ELASTICSEARCH_INDEX,
                    '_id': question.pk,
                    '_source': question_document(question),
                }
                for question in questions
            )
            indexed, _ = bulk(client, actions, refresh='wait_for')
        except Exception as error:
            raise CommandError(f'Could not rebuild the search index: {error}') from error

        self.stdout.write(
            self.style.SUCCESS(f'Indexed {indexed} questions.'),
        )
