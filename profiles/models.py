from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
class Profile(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="profileImages")
    user= models.OneToOneField(get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        return self.name