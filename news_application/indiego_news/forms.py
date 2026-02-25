from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Article


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'role')


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        type = forms.ChoiceField(choices=Article.TYPE_CHOICES,
                                 label="Article Type")

        fields = ['title', 'content', 'type']
