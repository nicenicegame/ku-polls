"""Detail page tests."""
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


class QuestionDetailViewTests(TestCase):
    """Test case for detail view."""

    def test_future_question(self):
        """The detail view of a question with a pub_date in the future returns a 404 not found."""
        future_question = create_question(question_text='Future question.', pub=5, end=6)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_past_question(self):
        """The detail view of a question in the past which is closed, they will displayed the question's text."""
        past_question = create_question(question_text='Past Question.', pub=-5, end=-4)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
