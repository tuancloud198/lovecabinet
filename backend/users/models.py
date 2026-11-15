from django.contrib.auth.models import AbstractUser
from django.db import models
class User(AbstractUser):
    display_name = models.CharField(max_length=100)
    birth_date = models.DateField(null=True, blank=True)
    bio = models.CharField(max_length=120, blank=True)
    gender = models.CharField(max_length=30, blank=True)
