from django.urls import path
from . import views

urlpatterns = [
    path('<str:content_type>/<int:object_id>/<int:value>/', views.vote_view, name='vote'),
]
