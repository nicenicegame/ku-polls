"""Index page tests."""
import datetime

from django.shortcuts import reverse
from django.test import TestCase
from django.utils import timezone

from ..models import Question


def create_question(question_text, pub, end):
    """Create question with publication date and end date.

    `pub` and `end` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    pub_time = timezone.now() + datetime.timedelta(days=pub)
    end_time = timezone.now() + datetime.timedelta(days=end)
    return Question.objects.create(question_text=question_text, pub_date=pub_time, end_date=end_time)


class QuestionIndexViewTests(TestCase):
    """Test cases for index view."""

    def test_no_questions(self):
        """If no questions exist, an appropriate message is displayed."""
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['questions'], [])

    def test_past_question(self):
        """Questions with a pub_date in the past are displayed on the index page."""
        create_question(question_text="Past question.", pub=-30, end=-29)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['questions'],
            ['<Question: Past question.>']
        )

    def test_future_question(self):
        """Questions with a pub_date in the future are displayed on the index page, but can't vote on them."""
        future_question = create_question(question_text="Future question.", pub=30, end=31)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['questions'], ['<Question: Future question.>'])
        self.assertFalse(future_question.can_vote())

    def test_future_question_and_past_question(self):
        """Even if both past and future questions exist, and future question can't vote yet. Both will be displayed."""
        create_question(question_text="Past question.", pub=-30, end=-29)
        create_question(question_text="Future question.", pub=30, end=31)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['questions'],
            ['<Question: Future question.>', '<Question: Past question.>']
        )

    def test_two_past_questions(self):
        """The questions index page may display multiple questions."""
        create_question(question_text="Past question 1.", pub=-30, end=-29)
        create_question(question_text="Past question 2.", pub=-5, end=-4)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['questions'],
            ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )
