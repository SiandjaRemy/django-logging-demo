# myapp/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'), # URL for the main page
    path('log/', views.log_message, name='log_message'), # URL for the AJAX endpoint
]