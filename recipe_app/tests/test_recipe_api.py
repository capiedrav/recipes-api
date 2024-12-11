"""
Tests for recipe APIs.
"""

from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core_app.models import Recipe, Tag, Ingredient
from recipe_app.serializers import RecipeSerializer, RecipeDetailSerializer, \
     TagSerializer, IngredientSerializer 


RECIPES_URL = reverse("recipe_app:recipe-list")
User = get_user_model()


def create_user(**params):
    """
    Create and return a new user.
    """

    return User.objects.create_user(**params)

def detail_url(recipe_id):
    """
    Create and return a recipe detail URL.
    """

    return reverse("recipe_app:recipe-detail", args=[recipe_id, ])


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
        self.user = create_user(email="testuser@example.com", password="passtest123") 
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

        other_user = create_user(email="otheruser@example.com", password="testpass123")
        
        create_recipe(user=other_user) # create a recipe with other user
        create_recipe(user=self.user) # create a recipe with auth user

        response = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
        
    def test_get_recipe_detail(self):

        recipe = create_recipe(user=self.user)

        url = detail_url(recipe_id=recipe.id)
        response = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_recipe(self):

        payload = {
            "title": "Sample recipe",
            "time_minutes": 30,
            "price": Decimal("5.99")
        }

        # make POST request to create a new recipe
        response  = self.client.post(RECIPES_URL, payload)

        # check the recipe was created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # check the recipe data was stored correctly
        recipe = Recipe.objects.first()
        self.assertDictEqual(response.data, RecipeDetailSerializer(recipe).data)
         
    def test_partial_recipe_update(self):

        # create a recipe
        original_link = "http://example.com/recipe.pdf"        
        recipe = create_recipe(
            user=self.user,
            title="Sample recipe title",
            link=original_link
        )

        # update recipe title
        payload = {"title": "New recipe title"}
        url = detail_url(recipe_id=recipe.id)
        response = self.client.patch(url, payload)

        # check the update was successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload["title"])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_recipe_update(self):

        # create a recipe
        recipe = create_recipe(
            user=self.user,
            title="Sample recipe title",
            link = "http://example.com/recipe.pdf",
            description="Sample recipe description"
        )

        payload = {
            "title": "New recipe title",
            "link": "http://example.com/new-recipe.pdf",
            "description": "New recipe description",
            "time_minutes": 10,
            "price": Decimal("2.50")
        }

        # update all recipe info
        url = detail_url(recipe_id=recipe.id)
        response = self.client.put(url, payload)

        # check the update was successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertDictEqual(response.data, RecipeDetailSerializer(recipe).data)

    def test_cant_change_recipe_user(self):
        
        # create a recipe
        recipe = create_recipe(user=self.user)
        
        # create a new user, and try to update the recipe user
        new_user = create_user(email="user2@example.com", password="testpass123")
        payload = {"user": new_user.id}  
        url = detail_url(recipe_id=recipe.id)
        response = self.client.patch(url, payload)

        # check the update did not work
        recipe.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):

        # create a recipe
        recipe = create_recipe(user=self.user)

        # delete the recipe
        url = detail_url(recipe_id=recipe.id)
        response = self.client.delete(url)

        # check the recipe was deleted
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Recipe.objects.count(), 0)

    def test_cant_delete_other_users_recipe(self):
        
        # create another user's recipe
        other_user = create_user(email="otheruser@example.com", password="testpass123")
        recipe = create_recipe(user=other_user)
        
        # try to delete it
        url = detail_url(recipe_id=recipe.id)
        response = self.client.delete(url)

        # check the recipe was not deleted
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Recipe.objects.count(), 1)

    def test_create_recipe_with_tags(self):

        # recipe with tags
        payload = {
            "title": "Thai Prawn Curry",
            "time_minutes": 30,
            "price": Decimal("2.50"),
            "tags": [{"name": "Thai"}, {"name": "Dinner"}] # note the tags
        }
        response = self.client.post(RECIPES_URL, data=payload, format="json") # make a POST request to create the recipe

        # check the recipe was created successfully
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)        
        self.assertEqual(Recipe.objects.count(), 1)

        # check also the tags
        recipe = Recipe.objects.first()
        self.assertEqual(recipe.tags.count(), 2) 
        self.assertEqual(response.data["tags"], TagSerializer(recipe.tags, many=True).data)

    def test_create_recipe_with_existing_tags_dont_duplicate_tags(self):

        # create a tag
        tag_1 = Tag.objects.create(user=self.user, name="Indian")

        # recipe with tags
        payload = {
            "title": "Pongal",
            "time_minutes": 60,
            "price": Decimal("4.50"),
            "tags": [
                {"name": "Indian"}, # This tag already exists (tag_1)
                {"name": "Breakfast"}
            ]
        }        
        response = self.client.post(RECIPES_URL, data=payload, format="json") # make a POST request to create the recipe

        # check the recipe was created successfully
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Recipe.objects.count(), 1)

        # check for no duplicated tags
        recipe = Recipe.objects.first()        
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag_1, recipe.tags.all())
        self.assertEqual(response.data["tags"], TagSerializer(recipe.tags, many=True).data)

    def test_can_add_a_tag_when_updating_a_recipe(self):
        # create a recipe
        recipe = create_recipe(user=self.user)
        
        # update the recipe adding a tag
        payload = {"tags": [{"name": "Lunch"}, ]}
        url = detail_url(recipe_id=recipe.id)
        response = self.client.patch(url, data=payload, format="json")

        # check the recipe was updated
        self.assertEqual(response.status_code, status.HTTP_200_OK)        
        tag = Tag.objects.get(user=self.user, name="Lunch")       
        self.assertIn(tag, recipe.tags.all())

    def test_change_tag_of_a_recipe(self):
        
        # create a recipe with a tag
        tag_breakfast = Tag.objects.create(user=self.user, name="Breakfast")
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_breakfast)

        # update the tag
        payload = {"tags": [{"name": "Lunch"}, ]}
        url = detail_url(recipe_id=recipe.id)
        response = self.client.patch(url, data=payload, format="json")

        # check the tag was updated successfully
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        tag_lunch = Tag.objects.get(user=self.user, name="Lunch")
        self.assertIn(tag_lunch, recipe.tags.all())
        self.assertNotIn(tag_breakfast, recipe.tags.all())
 
    def test_clear_recipe_tags(self):

        # create a recipe with a tag
        tag_breakfast = Tag.objects.create(user=self.user, name="Breakfast")
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_breakfast)

        # delete the tag
        payload = {"tags": []}
        url = detail_url(recipe_id=recipe.id)
        response = self.client.patch(url, data=payload, format="json")

        # check the tag was successfully deleted
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)

    def test_create_a_recipe_with_ingredients(self):
        
        # create a recipe 
        payload = {
            "title": "Cauliflower Tacos",
            "time_minutes": 60,
            "price": Decimal("4.30"),
            "ingredients": [ # note the recipe include ingredients
                    {"name": "Cauliflower"},
                    {"name": "Salt"}
                ]
        }
        response = self.client.post(RECIPES_URL, data=payload, format="json")

        # check the recipe was created 
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)

        # check the ingredients were created correctly
        ingredients = Ingredient.objects.filter(user=self.user)
        self.assertEqual(ingredients.count(), 2)
        self.assertEqual(response.data["ingredients"], IngredientSerializer(ingredients, many=True).data)
        
    def test_create_a_recipe_with_existing_ingredients_dont_duplicate_ingredients(self):

        # create an ingredient
        ingredient = Ingredient.objects.create(user=self.user, name="Lemon")

        # create a recipe 
        payload = {
            "title": "Vietnamese Soup",
            "time_minutes": 25,
            "price": Decimal("2.55"),
            "ingredients": [
                {"name": "Lemon"}, # note this ingredient already exists in the database
                {"name": "Fish Sauce"}
            ]
        }
        response = self.client.post(RECIPES_URL, data=payload, format="json")

        # check the recipe was created successfully
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)

        # check that no duplicate ingredients were created
        ingredients = Ingredient.objects.filter(user=self.user)
        self.assertEqual(ingredients.count(), 2)
        self.assertEqual(response.data["ingredients"], IngredientSerializer(ingredients, many=True).data)

    def test_create_ingredient_on_recipe_update(self):

        # create a recipe
        recipe = create_recipe(user=self.user)

        # add an ingredient to the recipe using the API
        payload = {"ingredients": [{"name": "Limes"}, ]}
        url = detail_url(recipe_id=recipe.id)
        response = self.client.patch(url, data=payload, format="json")

        # check the ingredient was added to the recipe
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_ingredient = Ingredient.objects.get(user=self.user, name="Limes")
        self.assertIn(new_ingredient, recipe.ingredients.all())

    def test_assigning_an_ingredient_on_recipe_update(self):

        # create a recipe with one ingredient
        recipe = create_recipe(user=self.user)
        ingredient_1 = Ingredient.objects.create(user=self.user, name="Pepper")
        recipe.ingredients.add(ingredient_1)

        # update the ingredients of the recipe using the API
        ingredient_2 = Ingredient.objects.create(user=self.user, name="Chili")
        payload = {"ingredients": [{"name": "Chili"}, ]}
        url = detail_url(recipe_id=recipe.id)
        response = self.client.patch(url, data=payload, format="json")

        # check the recipe ingredients were updated
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(ingredient_2, recipe.ingredients.all())
        self.assertNotIn(ingredient_1, recipe.ingredients.all())

    def test_clear_recipe_ingredients(self):
        
        # create a recipe with an ingredient
        ingredient = Ingredient.objects.create(user=self.user, name="Garlic")
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient)

        # delete the ingredient using the API
        payload = {"ingredients": []}
        url = detail_url(recipe_id=recipe.id)
        response = self.client.patch(url, data=payload, format="json")

        # check the ingredient was deleted
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)
