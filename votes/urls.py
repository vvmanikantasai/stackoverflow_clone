from django.urls import re_path
from . import views

urlpatterns = [
    re_path(
        r'^(?P<content_type>question|answer)/(?P<object_id>\d+)/(?P<value>-?1)/$',
        views.vote_view,
        name='vote',
    ),
]
