from django.urls import path

from . import views

urlpatterns = [
    path('', views.get_all_match_details, name='find_matches'),
    path('create/', views.find_and_create_matches, name='find_matches')
]