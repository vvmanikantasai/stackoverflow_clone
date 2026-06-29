from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from accounts.models import Profile, ReputationHistory
from answers.models import Answer
from questions.models import Question

from .models import Vote


QUESTION_UPVOTE_POINTS = 5
QUESTION_DOWNVOTE_POINTS = -2
ANSWER_UPVOTE_POINTS = 10
ANSWER_DOWNVOTE_POINTS = -2


def get_vote_target(content_type, object_id):
    if content_type == 'question':
        target = get_object_or_404(Question, pk=object_id)
        target_type = ContentType.objects.get_for_model(Question)
        return target, target_type

    if content_type == 'answer':
        target = get_object_or_404(Answer, pk=object_id)
        target_type = ContentType.objects.get_for_model(Answer)
        return target, target_type

    return None, None


def apply_reputation(user, target_obj, vote_value, is_removal=False):
    if isinstance(target_obj, Question):
        if vote_value == 1:
            points = QUESTION_UPVOTE_POINTS
            action = 'question_upvote'
            description = f'Question upvoted: {target_obj.title}'
        else:
            points = QUESTION_DOWNVOTE_POINTS
            action = 'question_downvote'
            description = f'Question downvoted: {target_obj.title}'

    elif isinstance(target_obj, Answer):
        if vote_value == 1:
            points = ANSWER_UPVOTE_POINTS
            action = 'answer_upvote'
            description = 'Answer upvoted'
        else:
            points = ANSWER_DOWNVOTE_POINTS
            action = 'answer_downvote'
            description = 'Answer downvoted'

    else:
        return

    if is_removal:
        points = -points
    elif isinstance(target_obj, Question):
        ReputationHistory.objects.create(
            user=user,
            action=action,
            points=points,
            description=description,
            question=target_obj,
        )
    else:
        ReputationHistory.objects.create(
            user=user,
            action=action,
            points=points,
            description=description,
            answer=target_obj,
        )

    profile = Profile.objects.select_for_update().get(user=user)
    profile.reputation = max(0, profile.reputation + points)
    profile.save(update_fields=['reputation'])


@login_required
@require_POST
@transaction.atomic
def vote_view(request, content_type, object_id, value):
    value = int(value)
    if value not in [1, -1]:
        return JsonResponse({'error': 'Invalid vote'}, status=400)

    target, target_type = get_vote_target(content_type, object_id)
    if not target:
        return JsonResponse({'error': 'Invalid content type'}, status=400)

    if target.author == request.user:
        error = f'Cannot vote on your own {content_type}'
        return JsonResponse({'error': error, 'vote_count': target.vote_count})

    target = type(target).objects.select_for_update().get(pk=target.pk)

    existing_vote = Vote.objects.filter(
        user=request.user,
        content_type=target_type,
        object_id=object_id,
    ).first()

    if existing_vote:
        if existing_vote.value == value:
            apply_reputation(
                target.author,
                target,
                existing_vote.value,
                is_removal=True,
            )
            existing_vote.delete()
            target.vote_count -= value
            target.save(update_fields=['vote_count'])
            return JsonResponse({
                'vote_count': target.vote_count,
                'user_vote': None,
            })
        old_value = existing_vote.value
        apply_reputation(target.author, target, old_value, is_removal=True)
        apply_reputation(target.author, target, value)

        target.vote_count = target.vote_count - old_value + value
        target.save(update_fields=['vote_count'])

        existing_vote.value = value
        existing_vote.save(update_fields=['value'])
        return JsonResponse({
            'vote_count': target.vote_count,
            'user_vote': value,
        })

    Vote.objects.create(
        user=request.user,
        content_type=target_type,
        object_id=object_id,
        value=value,
    )
    apply_reputation(target.author, target, value)
    target.vote_count += value
    target.save(update_fields=['vote_count'])

    return JsonResponse({
        'vote_count': target.vote_count,
        'user_vote': value,
    })
