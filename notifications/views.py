from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .models import Notification


@login_required
def notification_list_view(request):
    notifications = (
        request.user.notifications
        .select_related('actor')
        .all()
    )
    page = Paginator(notifications, 20).get_page(request.GET.get('page'))
    return render(
        request,
        'notifications/list.html',
        {'page': page},
    )


@login_required
@require_POST
def mark_all_read_view(request):
    request.user.notifications.filter(is_read=False).update(
        is_read=True,
        read_at=timezone.now(),
    )
    return redirect('notifications')


@login_required
def open_notification_view(request, pk):
    notification = get_object_or_404(
        Notification,
        pk=pk,
        recipient=request.user,
    )
    if not notification.is_read:
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save(update_fields=['is_read', 'read_at'])

    target_url = notification.target_url or reverse('notifications')
    if not url_has_allowed_host_and_scheme(
        target_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return HttpResponseBadRequest('Invalid notification target.')
    return redirect(target_url)

