"""
Database models.
"""

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    """
    Manager for users.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Create, save and return a new user.
        """

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
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
