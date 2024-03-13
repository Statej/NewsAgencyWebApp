from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=80)

    def __str__(self):
        return self.name


article_categories = [('pol', 'Politics'), ('tech', 'Technology News'), ('art', 'Art News'), ('trivia', 'Trivia News')]
article_regions = [('uk', 'UK News'), ('eu', 'European News'), ('w', 'World News')]


class Article(models.Model):
    headline = models.CharField(max_length=64)
    category = models.CharField(max_length=10, choices=article_categories)
    region = models.CharField(max_length=10, choices=article_regions)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    date = models.DateField()
    details = models.CharField(max_length=128)

    def __str__(self):
        return f"{self.headline}, {self.author.name}"

