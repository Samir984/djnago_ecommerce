from django.db import models
from django.contrib.auth.models import AbstractUser,AbstractBaseUser

class User(AbstractUser):
    email= models.EmailField(unique=True )