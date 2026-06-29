from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('questions.urls')),
    path('accounts/', include('accounts.urls')),
    path('answers/', include('answers.urls')),
    path('comments/', include('comments.urls')),
    path('tags/', include('tags.urls')),
    path('badges/', include('badges.urls')),
    path('reports/', include('reports.urls')),
    path('votes/', include('votes.urls')),
    path('notifications/', include('notifications.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if not settings.DEBUG:
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.BASE_DIR / 'static'}),
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]
