from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    nickname = models.CharField(max_length=30)
    school_email = models.EmailField()
    rating_order = models.IntegerField(default=0)
    rating_delivery = models.IntegerField(default=0)