from django.urls import path
from .views import movie_list, get_movie_by_id, get_movies_by_genre, get_movies_by_year, search_movies ,rate_movie, get_random_unrated_movies , get_latest_movies , get_popular_movies
from .views import toggle_watch_later, get_watch_later_status,get_watch_later_movies, get_rated_movies
urlpatterns = [
    path('', movie_list, name='movie-list'),  
    path('<int:movie_id>/', get_movie_by_id, name='get-movie-by-id'),  
    path('year/<int:year>/', get_movies_by_year, name='get-movies-by-year'),  
    path('search/', search_movies, name='search-movies'),  
    path('rate/', rate_movie, name='rate-movie'),
    path('random-unrated-movies/', get_random_unrated_movies, name='random-unrated-movies'),
    path('latest/', get_latest_movies, name='get_latest_movies'),
    path('popular/', get_popular_movies, name='get_popular_movies'),
    path('genre/<str:genre>/', get_movies_by_genre, name='get_movies_by_genre'),
    path('toggle-watch-later/', toggle_watch_later, name='toggle_watch_later'),
    path('watch-later-status/<int:movie_id>/', get_watch_later_status, name='watch_later_status'),
    path('watch-later/', get_watch_later_movies, name='watch_later'),
    path('rated-movies/', get_rated_movies, name='rated_movies'),
]
