"""Create custom admin page."""
from django.contrib import admin

from .models import Question, Choice


# Register your models here.


class ChoiceInline(admin.TabularInline):
    """Can add choice in question with default 3 fields."""

    model = Choice
    extra = 3


class QuestionAdmin(admin.ModelAdmin):
    """Custom question fields in admin page."""

    fieldsets = [
        (None, {'fields': ['question_text']}),
        ('Date information', {'fields': ['pub_date', 'end_date'], 'classes': ['collapse']})
    ]
    inlines = [ChoiceInline]
    list_display = ('question_text', 'pub_date', 'was_published_recently', 'is_published', 'can_vote')
    list_filter = ['pub_date']
    search_fields = ['question_text']


admin.site.register(Question, QuestionAdmin)
