from django.db import models
from django.contrib.auth.models import User  

class Movie(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    vote_average = models.FloatField()
    vote_count = models.IntegerField()
    status = models.CharField(max_length=50)
    release_date = models.DateField()
    revenue = models.BigIntegerField()
    runtime = models.IntegerField()
    adult = models.BooleanField()
    backdrop_path = models.CharField(max_length=255)
    budget = models.BigIntegerField()
    homepage = models.URLField(blank=True, null=True)
    imdb_id = models.CharField(max_length=20)
    original_language = models.CharField(max_length=10)
    original_title = models.CharField(max_length=255)
    overview = models.TextField()
    popularity = models.FloatField()
    poster_path = models.CharField(max_length=255)
    tagline = models.CharField(max_length=255)
    genres = models.CharField(max_length=255)  # Could also be a ManyToManyField if normalized
    production_companies = models.TextField()  # Consider a separate table if normalized
    production_countries = models.TextField()
    spoken_languages = models.TextField()
    keywords = models.TextField()

    def __str__(self):
        return self.title

class MovieRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # ارتباط با کاربر
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)  # ارتباط با فیلم
    rating = models.PositiveSmallIntegerField()  # رتبه از 1 تا 5
    rated_at = models.DateTimeField(auto_now_add=True)  # زمان ثبت رتبه

    class Meta:
        unique_together = ('user', 'movie')  # جلوگیری از ثبت چندین رتبه برای یک فیلم توسط یک کاربر

    def __str__(self):
        return f"{self.user.username} rated {self.movie.title} as {self.rating}"

class WatchLater(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Movie {self.movie_id}"
