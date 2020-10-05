import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Question


# Create your tests here.


def create_question(question_text, pub, end):
    """
    Create a question with the given `question_text` and published the
    given number of `pub` and `end` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published)
    """
    pub_time = timezone.now() + datetime.timedelta(days=pub)
    end_time = timezone.now() + datetime.timedelta(days=end)
    return Question.objects.create(question_text=question_text, pub_date=pub_time, end_date=end_time)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['questions'], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        create_question(question_text="Past question.", pub=-30, end=-29)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['questions'],
            ['<Question: Past question.>']
        )

    def test_future_question(self):
        """
        Questions with a pub_date in the future are displayed on
        the index page, but can't vote on them.
        """
        future_question = create_question(question_text="Future question.", pub=30, end=31)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['questions'], ['<Question: Future question.>'])
        self.assertFalse(future_question.can_vote())

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, and future question
        can't vote yet. Both will be displayed.
        """
        create_question(question_text="Past question.", pub=-30, end=-29)
        create_question(question_text="Future question.", pub=30, end=31)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['questions'],
            ['<Question: Future question.>', '<Question: Past question.>']
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        create_question(question_text="Past question 1.", pub=-30, end=-29)
        create_question(question_text="Past question 2.", pub=-5, end=-4)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['questions'],
            ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )


class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

    def test_is_published_with_past_question(self):
        """
        is_published() returns True for question whose pub_date
        is in the paste.
        """
        time = timezone.now() - datetime.timedelta(days=5)
        past_question = Question(pub_date=time)
        self.assertIs(past_question.is_published(), True)

    def test_is_published_with_future_question(self):
        """
        is_published() returns False for question whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(hours=3)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.is_published(), False)

    def test_can_vote_with_past_question(self):
        """
        can_vote() returns False for question whose closed (pub_date
        and end_date are in the past).
        """
        time = timezone.now() - datetime.timedelta(days=3)
        end_time = timezone.now() - datetime.timedelta(days=1)
        past_question = Question(pub_date=time, end_date=end_time)
        self.assertIs(past_question.can_vote(), False)

    def test_can_vote_with_future_question(self):
        """
        can_vote() returns False for question whose not opened yet (pub_date
        and end_date are in the future).
        """
        time = timezone.now() + datetime.timedelta(days=1)
        end_time = timezone.now() + datetime.timedelta(days=3)
        future_question = Question(pub_date=time, end_date=end_time)
        self.assertIs(future_question.can_vote(), False)


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text='Future question.', pub=5, end=6)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date and end_date in the past
        which is closed, they will displayed the question's text.
        """
        past_question = create_question(question_text='Past Question.', pub=-5, end=-4)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
