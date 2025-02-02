import os
import django
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.core.management.base import BaseCommand
from movies.models import Movie

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movieRecommendation.settings")
django.setup()

class Command(BaseCommand):
    help = "Generate cosine similarity matrix for selected movies"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("Generating similarity matrix..."))

        movies = Movie.objects.all().values("id", "title", "genres", "overview", "keywords")
        df = pd.DataFrame(list(movies))

        if df.empty:
            self.stdout.write(self.style.WARNING("No movie data found."))
            return

        def combine_features(row):
            return f"{row['title']} {row['genres']} {row['overview']} {row['keywords']}"

        df["combined_features"] = df.apply(combine_features, axis=1)

        tfidf_vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = tfidf_vectorizer.fit_transform(df["combined_features"])

        cosine_sim = cosine_similarity(tfidf_matrix)

        similarity_df = pd.DataFrame(cosine_sim, index=df["title"], columns=df["title"])

        selected_movies = ["Avengers: Endgame", "Iron Man", "Spider-Man", "Doctor Strange", "Thor", "Guardians of the Galaxy"]
        selected_df = similarity_df.loc[selected_movies, selected_movies]

        if selected_df.empty:
            self.stdout.write(self.style.WARNING("Selected movies not found in dataset."))
            return

        plt.figure(figsize=(10, 6))
        sns.heatmap(selected_df, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
        plt.title("Cosine Similarity Matrix for Selected Movies")
        plt.xlabel("Movies")
        plt.ylabel("Movies")

        image_path = "cosine_similarity_matrix.png"
        plt.savefig(image_path, dpi=300)
        self.stdout.write(self.style.SUCCESS(f"Similarity matrix saved to {image_path}"))

        print(selected_df)
