"""Create models for KU Polls."""
import datetime

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


# Create your models here.


class Question(models.Model):
    """Question model for KU Polls.

    Question model with question text, publication date, end date.
    """

    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    end_date = models.DateTimeField('ending date')

    def __str__(self):
        """Return question text."""
        return self.question_text

    def was_published_recently(self):
        """Return true if the question was published not more than 1 day."""
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    def is_published(self):
        """Return true if question is published."""
        return timezone.now() >= self.pub_date

    def can_vote(self):
        """Return ture if question can vote."""
        return self.end_date >= timezone.now() >= self.pub_date

    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'
    is_published.admin_order_field = 'pub_date'
    is_published.boolean = True
    is_published.short_description = 'Published?'
    can_vote.admin_order_field = 'pub_date'
    can_vote.boolean = True
    can_vote.short_description = 'Can vote?'


class Choice(models.Model):
    """Choice model for KU Polls.

    Choice with it own question, choice text, and their votes.
    """

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)

    def __str__(self):
        """Return choice text."""
        return self.choice_text

    @property
    def votes(self):
        return self.question.vote_set.filter(choice=self).count()


class Vote(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, default=0)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE, default=0)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        default=0)
