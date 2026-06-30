from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('profile/<str:username>/follow/', views.toggle_follow_view, name='toggle_follow'),
    path('profile/<str:username>/followers/', views.followers_view, name='followers'),
    path('profile/<str:username>/following/', views.following_view, name='following'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('change-password/', views.change_password_view, name='change_password'),
    path('users/', views.users_list_view, name='users'),
]
