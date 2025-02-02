from django.http import JsonResponse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utils import get_user_movie_matrix, calculate_user_similarity, recommend_movies
from movies.models import Movie , MovieRating
from movies.serializers import MovieSerializer
from django.db.models import Q
from rest_framework.decorators import api_view , authentication_classes ,permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

@api_view(['GET'])
def get_movie_recommendations(request ,movie_id):
    try:
        print("cb")
        movies = Movie.objects.all()
        if not movies:
            return []

        movies_data = pd.DataFrame(list(movies.values("id", "title", "genres", "overview", "keywords")))
        if movies_data.empty:
            return []

        def combine_features(row):
            return f"{row['title']} {row['genres']} {row['overview']} {row['keywords']}"

        movies_data["combined_features"] = movies_data.apply(combine_features, axis=1)

        tfidf_vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = tfidf_vectorizer.fit_transform(movies_data["combined_features"])

        movie_index = movies_data[movies_data["id"] == movie_id].index[0]

        similarity_scores = cosine_similarity(tfidf_matrix[movie_index], tfidf_matrix).flatten()

        top_indices = similarity_scores.argsort()[-11:][::-1][1:]
        recommended_movie_ids = movies_data.iloc[top_indices]["id"].tolist()

        recommended_movies = Movie.objects.filter(id__in=recommended_movie_ids)
        serializer = MovieSerializer(recommended_movies, many=True)
        return Response(serializer.data)
    except Exception as e:
        raise ValueError(f"Error in recommendation: {str(e)}")

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def recommend_movies_for_user(request):
    try:
        user = request.user
        user_id = user.id
        user_movie_matrix = get_user_movie_matrix()
        similarity_df = calculate_user_similarity(user_movie_matrix)
        recommendations = recommend_movies(user_id, user_movie_matrix, similarity_df)

        recommended_movie_ids = recommendations.index.tolist()
        recommended_movies = Movie.objects.filter(id__in=recommended_movie_ids)

        serializer = MovieSerializer(recommended_movies, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({"error": str(e)}, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def hybrid_recommendation(request):
    try:
        user = request.user
        user_id = user.id
        user_movie_matrix = get_user_movie_matrix()

        similarity_df = calculate_user_similarity(user_movie_matrix)
        collaborative_recommendations = recommend_movies(user_id, user_movie_matrix, similarity_df, num_recommendations=20)
        user_ratings = MovieRating.objects.filter(user_id=user_id).order_by('-rating')
        if user_ratings.exists():
            first_movie = user_ratings.first().movie
            content_based_recommendations = get_movie_recommendations(request._request, first_movie.id).data
        else:
            content_based_recommendations = []
        combined_scores = {}
        for movie_id in collaborative_recommendations:
            combined_scores[(movie_id)] = combined_scores.get(movie_id, 0) + 0.7  

        for movie in content_based_recommendations:
            movie_id = movie["id"]
            combined_scores[movie_id] = combined_scores.get(movie_id, 0) + 0.3 
        sorted_movies = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        recommended_movie_ids = [movie_id for movie_id, _ in sorted_movies[:10]]

        recommended_movies = Movie.objects.filter(id__in=recommended_movie_ids)
        serializer = MovieSerializer(recommended_movies, many=True)
        return Response(serializer.data)

    except Exception as e:
        return Response({"error": str(e)}, status=400)
