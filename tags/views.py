from django.core.paginator import Paginator
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from questions.models import Question
from .models import Tag


def tags_list_view(request):
    search = request.GET.get('q', '')
    sort_by = request.GET.get('sort', 'popular')
    tags = Tag.objects.annotate(usage=Count('questions'))
    if search:
        tags = tags.filter(name__icontains=search)
    if sort_by == 'name':
        tags = tags.order_by('name')
    elif sort_by == 'new':
        tags = tags.order_by('-created_at')
    else:
        sort_by = 'popular'
        tags = tags.order_by('-usage', 'name')

    if request.GET.get('format') == 'json':
        return JsonResponse({
            'tags': [
                {'name': tag.name, 'slug': tag.slug, 'usage': tag.usage}
                for tag in tags[:10]
            ]
        })

    paginator = Paginator(tags, 36)
    page = paginator.get_page(request.GET.get('page', 1))
    return render(
        request,
        'tags/list.html',
        {'page': page, 'search': search, 'sort': sort_by},
    )


def tag_detail_view(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    questions = (
        Question.objects.filter(tags=tag, is_deleted=False)
        .select_related('author')
        .order_by('-created_at')
    )
    paginator = Paginator(questions, 15)
    page = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'tags/detail.html', {'tag': tag, 'page': page})
