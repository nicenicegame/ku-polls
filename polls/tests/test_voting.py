"""Voting tests."""
import datetime

from django.contrib.auth.models import User
from django.shortcuts import reverse
from django.test import TestCase
from django.utils import timezone

from ..models import Question


class VotingTest(TestCase):
    """Test cases for voting the polls."""

    def setUp(self):
        """Initialize logged in user and the question with choices."""
        self.question = Question.objects.create(
            question_text='Test question',
            pub_date=timezone.now(),
            end_date=timezone.now() + datetime.timedelta(days=3)
        )
        for i in range(3):
            self.question.choice_set.create(choice_text=f'Test choice {i}')
        self.user = {
            'username': 'nicenicegame',
            'password': 'ha159357'
        }
        User.objects.create_user(**self.user)
        self.client.post(reverse('login'), self.user)

    def test_authenticated_voting(self):
        """The authenticated user can vote for the polls."""
        response = self.client.get(reverse('polls:index'))
        self.assertTrue(response.context['user'].is_active)
        self.client.post(reverse('polls:vote', args=(self.question.id,)), {'choice': 1})
        self.assertTrue(self.question.vote_set.filter(question=self.question).exists)

    def test_not_authenticated_voting(self):
        """The vote will be restrict for unauthenticated user."""
        self.client.post(reverse('logout'))
        response = self.client.get(reverse('polls:index'))
        self.assertFalse(response.context['user'].is_active)
        response = self.client.post(reverse('polls:vote', args=(self.question.id,)), {'choice': 1})
        self.assertEqual(response.status_code, 302)
