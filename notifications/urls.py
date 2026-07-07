from django.urls import path

from . import views


urlpatterns = [
    path('', views.notification_list_view, name='notifications'),
    path('read-all/', views.mark_all_read_view, name='mark_all_notifications_read'),
    path('<int:pk>/open/', views.open_notification_view, name='open_notification'),
]

