from django.urls import path
from . import views

urlpatterns = [
    path('post/<int:question_pk>/', views.post_answer_view, name='post_answer'),
    path('<int:pk>/edit/', views.edit_answer_view, name='edit_answer'),
    path('<int:pk>/delete/', views.delete_answer_view, name='delete_answer'),
    path('<int:pk>/accept/', views.accept_answer_view, name='accept_answer'),
]
