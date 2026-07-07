from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from answers.models import Answer
from notifications.models import Notification
from notifications.services import create_notification
from questions.models import Question
from votes.models import Vote
from .forms import CommentForm
from .models import Comment

def is_ajax(request):
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'


def get_comment_target(content_type, object_id):
    if content_type == 'question':
        return get_object_or_404(Question, pk=object_id)
    if content_type == 'answer':
        return get_object_or_404(Answer, pk=object_id)
    return None


def get_question_url(target):
    if isinstance(target, Question):
        return target.get_absolute_url()
    return target.question.get_absolute_url()


def collect_comment_subtree_ids(comment):
    comment_ids = [comment.pk]
    for reply in comment.replies.all():
        comment_ids.extend(collect_comment_subtree_ids(reply))
    return comment_ids


@login_required
def add_comment_view(request, content_type, object_id):
    target = get_comment_target(content_type, object_id)
    if not target:
        return JsonResponse({'error': 'Invalid'}, status=400)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            target_type = ContentType.objects.get_for_model(target)
            parent = None
            parent_id = request.POST.get('parent_id')

            if parent_id:
                parent = get_object_or_404(
                    Comment,
                    pk=parent_id,
                    content_type=target_type,
                    object_id=object_id,
                    is_deleted=False,
                )

            comment = Comment.objects.create(
                author=request.user,
                content=form.cleaned_data['content'],
                content_type=target_type,
                object_id=object_id,
                parent=parent,
            )
            question_id = (
                target.pk
                if isinstance(target, Question)
                else target.question_id
            )
            Question.objects.filter(pk=question_id).update(
                last_activity=timezone.now(),
            )
            target_url = f'{get_question_url(target)}#comment-{comment.pk}'
            if parent:
                create_notification(
                    recipient=parent.author,
                    actor=request.user,
                    kind=Notification.Kind.REPLY,
                    message=(
                        f'{request.user.username} replied to your comment.'
                    ),
                    target_url=target_url,
                )

            target_author = target.author
            if not parent or target_author.pk != parent.author_id:
                target_name = 'question' if isinstance(target, Question) else 'answer'
                create_notification(
                    recipient=target_author,
                    actor=request.user,
                    kind=Notification.Kind.COMMENT,
                    message=(
                        f'{request.user.username} commented on your '
                        f'{target_name}.'
                    ),
                    target_url=target_url,
                )

            if is_ajax(request):
                return JsonResponse({
                    'success': True,
                    'comment_id': comment.pk,
                    'content': comment.content,
                    'author': comment.author.username,
                    'created_at': comment.created_at.strftime('%b %d, %Y'),
                    'parent_id': parent.pk if parent else None,
                })

        elif is_ajax(request):
            return JsonResponse({'success': False, 'errors': form.errors})

    return redirect(get_question_url(target))


@login_required
def edit_comment_view(request, pk):
    comment = get_object_or_404(Comment, pk=pk, is_deleted=False)
    if request.user != comment.author and not request.user.is_staff:
        if is_ajax(request):
            return JsonResponse({'success': False, 'error': 'Permission denied.'}, status=403)

        messages.error(request, 'Permission denied.')
        return redirect(request.META.get('HTTP_REFERER', '/'))

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            if is_ajax(request):
                return JsonResponse({'success': True, 'content': comment.content})

            messages.success(request, 'Comment updated.')
        elif is_ajax(request):
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def delete_comment_view(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if request.user != comment.author and not request.user.is_staff:
        messages.error(request, 'Permission denied.')
    elif request.method == 'POST':
        comment_ids = collect_comment_subtree_ids(comment)
        Comment.objects.filter(pk__in=comment_ids).update(is_deleted=True)
        if is_ajax(request):
            return JsonResponse({'success': True})

        messages.success(request, 'Comment deleted.')

    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def vote_comment_view(request, pk, value):
    value = int(value)
    if value != 1:
        return JsonResponse(
            {'success': False, 'error': 'Comments can only be upvoted.'},
            status=400,
        )

    comment = get_object_or_404(Comment, pk=pk, is_deleted=False)
    if comment.author == request.user:
        return JsonResponse({
            'success': False,
            'error': 'Cannot vote on your own comment',
            'vote_count': comment.vote_count,
        }, status=400)

    comment_type = ContentType.objects.get_for_model(Comment)
    existing_vote = Vote.objects.filter(
        user=request.user,
        content_type=comment_type,
        object_id=comment.pk,
    ).first()

    if existing_vote:
        if existing_vote.value == value:
            existing_vote.delete()
            Comment.objects.filter(pk=comment.pk).update(vote_count=F('vote_count') - value)
            user_vote = None
        else:
            old_value = existing_vote.value
            existing_vote.value = value
            existing_vote.save(update_fields=['value'])
            Comment.objects.filter(pk=comment.pk).update(vote_count=F('vote_count') - old_value + value)
            user_vote = value
    else:
        Vote.objects.create(
            user=request.user,
            content_type=comment_type,
            object_id=comment.pk,
            value=value,
        )
        Comment.objects.filter(pk=comment.pk).update(vote_count=F('vote_count') + value)
        user_vote = value

    comment.refresh_from_db(fields=['vote_count'])
    return JsonResponse({'success': True, 'vote_count': comment.vote_count, 'user_vote': user_vote})
