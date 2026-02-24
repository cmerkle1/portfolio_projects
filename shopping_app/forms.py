from django import forms
from .models import Item, Buyer, Review


class RegistrationForm(forms.Form):
    """Form that allows user to register as
    either buyer or seller.

    Fields:
    - username: CharField for username.
    - password: CharField for the password.
    - name: Charfield for username.
    - email: EmailField for the email address.
    - user_type: ChoiceField for the user type"""
    USER_TYPE_CHOICES = (
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
    )

    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    name = forms.CharField(max_length=255)
    email = forms.EmailField()
    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES)


class ProductForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ["name", "description", "price", "available", "image"]


class ReviewForm(forms.ModelForm):
    """Allows the user to post a review.
    If the user has purchased the item,
    they post verified. Otherwise,
    they post unverified.
    Fields:
    - rating: PositiveIntegerField for the rating 1-5
    - comment: TextField for the rating text
    - product: ForeignKey to access product
    - user: ForeignKey to access the buyer"""

    class Meta:
        model = Review
        fields = ["rating", "comment"]


class SendInvoice(forms.ModelForm):
    """Sends email to user after purchase
    Fields:
    - name: CharField for user's name
    - email: sends email to user"""

    class Meta:
        model = Buyer
        fields = ["name", "email"]
