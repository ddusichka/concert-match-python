from django.urls import path

from . import views

urlpatterns = [
    path('<str:user_id>/', views.get_all_match_details, name='get_matches'),
    path('create/<str:user_id>/', views.create_matches, name='create_matches'),
    path('favorites/<str:user_id>/', views.get_favorite_matches_for_user, name='favorite_matches'),
    path('favorite/<str:user_id>/<int:match_id>', views.favorite_match, name='favorite_match')
]