from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
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
]

if not settings.USE_CLOUDINARY_MEDIA:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]
