# notes/forms.py
from django import forms
from .models import Note


class NoteForm(forms.ModelForm):
    """
    Form for creating and updating Note objects.
    Fields:
    - title: CharField for the nost title.
    - content: TextField for the nost content.
    Meta class:
    - Defines the model to use (Note) and the fields to include in the
    form.
    :param forms.ModelForm: Django's ModelForm class.
    """

    class Meta:
        model = Note
        fields = ["title", "content", "author"]
