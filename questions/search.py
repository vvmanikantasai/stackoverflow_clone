import logging
from functools import lru_cache

from django.conf import settings

try:
    from elasticsearch import ApiError, ConnectionError, Elasticsearch
except ImportError:  # Allows management commands to explain a missing dependency.
    ApiError = ConnectionError = Elasticsearch = None


logger = logging.getLogger(__name__)

QUESTION_INDEX_MAPPINGS = {
    'properties': {
        'title': {'type': 'text'},
        'content': {'type': 'text'},
        'tags': {'type': 'keyword'},
        'created_at': {'type': 'date'},
        'is_deleted': {'type': 'boolean'},
    },
}
_index_is_ready = False


@lru_cache(maxsize=1)
def get_search_client():
    if not settings.ELASTICSEARCH_URL or Elasticsearch is None:
        return None

    options = {
        'request_timeout': 3,
    }
    if settings.ELASTICSEARCH_API_KEY:
        options['api_key'] = settings.ELASTICSEARCH_API_KEY
    elif settings.ELASTICSEARCH_USERNAME:
        options['basic_auth'] = (
            settings.ELASTICSEARCH_USERNAME,
            settings.ELASTICSEARCH_PASSWORD,
        )

    return Elasticsearch(settings.ELASTICSEARCH_URL, **options)


def ensure_search_index(client):
    global _index_is_ready

    if _index_is_ready:
        return True

    try:
        if not client.indices.exists(index=settings.ELASTICSEARCH_INDEX):
            client.indices.create(
                index=settings.ELASTICSEARCH_INDEX,
                mappings=QUESTION_INDEX_MAPPINGS,
            )
        _index_is_ready = True
        return True
    except (ApiError, ConnectionError) as error:
        logger.warning('Could not prepare the search index: %s', error)
        return False


def question_document(question):
    return {
        'title': question.title,
        'content': question.content,
        'tags': [tag.name.lower() for tag in question.tags.all()],
        'created_at': question.created_at,
        'is_deleted': question.is_deleted,
    }


def index_question(question):
    client = get_search_client()
    if client is None or not ensure_search_index(client):
        return False

    try:
        client.index(
            index=settings.ELASTICSEARCH_INDEX,
            id=question.pk,
            document=question_document(question),
        )
        return True
    except (ApiError, ConnectionError) as error:
        logger.warning('Could not index question %s: %s', question.pk, error)
        return False


def remove_question(question_id):
    client = get_search_client()
    if client is None:
        return False

    try:
        client.delete(
            index=settings.ELASTICSEARCH_INDEX,
            id=question_id,
        )
        return True
    except (ApiError, ConnectionError) as error:
        if getattr(error, 'status_code', None) == 404:
            return True
        logger.warning('Could not remove question %s from search: %s', question_id, error)
        return False


def search_questions(text, tag_filters, page_number, page_size):
    client = get_search_client()
    if client is None:
        return None

    must = []
    if text:
        must.append({
            'multi_match': {
                'query': text,
                'fields': ['title^3', 'content'],
                'type': 'best_fields',
                'fuzziness': 'AUTO',
                'prefix_length': 1,
            },
        })

    filters = [{'term': {'is_deleted': False}}]
    filters.extend({'term': {'tags': tag}} for tag in tag_filters)

    query = {'bool': {'must': must, 'filter': filters}}
    offset = (page_number - 1) * page_size

    try:
        response = client.search(
            index=settings.ELASTICSEARCH_INDEX,
            query=query,
            from_=offset,
            size=page_size,
            sort=['_score', {'created_at': 'desc'}],
            track_total_hits=True,
        )
    except (ApiError, ConnectionError) as error:
        logger.warning('Elasticsearch search failed: %s', error)
        return None

    hits = response['hits']
    question_ids = [int(hit['_id']) for hit in hits['hits']]
    total = hits['total']['value']
    return question_ids, total
