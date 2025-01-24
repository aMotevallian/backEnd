import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from movies.models import Movie, MovieRating

def get_user_movie_matrix():
    ratings = MovieRating.objects.all().values("user_id", "movie_id", "rating")
    df = pd.DataFrame(ratings)
    user_movie_matrix = df.pivot(index="user_id", columns="movie_id", values="rating")
    return user_movie_matrix

def calculate_user_similarity(user_movie_matrix):
    matrix = user_movie_matrix.fillna(0)
    similarity_matrix = cosine_similarity(matrix)
    similarity_df = pd.DataFrame(similarity_matrix, index=matrix.index, columns=matrix.index)
    return similarity_df

def recommend_movies(user_id, user_movie_matrix, similarity_df, num_recommendations=5):
    user_ratings = user_movie_matrix.loc[user_id]
    similar_users = similarity_df[user_id].sort_values(ascending=False)
    weighted_ratings = pd.Series(0, index=user_movie_matrix.columns)
    for other_user, similarity in similar_users.items():
        if other_user != user_id:
            other_user_ratings = user_movie_matrix.loc[other_user]
            weighted_ratings += similarity * other_user_ratings

    recommendations = weighted_ratings[user_ratings.isnull()].sort_values(ascending=False)
    return recommendations.head(num_recommendations)
