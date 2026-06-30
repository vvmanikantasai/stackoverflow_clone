from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver

from .models import Question
from .search import index_question, remove_question


@receiver(post_save, sender=Question)
def update_question_index(sender, instance, **kwargs):
    index_question(instance)


@receiver(m2m_changed, sender=Question.tags.through)
def update_question_tags_in_index(
    sender,
    instance,
    action,
    reverse,
    pk_set,
    **kwargs,
):
    if action not in {'post_add', 'post_remove', 'post_clear'}:
        return

    if reverse:
        for question in Question.objects.filter(pk__in=pk_set or []):
            index_question(question)
    else:
        index_question(instance)


@receiver(post_delete, sender=Question)
def delete_question_from_index(sender, instance, **kwargs):
    remove_question(instance.pk)
