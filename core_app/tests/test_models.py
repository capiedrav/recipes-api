"""
Tests for models.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from core_app.models import Recipe, Tag, Ingredient


User = get_user_model()


class UserModelTests(TestCase):
    """
    Tests for User model.    
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


class RecipeModelTests(TestCase):
    """
    Tests for Recipe model.
    """
    
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


class TagModelTests(TestCase):
    """
    Tests for Tag model.
    """

    def create_user(self, email="testuser@example.com", password="testpass123"):
        """
        Create and return an user.
        """

        return User.objects.create_user(email, password)

    def test_create_tag(self):
        """
        Test creating a tag is successful.
        """

        user = self.create_user()
        tag = Tag.objects.create(user=user, name="Tag1")

        self.assertEqual(str(tag), tag.name)


class IngredientModelTests(TestCase):
    """
    Tests for Ingredient model.
    """

    def test_create_ingredient(self):

        user = User.objects.create_user(email="testuser@example.com", password="testpass123")
        ingredient = Ingredient.objects.create(user=user, name="Ingredient1")

        self.assertEqual(str(ingredient), ingredient.name)
