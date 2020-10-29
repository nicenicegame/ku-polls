from django.contrib.auth.models import User
from django.test import TestCase
from django.shortcuts import reverse


class AuthenticationTest(TestCase):
    """Test cases for authentication system."""

    def setUp(self):
        """Initialize the user."""
        self.user = {
            'username': 'nice',
            'password': 'ha159357'
        }
        User.objects.create_user(**self.user)

    def test_user_logged_in(self):
        """Test user logged in, the user username should display on the index page."""
        response = self.client.post(reverse('login'), self.user)
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('polls:index'))
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertContains(response, f'Hello {self.user["username"]}')

    def test_user_logged_out(self):
        """Test logged out, the user username will be not shown on the index page."""
        self.client.post(reverse('login'), self.user)
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertNotContains(response, f'Hello {self.user["username"]}')
