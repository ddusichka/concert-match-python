from django.urls import path

from . import views

urlpatterns = [
    path('', views.get_concerts, name='get_concerts')
]