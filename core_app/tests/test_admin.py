"""
Tests for the Django admin modifications.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client


class AdminSiteTests(TestCase):
    """
    Tests for Django admin site.
    """

    def setUp(self):
        """
        Create superuser and user.
        """
        
        User = get_user_model()
        
        self.client = Client()
        self.admin_user = User.objects.create_superuser(email="admin@example.com", password="testpass123")
        self.client.force_login(self.admin_user) # log in the admin user

        self.user = User.objects.create_user(email="user@example.com", password="testpass123", name="test user")

    def test_users_are_listed_on_admin_changelist(self):
        """
        Test that users are listed on admin changelist page.
        """

        url = reverse("admin:core_app_user_changelist") # get changelist page url

        response = self.client.get(url) # make GET request to changelist url

        # check the names of the users are listed on the changelist page
        self.assertContains(response, self.user.name)
        self.assertContains(response, self.user.email)
        self.assertContains(response, self.admin_user.name)
        self.assertContains(response, self.admin_user.email)

    def test_edit_user_page_works(self):

        url  = reverse("admin:core_app_user_change", args=[self.user.id, ]) # get change user url

        response = self.client.get(url) # make GET request to change user url
 
        self.assertEqual(response.status_code, 200) # check the page works

    def test_create_user_page_works(self):

        url = reverse("admin:core_app_user_add")

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200) # check the page works

