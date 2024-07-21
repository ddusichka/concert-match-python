from django.urls import path

from . import views

urlpatterns = [
    path('', views.get_concerts, name='get_concerts'),
    path('fetch/', views.fetch_concerts, name='fetch_concerts'),
    path('markets/', views.get_markets, name='get_markets')
]