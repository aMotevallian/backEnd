from django.urls import path
from .views import movie_list, get_movie_by_id, get_movies_by_genre, get_movies_by_year, search_movies ,rate_movie, get_random_unrated_movies , get_latest_movies , get_popular_movies
from .views import toggle_watch_later, get_watch_later_status
urlpatterns = [
    path('', movie_list, name='movie-list'),  # /api/movies/
    path('<int:movie_id>/', get_movie_by_id, name='get-movie-by-id'),  # /api/movies/<id>/
    # path('genre/<str:genre>/', get_movies_by_genre, name='get-movies-by-genre'),  # /api/movies/genre/<genre>/
    path('year/<int:year>/', get_movies_by_year, name='get-movies-by-year'),  # /api/movies/year/<year>/
    path('search/', search_movies, name='search-movies'),  # /api/movies/search/?q=<query>
    path('rate/', rate_movie, name='rate-movie'),
    path('random-unrated-movies/', get_random_unrated_movies, name='random-unrated-movies'),
    path('latest/', get_latest_movies, name='get_latest_movies'),
    path('popular/', get_popular_movies, name='get_popular_movies'),
    path('genre/<str:genre>/', get_movies_by_genre, name='get_movies_by_genre'),
    path('toggle-watch-later/', toggle_watch_later, name='toggle_watch_later'),
    path('watch-later-status/<int:movie_id>/', get_watch_later_status, name='watch_later_status'),
]
