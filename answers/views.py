from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import ReputationHistory
from badges.utils import check_and_award_badges
from questions.models import Question

from .forms import AnswerForm
from .models import Answer


ACCEPTED_ANSWER_POINTS = 15


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
            check_and_award_badges(request.user)
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
        answer.is_deleted = True
        answer.is_accepted = False
        answer.save()
        question = answer.question
        question.answer_count = max(0, question.answers.filter(is_deleted=False).count())
        question.save(update_fields=['answer_count'])
        messages.success(request, 'Answer deleted.')
    return redirect('question_detail', slug=answer.question.slug)


@login_required
def accept_answer_view(request, pk):
    answer = get_object_or_404(Answer, pk=pk)
    question = answer.question
    if request.user != question.author:
        messages.error(request, 'Only the question author can accept answers.')
        return redirect('question_detail', slug=question.slug)
    if request.method == 'POST':
        if answer.is_accepted:
            messages.info(request, 'That answer is already accepted.')
            return redirect('question_detail', slug=question.slug)
        question.answers.update(is_accepted=False)
        answer.is_accepted = True
        answer.save(update_fields=['is_accepted'])

        answer.author.profile.reputation += ACCEPTED_ANSWER_POINTS
        answer.author.profile.save(update_fields=['reputation'])
        ReputationHistory.objects.create(
            user=answer.author,
            action='answer_accepted',
            points=ACCEPTED_ANSWER_POINTS,
            description=f'Answer accepted on: {question.title}',
            question=question,
            answer=answer
        )

        check_and_award_badges(answer.author)
        messages.success(request, 'Answer accepted!')
    return redirect('question_detail', slug=question.slug)
