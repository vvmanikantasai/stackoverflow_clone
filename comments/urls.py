from django.urls import path, re_path
from . import views

urlpatterns = [
    path('add/<str:content_type>/<int:object_id>/', views.add_comment_view, name='add_comment'),
    path('<int:pk>/edit/', views.edit_comment_view, name='edit_comment'),
    path('<int:pk>/delete/', views.delete_comment_view, name='delete_comment'),
    re_path(r'^(?P<pk>\d+)/vote/(?P<value>-?\d+)/$', views.vote_comment_view, name='vote_comment'),
]
