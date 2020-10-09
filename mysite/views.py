"""Create view for KU Polls."""
from django.shortcuts import redirect


def index(request):
    """Landing page for KU Polls.

    Return:
        redirect to KU Polls index page.
    """
    return redirect('polls:index')
