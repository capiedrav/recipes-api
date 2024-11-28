"""
Tests for the tags API.
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core_app.models import Tag
from recipe_app.serializers import TagSerializer

TAGS_URL = reverse("recipe_app:tag-list")
User = get_user_model()


class PublicTagsAPITests(TestCase):
    """
    Test unauthenticated API requests.
    """

    def setUp(self):

        self.client = APIClient()

    def test_authentication_required_for_retrieving_tags(self):

        response = self.client.get(TAGS_URL)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    
class PrivateTagsAPItests(TestCase):

    def setUp(self):

        self.user = self.create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user) 

    def create_user(self, email="testuser@example.com", password="testpass123"):
        """
        Create and return an user.
        """

        return User.objects.create_user(email=email, password=password)

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
        another_user = self.create_user(email="anotheruser@example.com")
        Tag.objects.create(user=another_user, name="Fruity")

        # create a tag for the authenticated user
        tag = Tag.objects.create(user=self.user, name="Comfort food")       
        
        # retrieve the tag
        response = self.client.get(TAGS_URL)

        # check that the retrieve tag belongs to the authenticated user
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0], TagSerializer(tag).data)
