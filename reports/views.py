from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from .models import Report
from questions.models import Question
from answers.models import Answer
from comments.models import Comment


@login_required
def report_view(request, content_type, object_id):
    if content_type == 'question':
        model = Question
    elif content_type == 'answer':
        model = Answer
    elif content_type == 'comment':
        model = Comment
    else:
        messages.error(request, 'Invalid report target.')
        return redirect('home')

    obj = get_object_or_404(model, pk=object_id)

    if request.method == 'POST':
        reason = request.POST.get('reason')
        description = request.POST.get('description', '')
        target_type = ContentType.objects.get_for_model(model)
        already_reported = Report.objects.filter(
            reporter=request.user,
            content_type=target_type,
            object_id=object_id,
        ).exists()

        if already_reported:
            messages.warning(request, 'You have already reported this.')
        else:
            Report.objects.create(
                reporter=request.user,
                reason=reason,
                description=description,
                content_type=target_type,
                object_id=object_id,
            )
            messages.success(request, 'Report submitted. Thank you.')

        return redirect(request.META.get('HTTP_REFERER', '/'))

    context = {
        'object': obj,
        'content_type': content_type,
        'object_id': object_id,
    }
    return render(request, 'reports/report.html', context)
