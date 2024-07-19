from django.urls import path

from . import views

urlpatterns = [
    path('top-tracks/', views.get_top_tracks, name='get_top_tracks'),
    path('login/', views.login, name='login'),
    path('callback/', views.callback, name='callback'),
    ]