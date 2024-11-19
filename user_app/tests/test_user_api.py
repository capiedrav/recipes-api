"""
Tests for the user API.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status



User = get_user_model()
TOKEN_URL = reverse("user:token")
CREATE_USER_URL = reverse("user:create")
ME_URL = reverse("user:me")

def create_user(**params):
    """
    Create and return a new user.
    """

    return User.objects.create_user(**params)


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
        self.assertNotIn("password", response.data) # check the password is not retrieved in the response

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

    def test_create_auth_token_for_user(self):
        
        # create a user in the database
        create_user(**self.payload)

        # make a POST request to the token url passing user credentials
        response = self.client.post(TOKEN_URL, data={
            "email":self.payload["email"], 
            "password": self.payload["password"]
            })
        
        # check a token is created
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

    def test_cant_create_auth_token_with_bad_credentials(self):
        """
        Test returns error if credentials invalid.
        """

        # create a user in the database
        create_user(**self.payload)

        # make a POST request to the token url passing bad credentials (incorrect password)
        response = self.client.post(TOKEN_URL, data={"email": self.payload["email"], "password": "badpass123"})

        # check that the token is not created
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", response.data)

    def test_cant_create_token_with_blank_password(self):
        """
        Test posting a blank password returns an error.
        """

        # create a user in the database
        create_user(**self.payload)

        # make a POST request to the token url passing bad credentials (blank password)
        response = self.client.post(TOKEN_URL, data={"email": self.payload["email"], "password": ""})

        # check that the token is not created
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", response.data)

    def test_user_authentication_is_required(self):
        """
        Test user auth is required to access "me" endpoint.
        """

        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """
    Test API requests that require authentication.
    """

    def setUp(self):
        
        self.user = create_user(email="testuser@example.com", password="testpass123", name="test user")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_auth_user_can_retrieve_his_profile(self):

        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            "name": self.user.name,
            "email": self.user.email
        })

    def test_auth_user_cant_POST_to_me_url(self):
        """
        Test can't make POST request to the "me" endpoint.
        """

        response = self.client.post(ME_URL, data={})

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
  
    def test_auth_user_can_update_his_profile(self):
        
        # update user info
        new_payload = {"name": "new name", "password": "newpass123"}         
        response = self.client.patch(ME_URL, data=new_payload)

        self.user.refresh_from_db() # get updated user info

        # check the new info was stored correctly
        self.assertEqual(self.user.name, new_payload["name"])
        self.assertTrue(self.user.check_password(new_payload["password"]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
