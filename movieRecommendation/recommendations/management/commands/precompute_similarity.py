import os
import pickle
from django.core.management.base import BaseCommand
from movies.models import Movie
from sentence_transformers import SentenceTransformer
from annoy import AnnoyIndex
import pandas as pd

class Command(BaseCommand):
    help = "Precompute movie embeddings and build Annoy index"

    def handle(self, *args, **kwargs):
        # Fetch all movies
        movies = Movie.objects.all()
        if not movies:
            self.stdout.write("No movies found.")
            return

        # Combine movie features into a single string
        movies_data = pd.DataFrame(list(movies.values("id", "title", "genres", "overview", "keywords")))
        movies_data["combined_features"] = movies_data.apply(
            lambda row: f"{row['title']} {row['genres']} {row['overview']} {row['keywords']}", axis=1
        )

        # Encode movie features into embeddings
        self.stdout.write("Encoding movie features...")
        model = SentenceTransformer("all-MiniLM-L6-v2")
        embeddings = model.encode(movies_data["combined_features"].tolist(), show_progress_bar=True)

        # Save embeddings with IDs
        movie_embeddings = [{"id": row["id"], "embedding": embedding} for row, embedding in zip(movies_data.to_dict("records"), embeddings)]
        embeddings_path = os.path.join("recommendations", "data", "movie_embeddings.pkl")
        os.makedirs(os.path.dirname(embeddings_path), exist_ok=True)
        with open(embeddings_path, "wb") as f:
            pickle.dump(movie_embeddings, f)

        # Build Annoy index
        self.stdout.write("Building Annoy index...")
        embedding_dim = len(embeddings[0])
        index = AnnoyIndex(embedding_dim, "angular")
        for i, embedding in enumerate(embeddings):
            index.add_item(i, embedding)

        index_path = os.path.join("recommendations", "data", "movie_index.ann")
        index.build(10)  # Number of trees
        index.save(index_path)

        self.stdout.write("Precomputed movie embeddings and Annoy index saved.")
