"""
Tests for the tags API.
"""
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core_app.models import Tag, Recipe
from recipe_app.serializers import TagSerializer


TAGS_URL = reverse("recipe_app:tag-list")
User = get_user_model()


def detail_iur(tag_id):
    """
    Create and return a tag detail url.
    """

    return reverse("recipe_app:tag-detail", args=[tag_id, ])

def create_user(email="testuser@example.com", password="testpass123"):
        """
        Create and return an user.
        """

        return User.objects.create_user(email=email, password=password)


class PublicTagsAPITests(TestCase):
    """
    Test unauthenticated API requests.
    """

    def setUp(self):

        self.client = APIClient()
        

    def test_authentication_required_for_retrieving_tags(self):

        response = self.client.get(TAGS_URL)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authentication_required_to_create_tags(self):

        user = create_user()

        response = self.client.post(TAGS_URL, data={"user": user, "name": "Dessert"})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    
class PrivateTagsAPITests(TestCase):

    def setUp(self):

        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)    

    def test_create_tag(self):

        # create a tag through a POST request
        response = self.client.post(TAGS_URL, data={"name": "Dessert"})

        # check the tag was created successfully
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Tag.objects.count(), 1)
        tag = Tag.objects.first()
        self.assertEqual(response.data, TagSerializer(tag).data)

    def test_retrieve_tags(self):
           
        # create two tags
        Tag.objects.create(user=self.user, name="Vegan")
        Tag.objects.create(user=self.user, name="Dessert")

        # retrieve the tags
        response = self.client.get(TAGS_URL)

        # check that the tags were created successfully
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        tags = Tag.objects.all().order_by("-name")
        self.assertEqual(response.data, TagSerializer(tags, many=True).data)

    def test_tags_retrieved_are_limited_to_the_auth_user(self):

        # create another user and associate a tag to him
        another_user = create_user(email="anotheruser@example.com")
        Tag.objects.create(user=another_user, name="Fruity")

        # create a tag for the authenticated user
        tag = Tag.objects.create(user=self.user, name="Comfort food")       
        
        # retrieve the tag
        response = self.client.get(TAGS_URL)

        # check that the retrieve tag belongs to the authenticated user
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0], TagSerializer(tag).data)

    def test_update_tag(self):

        # create a tag in the database
        tag = Tag.objects.create(user=self.user, name="After Dinner")

        # update the tag through a PATCH request
        payload = {"name": "Dessert"}
        url = detail_iur(tag_id=tag.id)
        response = self.client.patch(url, payload)

        # check the tag was updated
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload["name"])

    def test_delete_tag(self):

        # create a tag in the database
        tag = Tag.objects.create(user=self.user, name="After Dinner")

        # delete the tag through a DELETE request
        url = detail_iur(tag_id=tag.id)
        response  = self.client.delete(url)

        # check the tag was deleted
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Tag.objects.count(), 0)

    def test_filter_tags_by_those_assigned_to_recipes(self):
        
        # create a recipe with a tag
        tag1 = Tag.objects.create(user=self.user, name="Breakfast")
        recipe = Recipe.objects.create(
            title="Green Eggs on Toast", 
            time_minutes=20,
            price=Decimal("2.50"),
            user=self.user            
        )
        recipe.tags.add(tag1)

        # create another tag (not assigned to any recipe)
        tag2 = Tag.objects.create(user=self.user, name="Lunch")

        # request tags assigned to recipes
        response = self.client.get(TAGS_URL, data={"assigned_only": 1})

        # check that only tags assigned to recipes were retrieved
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(TagSerializer(tag1).data, response.data)
        self.assertNotIn(TagSerializer(tag2).data, response.data)

    def test_filtered_tags_are_unique(self):

        # create to recipes with the same tag
        tag1 = Tag.objects.create(user=self.user, name="Breakfast")
        recipe1 = Recipe.objects.create(
            title="Pancakes",
            time_minutes=5,
            price=Decimal("2.00"),
            user=self.user
        )
        recipe2 = Recipe.objects.create(
            title="Porridge",
            time_minutes=3,
            price=Decimal("2.20"),
            user=self.user
        )
        recipe1.tags.add(tag1)
        recipe2.tags.add(tag1)

        # create another tag (not assigned to any recipe)
        tag2 = Tag.objects.create(user=self.user, name="Dinner")

        # request tags assigned to recipes
        response = self.client.get(TAGS_URL, data={"assigned_only": 1})

        # check that the tag retrieved is not duplicated
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0], TagSerializer(tag1).data)

