from django.urls import path
from . import views

urlpatterns = [
    path('', views.tags_list_view, name='tags'),
    path('<slug:slug>/', views.tag_detail_view, name='tag_detail'),
]
