"""
Tests for recipe APIs.
"""

from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core_app.models import Recipe
from recipe_app.serializers import RecipeSerializer


RECIPES_URL = reverse("recipe_app:recipe-list")
User = get_user_model()


def create_recipe(user, **params):
    """
    Create and return a sample recipe.
    """

    defaults = {
        "title": "Sample recipe title",
        "time_minutes": 22,
        "price": Decimal("5.25"),
        "description": "Sample description",
        "link": "http://example.com/recipe.pdf"

    }

    defaults.update(params)
    recipe = Recipe.objects.create(user=user, **defaults)

    return recipe


class PublicRecipeAPITests(TestCase):
    """
    Test unauthenticated API requests.
    """

    def setUp(self):
        self.client = APIClient()

    def test_authentication_is_required_to_access_recipes(self):

        response = self.client.get(RECIPES_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED) 


class PrivateRecipeAPITests(TestCase):
    """
    Test authenticated API requests.
    """

    def setUp(self):

        self.client = APIClient()
        self.user = User.objects.create_user(email="testuser@example.com", password="testpass123")
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):

        # create several recipes
        create_recipe(user=self.user)
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        response = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.all().order_by("-id")
        serializer = RecipeSerializer(recipes, many=True)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_only_retrieve_recipes_of_authenticated_user(self):

        other_user = User.objects.create_user(
            email="otheruser@example.com",
            password="testpass123"
        )

        create_recipe(user=other_user) # create a recipe with other user
        create_recipe(user=self.user) # create a recipe with auth user

        response = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
        