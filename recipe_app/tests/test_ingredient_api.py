"""
Tests for the ingredient API.
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core_app.models import Ingredient
from recipe_app.serializers import IngredientSerializer


INGREDIENTS_URL = reverse("recipe_app:ingredient-list")


def detail_url(ingredient_id):
    """
    create and return an ingredient detail URL.
    """

    return reverse("recipe_app:ingredient-detail", args=[ingredient_id, ])

def create_user(email="testuser@example.com", password="testpass123"):
    """
    Create and return a user.
    """

    return get_user_model().objects.create_user(email=email, password=password)


class PublicIngredientsAPITests(TestCase):
    """
    Test unauthenticated API requests.
    """

    def setUp(self):

        self.client = APIClient()

    def test_authentication_is_required_for_retrieving_ingredients(self):

        response = self.client.get(INGREDIENTS_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsAPITests(TestCase):
    """
    Test authenticated API requests.
    """

    def setUp(self):

        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):

        # create ingredients in the database
        Ingredient.objects.create(user=self.user, name="Kale")
        Ingredient.objects.create(user=self.user, name="Vanilla")

        # request the ingredients through the ingredients API
        response = self.client.get(INGREDIENTS_URL)

        # retrieve the ingredients from the database
        ingredients = Ingredient.objects.all().order_by("-name")   

        # check ingredients retrieved successfully
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, IngredientSerializer(ingredients, many=True).data)

    def test_recipes_retrieved_are_limited_to_the_auth_user(self):

        # create an ingredient using other user
        other_user = create_user(email="anotheruser@example.com")
        Ingredient.objects.create(user=other_user, name="Salt")

        # create an ingredient using the auth user
        ingredient = Ingredient.objects.create(user=self.user, name="Pepper")

        # retrieve the ingredients using the ingredients API
        response = self.client.get(INGREDIENTS_URL)

        # check that only the ingredients created by the auth user
        # were retrieved
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertDictEqual(response.data[0], IngredientSerializer(ingredient).data)

    def test_update_ingredient(self):

        # create an ingredient
        ingredient = Ingredient.objects.create(user=self.user, name="Cilantro")

        # update the ingredient
        payload = {"name": "Coriander"}
        url = detail_url(ingredient.id)
        response  = self.client.patch(url, payload)

        # check the ingredient was correctly updated
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload["name"])

    def test_delete_ingredient(self):
        
        # create an ingredient
        ingredient = Ingredient.objects.create(user=self.user, name="Lettuce")

        # delete the ingredient
        url = detail_url(ingredient.id)
        response = self.client.delete(url)

        # check the ingredient was deleted
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Ingredient.objects.count(), 0)