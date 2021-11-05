from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    nickname = models.CharField(max_length=30)
    school_email = models.EmailField()
    department = models.CharField(max_length=50, default='')
    school_number = models.CharField(max_length=8,default='')
    rating_order = models.IntegerField(default=0)
    rating_delivery = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to = "userImage/", blank=True, null=True)
    is_trial =models.BooleanField(default=False)