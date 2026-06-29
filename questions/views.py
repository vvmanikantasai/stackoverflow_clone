from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.db.models import Count, F, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify

from answers.forms import AnswerForm
from answers.models import Answer
from badges.utils import check_and_award_badges
from comments.forms import CommentForm
from comments.models import Comment
from tags.models import Tag
from votes.models import Vote

from .forms import QuestionForm
from .models import Bookmark, Question, QuestionImage, RecentlyViewed


def get_visible_questions():
    """Return questions that should be shown on public pages."""
    return (
        Question.objects.filter(is_deleted=False)
        .select_related('author', 'author__profile')
        .prefetch_related('tags')
    )


def save_question_tags(question, tag_names, user):
    """Replace a question's tags with the names submitted in the form."""
    question.tags.clear()

    for tag_name in tag_names:
        tag, _ = Tag.objects.get_or_create(
            slug=slugify(tag_name),
            defaults={
                'name': tag_name,
                'created_by': user,
            },
        )
        question.tags.add(tag)


def save_question_images(question, uploaded_images):
    """Save each uploaded image against the question."""
    for image in uploaded_images:
        QuestionImage.objects.create(question=question, image=image)


def build_comment_tree(model_cls, object_id, user):
    content_type = ContentType.objects.get_for_model(model_cls)
    comments = list(
        Comment.objects.filter(
            content_type=content_type,
            object_id=object_id,
            is_deleted=False,
        )
        .select_related('author', 'author__profile')
        .order_by('created_at')
    )

    comment_votes = {}
    if user.is_authenticated:
        comment_content_type = ContentType.objects.get_for_model(Comment)
        comment_ids = [comment.pk for comment in comments]
        votes = Vote.objects.filter(
            user=user,
            content_type=comment_content_type,
            object_id__in=comment_ids,
        )
        for vote in votes:
            comment_votes[vote.object_id] = vote.value

    comments_by_id = {}
    for comment in comments:
        comment.child_comments = []
        comment.user_vote = comment_votes.get(comment.pk)
        comments_by_id[comment.pk] = comment

    root_comments = []
    for comment in comments:
        parent = comments_by_id.get(comment.parent_id)
        if parent:
            parent.child_comments.append(comment)
        else:
            root_comments.append(comment)

    return root_comments


def home_view(request):
    filter_by = request.GET.get('filter', 'newest')
    search = request.GET.get('q', '')
    questions = get_visible_questions()

    if search:
        questions = questions.filter(
            Q(title__icontains=search)
            | Q(content__icontains=search)
            | Q(tags__name__icontains=search)
        ).distinct()

    if filter_by == 'newest':
        questions = questions.order_by('-created_at')
    elif filter_by == 'active':
        questions = questions.order_by('-last_activity')
    elif filter_by == 'votes':
        questions = questions.order_by('-vote_count')
    elif filter_by == 'unanswered':
        questions = questions.filter(answer_count=0).order_by('-created_at')
    elif filter_by == 'views':
        questions = questions.order_by('-view_count')

    paginator = Paginator(questions, 15)
    page = paginator.get_page(request.GET.get('page', 1))

    hot_questions = Question.objects.filter(is_deleted=False).order_by(
        '-view_count',
        '-vote_count',
    )[:5]
    trending_tags = Tag.objects.annotate(usage=Count('questions')).order_by('-usage')[:10]
    top_contributors = (
        User.objects.filter(is_active=True)
        .select_related('profile')
        .order_by('-profile__reputation')[:5]
    )

    context = {
        'page': page,
        'filter_by': filter_by,
        'search': search,
        'hot_questions': hot_questions,
        'trending_tags': trending_tags,
        'top_contributors': top_contributors,
        'total_questions': questions.count(),
    }
    return render(request, 'questions/home.html', context)


@login_required
def ask_question_view(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST, request.FILES)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user
            question.save()

            save_question_tags(
                question,
                form.cleaned_data.get('tags_input', []),
                request.user,
            )
            save_question_images(question, request.FILES.getlist('images'))

            check_and_award_badges(request.user)
            messages.success(request, 'Question posted successfully!')
            return redirect('question_detail', slug=question.slug)
    else:
        form = QuestionForm()
    return render(request, 'questions/ask.html', {'form': form})


def question_detail_view(request, slug):
    question = get_object_or_404(Question, slug=slug, is_deleted=False)

    Question.objects.filter(pk=question.pk).update(view_count=F('view_count') + 1)
    question.refresh_from_db()

    if request.user.is_authenticated:
        RecentlyViewed.objects.update_or_create(user=request.user, question=question)

    answers = list(
        question.answers.filter(is_deleted=False)
        .select_related('author', 'author__profile')
    )
    answer_form = AnswerForm()
    comment_form = CommentForm()

    user_question_vote = None
    user_answer_votes = {}
    is_bookmarked = False

    if request.user.is_authenticated:
        question_type = ContentType.objects.get_for_model(Question)
        question_vote = Vote.objects.filter(
            user=request.user,
            content_type=question_type,
            object_id=question.pk,
        ).first()
        if question_vote:
            user_question_vote = question_vote.value

        answer_type = ContentType.objects.get_for_model(Answer)
        answer_ids = [answer.pk for answer in answers]
        votes = Vote.objects.filter(
            user=request.user,
            content_type=answer_type,
            object_id__in=answer_ids,
        )
        for vote in votes:
            user_answer_votes[vote.object_id] = vote.value

        is_bookmarked = Bookmark.objects.filter(user=request.user, question=question).exists()

    question_comments = build_comment_tree(Question, question.pk, request.user)

    answers_with_comments = []
    for answer in answers:
        answers_with_comments.append({
            'answer': answer,
            'comments': build_comment_tree(Answer, answer.pk, request.user),
            'user_vote': user_answer_votes.get(answer.pk),
        })

    related_questions = Question.objects.filter(
        tags__in=question.tags.all(), is_deleted=False
    ).exclude(pk=question.pk).distinct()[:5]

    context = {
        'question': question,
        'answers_with_comments': answers_with_comments,
        'answer_form': answer_form,
        'comment_form': comment_form,
        'user_question_vote': user_question_vote,
        'is_bookmarked': is_bookmarked,
        'q_comments': question_comments,
        'related_questions': related_questions,
        'answer_count': len(answers),
    }
    return render(request, 'questions/detail.html', context)


@login_required
def edit_question_view(request, slug):
    question = get_object_or_404(Question, slug=slug)
    if request.user != question.author and not request.user.is_staff:
        messages.error(request, 'You do not have permission to edit this question.')
        return redirect('question_detail', slug=slug)
    if request.method == 'POST':
        form = QuestionForm(request.POST, request.FILES, instance=question)
        if form.is_valid():
            question = form.save()
            save_question_tags(
                question,
                form.cleaned_data.get('tags_input', []),
                request.user,
            )
            messages.success(request, 'Question updated successfully!')
            return redirect('question_detail', slug=question.slug)
    else:
        existing_tags = ' '.join(question.tags.values_list('name', flat=True))
        form = QuestionForm(instance=question, initial={'tags_input': existing_tags})
    return render(request, 'questions/edit.html', {'form': form, 'question': question})


@login_required
def delete_question_view(request, slug):
    question = get_object_or_404(Question, slug=slug)
    if request.user != question.author and not request.user.is_staff:
        messages.error(request, 'You do not have permission to delete this question.')
        return redirect('question_detail', slug=slug)
    if request.method == 'POST':
        question.is_deleted = True
        question.save()
        messages.success(request, 'Question deleted.')
        return redirect('home')
    return render(request, 'questions/confirm_delete.html', {'question': question})


@login_required
def toggle_bookmark_view(request, pk):
    question = get_object_or_404(Question, pk=pk)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, question=question)
    if not created:
        bookmark.delete()
        bookmarked = False
    else:
        bookmarked = True
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'bookmarked': bookmarked})
    return redirect('question_detail', slug=question.slug)


@login_required
def saved_questions_view(request):
    questions = (
        Question.objects.filter(bookmarks__user=request.user, is_deleted=False)
        .select_related('author')
        .prefetch_related('tags')
        .order_by('-bookmarks__created_at')
    )
    paginator = Paginator(questions, 15)
    page = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'questions/saved.html', {'page': page})


def search_view(request):
    query = request.GET.get('q', '')
    results = []
    if query:
        results = Question.objects.filter(
            Q(title__icontains=query)
            | Q(content__icontains=query)
            | Q(tags__name__icontains=query),
            is_deleted=False,
        )
        results = (
            results.distinct()
            .select_related('author')
            .prefetch_related('tags')
            .order_by('-vote_count')
        )
    paginator = Paginator(results, 15)
    page = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'questions/search.html', {'page': page, 'query': query})
