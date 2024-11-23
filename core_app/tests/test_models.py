"""
Tests for models.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from core_app.models import Recipe


User = get_user_model()


class ModelTests(TestCase):
    """
    Test models.    
    """

    def test_create_user_with_email_successful(self):
        """
        Test creating a user with an email is successful.
        """

        email = "test@example.com"
        password = "testpass123"
        
        user = User.objects.create_user(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        
    def test_new_user_email_is_normalized(self):
        """
        Test email is normalized for new users.
        """

        sample_emails = [
            ["test1@Example.com", "test1@example.com" ],
            ["Test2@Example.com", "Test2@example.com" ],
            ["TEST3@EXAMPLE.COM", "TEST3@example.com" ],
            ["test4@example.COM", "test4@example.com" ],
        ]
        
        for email, expected in sample_emails:
            user = User.objects.create_user(email=email, password="testpass123")

            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_ValueError(self):
        """
        Test that creating a user without an email raises a ValueError.
        """

        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="testpass123")

    def test_create_superuser(self):
        """
        Test creating a supersuser.
        """
        
        user = User.objects.create_superuser(email="superuser@example.com", password="testpass123")

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        """
        Test creating a recipe is successful.
        """

        user = User.objects.create_user(email="testuser@example.com", password="testpass123")

        recipe = Recipe.objects.create(
            user=user,
            title="Sample recipe name",
            time_minutes=5,
            price=Decimal("5.50"),
            description="Sample recipe description"
        )

        self.assertEqual(Recipe.objects.count(), 1)
        self.assertEqual(str(recipe), recipe.title)         

