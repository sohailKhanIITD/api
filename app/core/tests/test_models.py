"""
tests for models
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

class ModelTests(TestCase):
    """test Models"""

    def test_create_user_with_email_successful(self):
        """test creating a user with email address"""
        email = 'test@example.com'
        password = '123456'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(email, user.email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized"""
        samples_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
        ]
        for email, expected in samples_emails:
            user = get_user_model().objects.create_user(email, '123456')
            self.assertEqual(user.email, expected)
    
    def test_new_user_without_email_raises_error(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')
    
    def test_create_superuser(self):
        """test creating a superuser"""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            '123456'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
