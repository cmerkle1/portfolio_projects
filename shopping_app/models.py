from django.db import models
from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from rest_framework import serializers


class Seller(models.Model):
    """Model representing the seller for the storefront.
    Fields:
    - name: CharField for the sellers's name.
    - user: OnetoOneField to connect seller to user

    Methods:
    - __str__: Returns a string representation of the seller, showing the
    name.
    :param models.Model: Django's base model class."""

    name = models.CharField(max_length=255)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Buyer(models.Model):
    """Model representing the buyer for the storefront.
    Fields:
    user: ForeignKey for user
    name: CharField for the buyer's name.
    email: EmailField for buyer's email.

    Methods:
    - __str__: Returns a string representation of the buyer,
    showing their name
    :param models.Model: Django's base model class."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)

    def __str__(self):
        return self.name


class Store(models.Model):
    """Represents the storefront for sellers.
    - listed_on: DateTimeField displays the items list date
    - seller: CharField displays user name
    - name: CharField for store name

    Methods:
    - __str__: Returns a string representation of the items listed.
    :param models.Model: Django's base model class."""

    seller = models.OneToOneField(Seller, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, default="Unnamed Store")
    listed_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Store by {self.seller.name}"


class Item(models.Model):
    """Represents the items for the storefronts.
    - name: CharField shows the name of the item
    - description: TextField describes the item
    - price: DecimalField displays the item price to 2 digits
    - available: BooleanField shows availability
    - image: ImageField to show item

    Relationships:
    - store: ForeignKey representing the store the items belong to

    Methods:
    - __str__: Returns a string representation of the item name.
    :param models.Model: Django's base model class."""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)
    image = models.ImageField(upload_to="item_images/", blank=True, null=True)
    store = models.ForeignKey("Store", on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Cart(models.Model):
    """Represents the buyers cart to hold items.

    Relationships
    buyer: ForeignKey representing the user owning the cart

    Methods:
    - __str__(self): returns the cart owner's name"""
    buyer = models.ForeignKey(
      "Buyer", on_delete=models.CASCADE)

    def __str__(self):
        return f"Cart for {self.buyer}"


class CartItem(models.Model):
    """Represents all items in the cart and quantities
    - quantity: PositiveIntegerField representing the number of items available
    - cart: ForeignKey representing the cart object
    - item: ForeignKey representing items for the cart

    Methods:
    - __str__(self): returns quantity of each item"""
    quantity = models.PositiveIntegerField(default=1)
    cart = models.ForeignKey(
        "Cart", on_delete=models.CASCADE, related_name="cart_items")
    item = models.ForeignKey("Item", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.quantity} x {self.item.name}"


class Review(models.Model):
    """Model representing the Review for items.
    Fields:
    - buyer: ForeignKey for the sellers's name.
    - rating: IntegerField to select rating 1-5
    - comment: TextField for comment about item
    - verified: BooleanField displays user's purchase status
    - created_at: DateTimeField to show when review was left

    Methods:
    - __str__: Returns a string representation of the buyer name
    and their review status."""
    item = models.ForeignKey(Item, on_delete=models.CASCADE,
                             related_name="reviews")
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.buyer} for {self.item}"


class Order(models.Model):
    """Model representing the seller for the storefront.
    Fields:
    - buyer: ForeignKey representing the buyer
    - items: ManyToManyFields displaying all items in order
    - created_at: shows the time of purchase
    - total_price: DecimalField for total purchase price
    - status: CharField for order status, may not use this at end

    Methods:
    - __str__: Returns a string representation of order number and buyer"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped')
    ]
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE)
    items = models.ManyToManyField(Item, through="OrderItem")
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES,
                              default='pending')

    def __str__(self):
        return f"Order {self.id} by {self.buyer.name}"


class OrderItem(models.Model):
    order = models.ForeignKey("Order", on_delete=models.CASCADE)
    item = models.ForeignKey("Item", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.item.name}"


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']

    rating = forms.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        widget=forms.NumberInput(attrs={'min': 1, 'max': 5})
    )


class RegistrationForm(forms.ModelForm):
    """Registration form for new users with user type and name."""
    user_type = forms.ChoiceField(choices=[('buyer', 'Buyer'),
                                           ('seller', 'Seller')])
    name = forms.CharField(max_length=255)
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password', 'email']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.set_password(self.cleaned_data['password'])
            user.save()
        return user


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'description', 'price', 'image']


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'name', 'seller']
        read_only_fields = ['seller']
