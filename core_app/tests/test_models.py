"""
Tests for models.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model


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

        User = get_user_model()
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

        User = get_user_model()
        for email, expected in sample_emails:
            user = User.objects.create_user(email=email, password="testpass123")

            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_ValueError(self):
        """
        Test that creating a user without an email raises a ValueError.
        """

        User = get_user_model()

        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="testpass123")

