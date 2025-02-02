from django.core.management.base import BaseCommand
from movies.models import Movie  
import re

class Command(BaseCommand):
    help = 'Clean up the movie dataset by removing incomplete, offensive, and irrelevant entries.'

    def handle(self, *args, **kwargs):
        offensive_words = [
            "fuck", "cock", "bitch", "slut", "sex", "porn", "naked", "damn", "shit",
            "asshole", "dick", "pussy", "whore", "f**k", "c*", "f*", "s*", "bdsm",
            "pu*", "b*", "bitch", "Sexy", "Sex"
        ]
        escaped_words = [re.escape(word) for word in offensive_words]

        offensive_pattern = re.compile(r"|".join(escaped_words), re.IGNORECASE)

        incomplete_movies = Movie.objects.filter(
            title__isnull=True
        ) | Movie.objects.filter(
            title__exact=""
        ) | Movie.objects.filter(
            overview__isnull=True
        ) | Movie.objects.filter(
            overview__exact=""
        )
        incomplete_count = incomplete_movies.count()
        incomplete_movies.delete()
        self.stdout.write(f"Deleted {incomplete_count} movies with missing critical fields.")

        short_movies = Movie.objects.filter(runtime__lt=60)
        short_count = short_movies.count()
        short_movies.delete()
        self.stdout.write(f"Deleted {short_count} movies with runtime shorter than 60 minutes.")


        movies_without_imdb_id = Movie.objects.filter(imdb_id__isnull=True)
        imdb_id_count = movies_without_imdb_id.count()
        movies_without_imdb_id.delete()
        self.stdout.write(f"Deleted {imdb_id_count} movies without IMDb ID.")


        low_vote_movies = Movie.objects.filter(vote_count__lt=100)
        low_vote_count = low_vote_movies.count()
        low_vote_movies.delete()
        self.stdout.write(f"Deleted {low_vote_count} movies with less than 100 votes.")

        offensive_movies = Movie.objects.filter(
            keywords__iregex=offensive_pattern.pattern
        ) | Movie.objects.filter(
            overview__iregex=offensive_pattern.pattern
        )| Movie.objects.filter(
            title__iregex=offensive_pattern.pattern
        )
        offensive_count = offensive_movies.count()
        offensive_movies.delete()
        self.stdout.write(f"Deleted {offensive_count} movies with offensive content.")

        self.stdout.write("Dataset cleanup complete.")
