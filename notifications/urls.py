from django.urls import path
from . import views

urlpatterns = [
    path('', views.notifications_view, name='notifications'),
    path('mark-read/', views.mark_all_read_view, name='mark_notifications_read'),
]
