# shopping_app/serializers.py

from rest_framework import serializers
from .models import Store, Item, Review


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'name', 'seller']
        read_only_fields = ['seller']


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'store', 'name', 'description', 'price', 'image']


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'item', 'user', 'rating', 'comment']
