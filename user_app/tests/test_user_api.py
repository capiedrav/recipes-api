"""
Tests for the user API.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse("user:create")
User = get_user_model()

def create_user(**params):
    """
    Create and return a new user.
    """

    User.objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """
    Test the public features of the user API.
    """

    def setUp(self):
        
        self.client = APIClient()
        self.payload = {
            "email": "test_user@example.com",
            "password": "testpass123",
            "name": "test user"
        }


    def test_create_user(self):
        """
        Test creating a user is successful.
        """
        
        # make a POST request to the create user endpoint passing user info
        response = self.client.post(CREATE_USER_URL, self.payload) 
        
        # check the user is created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # retrieve the user from the database
        user = User.objects.get(email=self.payload["email"])
        
        self.assertTrue(user.check_password(self.payload["password"])) # check the password is correct
        self.assertNotIn("password", response.data) # check the password is not a retrieved in the response

    def test_user_email_already_exists_returns_error(self):
        """
        Test error is returned if user email already exists.
        """

        # create a user
        create_user(**self.payload)

        # create the same user through the create user endpoint
        response  = self.client.post(CREATE_USER_URL, self.payload)

        # check that the request fails
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_password_too_short_returns_error(self):
        """
        Test error is return if user password is less than 5 chars.
        """

        self.payload["password"] = "pw" # short password

        # create the the user with a short password
        response = self.client.post(CREATE_USER_URL, self.payload)

        # check the request fails
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)
