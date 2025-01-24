import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from movies.models import Movie

class Command(BaseCommand):
    help = 'Import movies from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        with open(csv_file, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                # Define the important fields that must not be null or empty
                important_fields = ['title', 'overview', 'poster_path', 'backdrop_path', 'release_date', 'keywords']
                missing_fields = [field for field in important_fields if not row[field].strip()]

                # Skip the row if any important field is missing
                if missing_fields:
                    self.stdout.write(
                        self.style.WARNING(f"Skipping movie due to missing fields ({', '.join(missing_fields)}): {row.get('title', 'Unknown Title')}")
                    )
                    continue  # Skip this row

                # Handle date format and skip rows with invalid dates
                release_date = None
                if row['release_date']:
                    try:
                        release_date = datetime.strptime(row['release_date'], '%Y-%m-%d').date()
                    except ValueError:
                        self.stdout.write(self.style.WARNING(f"Invalid date format for movie: {row['title']} - Skipping"))
                        continue  # Skip this row if the date is invalid

                # Update or create the movie record
                movie, created = Movie.objects.update_or_create(
                    id=row['id'],  # Check for the movie by ID
                    defaults={
                        'title': row['title'],
                        'vote_average': row['vote_average'],
                        'vote_count': row['vote_count'],
                        'status': row['status'],
                        'release_date': release_date,  # Safe to assign None if the date is invalid
                        'revenue': row['revenue'],
                        'runtime': row['runtime'],
                        'adult': row['adult'].lower() == 'true',
                        'backdrop_path': row['backdrop_path'],
                        'budget': row['budget'],
                        'homepage': row['homepage'],
                        'imdb_id': row['imdb_id'],
                        'original_language': row['original_language'],
                        'original_title': row['original_title'],
                        'overview': row['overview'],
                        'popularity': row['popularity'],
                        'poster_path': row['poster_path'],
                        'tagline': row['tagline'],
                        'genres': row['genres'],
                        'production_companies': row['production_companies'],
                        'production_countries': row['production_countries'],
                        'spoken_languages': row['spoken_languages'],
                        'keywords': row['keywords'],
                    }
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f"Movie created: {row['title']}"))
                else:
                    self.stdout.write(self.style.SUCCESS(f"Movie updated: {row['title']}"))

        self.stdout.write(self.style.SUCCESS('Movies imported successfully!'))
