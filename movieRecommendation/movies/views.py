# movies/views.py
from rest_framework.decorators import api_view , authentication_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import Movie
from .serializers import MovieSerializer
from rest_framework.authentication import TokenAuthentication

from .models import WatchLater
@api_view(['GET'])
def movie_list(request):
    """
    List all movies with pagination.
    """
    movies = Movie.objects.only('id', 'title', 'release_date', 'poster_path', 'overview')  # Optimized query
    paginator = PageNumberPagination()
    paginator.page_size = 10  # Set items per page
    paginated_movies = paginator.paginate_queryset(movies, request)
    serializer = MovieSerializer(paginated_movies, many=True)
    return paginator.get_paginated_response(serializer.data)
@api_view(['GET'])
def get_movie_by_id(request, movie_id):
    """
    Retrieve a specific movie by its ID.
    """
    try:
        movie = Movie.objects.get(id=movie_id)
        serializer = MovieSerializer(movie)
        return Response(serializer.data, status=200)
    except Movie.DoesNotExist:
        return Response({'error': 'Movie not found'}, status=404)
# @api_view(['GET'])
# def get_movies_by_genre(request, genre):
#     """
#     Retrieve movies by a specific genre.
#     """
#     movies = Movie.objects.filter(genres__icontains=genre).only('id', 'title', 'poster_path', 'release_date', 'overview')
#     paginator = PageNumberPagination()
#     paginator.page_size = 10
#     paginated_movies = paginator.paginate_queryset(movies, request)
#     serializer = MovieSerializer(paginated_movies, many=True)
#     return paginator.get_paginated_response(serializer.data)
@api_view(['GET'])
def get_movies_by_year(request, year):
    """
    Retrieve movies released in a specific year.
    """
    movies = Movie.objects.filter(release_date__year=year).only('id', 'title', 'poster_path', 'release_date', 'overview')
    paginator = PageNumberPagination()
    paginator.page_size = 10
    paginated_movies = paginator.paginate_queryset(movies, request)
    serializer = MovieSerializer(paginated_movies, many=True)
    return paginator.get_paginated_response(serializer.data)
@api_view(['GET'])
def search_movies(request):
    """
    Search movies by title.
    """
    query = request.query_params.get('q', '')
    if not query:
        return Response({'error': 'Search query is required'}, status=400)

    movies = Movie.objects.filter(title__startswith=query).only('id', 'title', 'poster_path', 'release_date', 'overview' ,'genres')
    paginator = PageNumberPagination()
    paginator.page_size = 10
    paginated_movies = paginator.paginate_queryset(movies, request)
    serializer = MovieSerializer(paginated_movies, many=True)
    return paginator.get_paginated_response(serializer.data)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from .models import Movie
from .models import MovieRating
from .serializers import MovieSerializer
import random

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_random_unrated_movies(request):
    """
    دریافت فیلم‌هایی که کاربر هنوز به آنها رتبه نداده است.
    """
    user = request.user
    rated_movie_ids = MovieRating.objects.filter(user=user).values_list('movie_id', flat=True)
    unrated_movies = Movie.objects.exclude(id__in=rated_movie_ids)

    # ترتیب تصادفی
    unrated_movies = list(unrated_movies)
    random.shuffle(unrated_movies)

    # صفحه‌بندی
    paginator = PageNumberPagination()
    paginator.page_size = 10
    paginated_movies = paginator.paginate_queryset(unrated_movies, request)

    movie_data = [
        {
            'id': movie.id,
            'title': movie.title,
            'release_date': movie.release_date,
            'poster_path': movie.poster_path,
            'overview': movie.overview,
        }
        for movie in paginated_movies
    ]

    return paginator.get_paginated_response(movie_data)

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User  # مدل پیش‌فرض User
from .models import Movie, MovieRating

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def rate_movie(request):
    """
    ذخیره یا به‌روزرسانی رتبه‌بندی یک فیلم توسط کاربر.
    """
    user = request.user  # کاربر احراز هویت‌شده
    movie_id = request.data.get('movie_id')
    rating = request.data.get('rating')

    # بررسی اعتبار داده‌ها
    if not movie_id or not rating:
        return Response({'error': 'Movie ID and rating are required.'}, status=status.HTTP_400_BAD_REQUEST)

    if not (1 <= int(rating) <= 5):
        return Response({'error': 'Rating must be between 1 and 5.'}, status=status.HTTP_400_BAD_REQUEST)

    # بررسی وجود فیلم
    movie = Movie.objects.filter(id=movie_id).first()
    if not movie:
        return Response({'error': 'Movie not found.'}, status=status.HTTP_404_NOT_FOUND)

    # ذخیره یا به‌روزرسانی رتبه‌بندی
    rating_obj, created = MovieRating.objects.update_or_create(
        user=user,
        movie=movie,
        defaults={'rating': rating}
    )

    return Response({
        'message': 'Rating saved successfully!',
        'rating': rating_obj.rating,
        'movie': movie.title
    }, status=status.HTTP_200_OK)
    
@api_view(['GET'])
def get_latest_movies(request):
    """
    Retrieve movies released in 2024.
    """
    movies = Movie.objects.filter(release_date__year=2024).only(
        'id', 'title', 'poster_path', 'release_date', 'overview', 'vote_average'
    ).order_by('-release_date','-popularity','-vote_average')

    paginator = PageNumberPagination()
    paginator.page_size = 10
    paginated_movies = paginator.paginate_queryset(movies, request)
    serializer = MovieSerializer(paginated_movies, many=True)
    return paginator.get_paginated_response(serializer.data)
from datetime import date, timedelta

@api_view(['GET'])
def get_popular_movies(request):
    """
    Retrieve movies with IMDb rating > 8 from the last 3 years.
    """
    three_years_ago = date.today() - timedelta(days=3 * 365)
    movies = Movie.objects.filter(
        vote_average__gte=8,
        release_date__gte=three_years_ago
    ).only('id', 'title', 'poster_path', 'release_date', 'overview', 'vote_average'
    ).order_by('-popularity','-vote_average')

    paginator = PageNumberPagination()
    paginator.page_size = 10
    paginated_movies = paginator.paginate_queryset(movies, request)
    serializer = MovieSerializer(paginated_movies, many=True)
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
def get_movies_by_genre(request, genre):
    """
    Retrieve movies by a specific genre, sorted by year and IMDb rating.
    """
    movies = Movie.objects.filter(genres__startswith=genre).only(
        'id', 'title', 'poster_path', 'release_date', 'overview', 'vote_average'
    ).order_by('-release_date','-popularity','-vote_average')

    paginator = PageNumberPagination()
    paginator.page_size = 10
    paginated_movies = paginator.paginate_queryset(movies, request)
    serializer = MovieSerializer(paginated_movies, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def toggle_watch_later(request):
    user = request.user
    movie_id = request.data.get('movie_id')

    if not movie_id:
        return Response({"error": "Movie ID is required"}, status=400)

    watch_later_entry, created = WatchLater.objects.get_or_create(user=user, movie_id=movie_id)

    if not created:
        # If the movie is already in watch later, remove it
        watch_later_entry.delete()
        return Response({"message": "Removed from Watch Later"})

    return Response({"message": "Saved to Watch Later"})

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_watch_later_status(request, movie_id):
    user = request.user
    exists = WatchLater.objects.filter(user=user, movie_id=movie_id).exists()
    return Response({"saved": exists})
