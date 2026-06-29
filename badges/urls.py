from django.urls import path
from . import views

urlpatterns = [
    path('', views.badges_list_view, name='badges'),
]
