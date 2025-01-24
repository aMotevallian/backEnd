from django.urls import path
from . import views

urlpatterns = [
    path('<int:movie_id>/', views.get_movie_recommendations, name='cb_movie_recommendations'),
    path('user/ub_recommendations/', views.recommend_movies_for_user, name='ub_recommend_movies'),
    path('user/hybridRecommendations/', views.hybrid_recommendation, name='hybrid_recommend_movies'),
]
