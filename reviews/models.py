from django.db import models
from books.models import Book
from django.contrib.auth import get_user_model
# Create your models here.
class Review(models.Model):
    text = models.TextField()
    user=models.ForeignKey(get_user_model(),on_delete=models.CASCADE,related_name="reviews")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="reviews")