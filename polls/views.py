"""Create Polls application view."""
import logging.config

from django.contrib import messages
from django.contrib.auth import user_logged_in, user_logged_out, user_login_failed
from django.contrib.auth.decorators import login_required
from django.dispatch import receiver
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from .models import Question, Choice, Vote
from .settings import LOGGING

logging.config.dictConfig(LOGGING)
logger = logging.getLogger('polls')


def get_client_ip(request):
    """Return client ip address."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@receiver(user_logged_in)
def user_logged_in_callback(sender, request, user, **kwargs):
    """Log the detail of user and ip address when user logged in."""
    logger.info(f'User {user.username} logged in from {get_client_ip(request)}')


@receiver(user_logged_out)
def user_logged_out_callback(sender, request, user, **kwargs):
    """Log the detail of user and ip address when user logged out."""
    logger.info(f'User {user.username} logged out from {get_client_ip(request)}')


@receiver(user_login_failed)
def user_login_failed_callback(sender, credentials, request, **kwargs):
    """Log the detail of user and ip address when user login failed."""
    logger.warning(f'User {request.POST["username"]} login failed from {get_client_ip(request)}')


def index(request):
    """View for polls index page.

    Return:
        Render HTML index page with context of all questions.
    """
    questions = Question.objects.all().order_by('-pub_date')
    return render(request, 'polls/index.html', {'questions': questions})


def detail(request, question_id):
    """View for polls detail page.

    Arguments:
        pk - primary key (id) of the question.
    Return:
        Render HTML detail page with context of selected question by id.
    """
    question = get_object_or_404(Question, pk=question_id)
    if not question.can_vote():
        messages.info(request, 'Voting is not allowed!')
        return redirect('polls:index')
    try:
        previous_choice = question.vote_set.get(user=request.user).choice
    except (KeyError, Vote.DoesNotExist):
        return render(request, 'polls/detail.html', {'question': question})
    return render(request, 'polls/detail.html', {'question': question, 'previous_choice': previous_choice})


def results(request, question_id):
    """Results page for the poll question.

    This page display all question choices and their votes.
    """
    question = Question.objects.get(pk=question_id)
    return render(request, 'polls/results.html', {'question': question})


@login_required()
def vote(request, question_id):
    """Vote for the selected choice in question.

    Arguments:
        question_id - is id of the question.
    Return:
        If the choice is valid, redirect to results page.
        If not, render the detail page.
    """
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        messages.error(request, "Please select one choice below for voting.")
        return render(request, 'polls/detail.html', {'question': question})
    else:
        if question.vote_set.filter(user=request.user).exists():
            this_vote = question.vote_set.get(user=request.user)
            this_vote.choice = selected_choice
            this_vote.save()
        else:
            selected_choice.vote_set.create(user=request.user, question=question)
        vote_again_url = reverse('polls:detail', args=(question_id,))
        vote_again_url_with_html = f'<a href="{vote_again_url}">here</a>'
        logger.info(f'User {request.user.username} voted for question id: {question.id} from {get_client_ip(request)}')
        messages.success(request, f'Vote successfully. Click {vote_again_url_with_html} to vote again.')
        return HttpResponseRedirect(reverse('polls:results', args=(question_id,)))
