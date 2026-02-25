from rest_framework import serializers
from .models import CustomUser, Publisher, Article, Subscription


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role']


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = ['id', 'name']


class ArticleSerializer(serializers.ModelSerializer):
    posted_by = serializers.StringRelatedField()
    reviewed = serializers.StringRelatedField()

    class Meta:
        model = Article
        fields = ['id', 'title', 'slug', 'content', 'approved', 'created_at',
                  'type', 'posted_by', 'reviewed']


class SubscriptionSerializer(serializers.ModelSerializer):
    subscriber = serializers.StringRelatedField()
    publisher = serializers.StringRelatedField()
    journalist = serializers.StringRelatedField()

    class Meta:
        model = Subscription
        fields = ['id', 'subscriber', 'publisher', 'journalist']
