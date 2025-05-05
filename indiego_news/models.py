from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.utils import timezone
from django.urls import reverse


class Publisher(models.Model):
    """Model representing the publishers
    involved in the article/newsletter. Names
    must be unique. Shows which editors and
    journalists the publisher manages if any.
    Fields:
    - name: Charfield representing user name
    - editors: ManyToManyField linking editors that are
    managed by the publisher
    - journalists: ManyToManyfield linking journalists
    that are managed by the publisher

    Methods:
    - __str__: Returns a string representation of the
    publisher's name."""

    name = models.CharField(max_length=150, unique=True)
    editors = models.ManyToManyField('CustomUser',
                                     related_name='editor_publishers',
                                     limit_choices_to={'role': 'editor'})
    journalists = models.ManyToManyField('CustomUser',
                                         related_name='journalist_publishers',
                                         limit_choices_to={'role': 'journalist'})

    def __str__(self):
        return self.name


class CustomUser(AbstractUser, models.Model):
    """Represents the user and their type. Each user
    can be either a reader, editor, or journalist.

    Fields:
    - role: Charfield that allows user to select their
    status as either reader, editor, or journalist.

    Methods:
    - __str__: Returns a string representation of the access
    status."""

    READER = "Reader"
    EDITOR = "Editor"
    JOURNALIST = "Journalist"

    ROLE_CHOICES = [
        (READER, 'Reader'),
        (EDITOR, 'Editor'),
        (JOURNALIST, 'Journalist'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    publisher = models.ForeignKey(
        Publisher, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='users'
        )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_reader(self):
        return self.role == self.READER

    @property
    def is_editor(self):
        return self.role == self.EDITOR

    @property
    def is_journalist(self):
        return self.role == self.JOURNALIST


class Article(models.Model):
    """Model representing a news article.
    Fields:
    - title: CharField representing article title
    - content: TextField representing the article
    body
    - approved: BooleanField representing if the
    article was approved by publisher or not
    - reviewed: ForeignKey accessing the reviewer
    of the article
    - posted_by: ForeignKey that determines who
    posted the article
    - slug: SlugField to generate keywords for emails

    Methods:
    - __str__: Returns a string representation of the approval
    status and article type.
    :param models.Model: Django's base model class."""

    ARTICLE = 'article'
    NEWSLETTER = 'newsletter'

    TYPE_CHOICES = [
        (ARTICLE, 'Article'),
        (NEWSLETTER, 'Newsletter'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField()
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    reviewed = models.ForeignKey(CustomUser, null=True, blank=True,
                                 on_delete=models.SET_NULL,
                                 related_name="reviewed_articles")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    posted_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="articles",
        null=True
        )

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Article.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('article_detail', args=[str(self.id), self.slug])

    def __str__(self):
        return (
            f"{self.get_type_display()} is "
            f"{'Approved' if self.approved else 'Pending'}"
            )


class Subscription(models.Model):
    """Model represents a relationship
    between a reader and their subscription.
    Fields:
    - subscriber: ForeignKey to access user
    access status
    - publisher: ForeignKey publisher details
    - journalist: ForeignKey for journalist details

    Methods
    def status(self): checks that user is reader and
    subscribed correctly.

    def __str__(self): return string with sub status"""

    subscriber = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                                   related_name='subscriptions_as_subscriber')
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE,
                                  blank=True, null=True)
    journalist = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                                   blank=True, null=True,
                                   related_name='subscriptions_as_journalist')

    def status(self):
        if self.subscriber.role != CustomUser.READER:
            raise ValidationError("Only Readers can subscribe.")

        if self.publisher and self.journalist:
            raise ValidationError("You can only subscribe to"
                                  " a publisher or journalist.")
        if not self.publisher and not self.journalist:
            raise ValidationError("You must subcribe to either"
                                  " a publisher or journalist.")

    def clean(self):
        self.status()

    def __str__(self):
        if self.publisher:
            return (
                f"{self.subscriber.username} subscribed "
                f"to {self.publisher.name}."
            )
        return (
            f"{self.subscriber.username} subscribed "
            f"to {self.journalist.username}."
        )
