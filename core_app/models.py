"""
Database models.
"""

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings


USER_MODEL = settings.AUTH_USER_MODEL


class UserManager(BaseUserManager):
    """
    Manager for users.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Create, save and return a new user.
        """

        if not email:
            raise ValueError("User must have an email address.")

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """
        Create a superuser.
        """

        user = self.create_user(email=email, password=password)
        user.is_staff = True
        user.is_superuser = True

        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model.
    """

    email = models.EmailField(unique=True, max_length=255)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager() # assign UserManager class as the manager for User objects
    
    USERNAME_FIELD = "email" # use email field for authentication


class Recipe(models.Model):
    """
    Recipe model.
    """

    user = models.ForeignKey(USER_MODEL, on_delete=models.CASCADE)  
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)
    tags = models.ManyToManyField("Tag") # many recipes can have many tags
    ingredients = models.ManyToManyField("Ingredient") # many recipes can have many ingredients

    def __str__(self):

        return self.title 


class Tag(models.Model):
    """
    Tag model.

    A tag is used for filtering recipes.
    """

    name = models.CharField(max_length=255)
    user = models.ForeignKey(USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):

        return self.name
    

class Ingredient(models.Model):
    """
    Ingredient model.
    """

    name = models.CharField(max_length=255)
    user = models.ForeignKey(USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):

        return self.name
    