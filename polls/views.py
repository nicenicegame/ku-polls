"""Create Polls application view."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from .models import Question, Choice, Vote


# Create your views here.


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
    """Result view for polls. This page display all question choices and their votes."""
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
            selected_choice.vote_set.create(user=request.user)
        vote_again_url = reverse('polls:detail', args=(question_id,))
        vote_again_url_with_html = f'<a href="{vote_again_url}">here</a>'
        messages.success(request, f'Vote successfully. Click {vote_again_url_with_html} to vote again.')
        return HttpResponseRedirect(reverse('polls:results', args=(question_id,)))
