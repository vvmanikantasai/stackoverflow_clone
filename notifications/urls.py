from django.urls import path

from . import views


urlpatterns = [
    path('', views.notification_list, name='notifications'),
    path('<int:pk>/open/', views.open_notification, name='open_notification'),
    path('read-all/', views.mark_all_read, name='mark_all_notifications_read'),
]
