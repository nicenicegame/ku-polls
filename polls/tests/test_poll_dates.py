"""Model and poll dates tests."""
import datetime

from django.test import TestCase
from django.utils import timezone

from ..models import Question


class QuestionModelTests(TestCase):
    """Test case for Question model."""

    def test_was_published_recently_with_future_question(self):
        """was_published_recently() returns False for questions whose pub_date is in the future."""
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """was_published_recently() returns False for questions whose pub_date is older than 1 day."""
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """was_published_recently() returns True for questions whose pub_date is within the last day."""
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

    def test_is_published_with_past_question(self):
        """is_published() returns True for question whose pub_date is in the paste."""
        time = timezone.now() - datetime.timedelta(days=5)
        past_question = Question(pub_date=time)
        self.assertIs(past_question.is_published(), True)

    def test_is_published_with_future_question(self):
        """is_published() returns False for question whose pub_date is in the future."""
        time = timezone.now() + datetime.timedelta(hours=3)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.is_published(), False)

    def test_can_vote_with_past_question(self):
        """can_vote() returns False for question whose closed (pub_date and end_date are in the past)."""
        time = timezone.now() - datetime.timedelta(days=3)
        end_time = timezone.now() - datetime.timedelta(days=1)
        past_question = Question(pub_date=time, end_date=end_time)
        self.assertIs(past_question.can_vote(), False)

    def test_can_vote_with_future_question(self):
        """can_vote() returns False for question whose not opened yet (pub_date and end_date are in the future)."""
        time = timezone.now() + datetime.timedelta(days=1)
        end_time = timezone.now() + datetime.timedelta(days=3)
        future_question = Question(pub_date=time, end_date=end_time)
        self.assertIs(future_question.can_vote(), False)
