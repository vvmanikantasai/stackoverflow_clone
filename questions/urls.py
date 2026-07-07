from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('questions/', views.questions_view, name='questions'),
    path('ask/', views.ask_question_view, name='ask_question'),
    path('questions/<slug:slug>/', views.question_detail_view, name='question_detail'),
    path('questions/<slug:slug>/edit/', views.edit_question_view, name='edit_question'),
    path('questions/<slug:slug>/delete/', views.delete_question_view, name='delete_question'),
    path('questions/<int:pk>/bookmark/', views.toggle_bookmark_view, name='toggle_bookmark'),
    path('saved/', views.saved_questions_view, name='saved_questions'),
    path('search/', views.search_view, name='search'),
]
