from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework import status
from django.test import TestCase
from .models import Publisher, Article, Subscription


class PublisherAPITests(TestCase):
    def setUp(self):
        """Tests that the API works to GET list
        of all publishers in db"""
        self.user = get_user_model().objects.create_user(username='testuser',
                                                         password='password123')
        self.client = APIClient()
        self.client.login(username='testuser', password='password123')

        self.publisher = Publisher.objects.create(name='Test Publisher')

    def test_publisher_list(self):
        response = self.client.get('/api/publishers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Test Publisher', response.content.decode())


class ArticleAPITests(TestCase):
    """Tests that articles can be retrieved
    with a GET request to article endpoint"""
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser',
                                                         password='password123')
        self.client = APIClient()
        self.client.login(username='testuser', password='password123')

        self.article = Article.objects.create(
            title='Test Article',
            content='This is a test article!',
            type=Article.ARTICLE,
            posted_by=self.user
        )

    def test_article_list(self):
        response = self.client.get('/api/articles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Test Article', response.content.decode())


class SubscriptionAPITests(TestCase):
    """Verifies that GET request will return
    list of subscriptions to a user"""
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser',
                                                         password='password123')
        self.client = APIClient()
        self.client.login(username='testuser', password='password123')

        self.publisher = Publisher.objects.create(name="Test Publisher")
        self.subscription = Subscription.objects.create(
            subscriber=self.user,
            publisher=self.publisher
        )

    def test_subscription_list(self):
        response = self.client.get('/api/subscriptions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Test Publisher', response.content.decode())
