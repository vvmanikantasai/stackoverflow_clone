from django.urls import path
from . import views

urlpatterns = [
    path('<str:content_type>/<int:object_id>/', views.report_view, name='report'),
]
