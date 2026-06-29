from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.models import Profile, ReputationHistory
from badges.tasks import award_badges
from notifications.services import create_notification
from questions.models import Question

from .forms import AnswerForm
from .models import Answer


ACCEPTED_ANSWER_POINTS = 15


def revoke_accepted_answer(answer):
    """Remove an accepted-answer award while the caller holds row locks."""
    answer.is_accepted = False
    answer.save(update_fields=['is_accepted'])

    profile = Profile.objects.select_for_update().get(user=answer.author)
    profile.reputation = max(
        0,
        profile.reputation - ACCEPTED_ANSWER_POINTS,
    )
    profile.save(update_fields=['reputation'])
    ReputationHistory.objects.create(
        user=answer.author,
        action='answer_accepted',
        points=-ACCEPTED_ANSWER_POINTS,
        description=f'Answer unaccepted on: {answer.question.title}',
        question=answer.question,
        answer=answer,
    )


@login_required
def post_answer_view(request, question_pk):
    question = get_object_or_404(Question, pk=question_pk, is_deleted=False)
    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = question
            answer.author = request.user
            answer.save()
            Question.objects.filter(pk=question.pk).update(answer_count=F('answer_count') + 1)
            transaction.on_commit(lambda: award_badges.delay(request.user.pk))
            create_notification(
                recipient=question.author,
                actor=request.user,
                message=f'answered your question “{question.title}”.',
                target_url=f'{question.get_absolute_url()}#answer-{answer.pk}',
            )
            messages.success(request, 'Answer posted!')
        else:
            messages.error(request, 'Please fix the errors below.')
    return redirect('question_detail', slug=question.slug)


@login_required
def edit_answer_view(request, pk):
    answer = get_object_or_404(Answer, pk=pk)
    if request.user != answer.author and not request.user.is_staff:
        messages.error(request, 'Permission denied.')
        return redirect('question_detail', slug=answer.question.slug)
    if request.method == 'POST':
        form = AnswerForm(request.POST, instance=answer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Answer updated!')
            return redirect('question_detail', slug=answer.question.slug)
    else:
        form = AnswerForm(instance=answer)

    return render(request, 'answers/edit.html', {'form': form, 'answer': answer})


@login_required
def delete_answer_view(request, pk):
    answer = get_object_or_404(Answer, pk=pk)
    if request.user != answer.author and not request.user.is_staff:
        messages.error(request, 'Permission denied.')
        return redirect('question_detail', slug=answer.question.slug)
    if request.method == 'POST' and not answer.is_deleted:
        with transaction.atomic():
            question = Question.objects.select_for_update().get(pk=answer.question_id)
            answer = (
                Answer.objects.select_for_update()
                .select_related('author', 'question')
                .get(pk=answer.pk)
            )
            if answer.is_accepted:
                revoke_accepted_answer(answer)
            answer.is_deleted = True
            answer.save(update_fields=['is_deleted'])
            question.answer_count = question.answers.filter(is_deleted=False).count()
            question.save(update_fields=['answer_count'])
        messages.success(request, 'Answer deleted.')
    return redirect('question_detail', slug=answer.question.slug)


@login_required
@require_POST
def accept_answer_view(request, pk):
    answer = get_object_or_404(
        Answer.objects.select_related('question'),
        pk=pk,
        is_deleted=False,
    )
    question = answer.question
    if request.user != question.author:
        messages.error(request, 'Only the question author can accept answers.')
        return redirect('question_detail', slug=question.slug)

    with transaction.atomic():
        question = Question.objects.select_for_update().get(pk=question.pk)
        answer = (
            Answer.objects.select_for_update()
            .select_related('author', 'question')
            .get(pk=answer.pk, is_deleted=False)
        )
        if answer.is_accepted:
            return redirect('question_detail', slug=question.slug)

        previous_answers = (
            question.answers.select_for_update()
            .filter(is_accepted=True)
            .exclude(pk=answer.pk)
            .select_related('author', 'question')
        )
        for previous in previous_answers:
            revoke_accepted_answer(previous)

        answer.is_accepted = True
        answer.save(update_fields=['is_accepted'])
        answer_profile = Profile.objects.select_for_update().get(
            user=answer.author
        )
        answer_profile.reputation += ACCEPTED_ANSWER_POINTS
        answer_profile.save(update_fields=['reputation'])
        ReputationHistory.objects.create(
            user=answer.author,
            action='answer_accepted',
            points=ACCEPTED_ANSWER_POINTS,
            description=f'Answer accepted on: {question.title}',
            question=question,
            answer=answer,
        )
        create_notification(
            recipient=answer.author,
            actor=request.user,
            message=f'accepted your answer to “{question.title}”.',
            target_url=f'{question.get_absolute_url()}#answer-{answer.pk}',
        )
        transaction.on_commit(lambda: award_badges.delay(answer.author_id))

    return redirect('question_detail', slug=question.slug)
