from .models import Article, Subscription, Publisher
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.contrib.sites.models import Site
import logging
import tweepy

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Article)
def article_approved(sender, instance, created, **kwargs):
    """Function determines article/newsletter status,
    and then will send email to subscribers and tweet
    if article is approved."""

    if not instance.approved:
        if created:
            print("Article pending approval.")
        return

    if created:
        print("New Article Approved.")
    else:
        print("Article approved after creation.")

    try:
        domain = Site.objects.get_current().domain
    except:
        domain = "localhost:8000"

    article_url = (
        f"http://{domain}"
        f"{reverse('article_detail', args=[instance.pk, instance.slug])}"
    )

    try:
        auth = tweepy.OAuth1UserHandler(
            settings.TWITTER_API_KEY,
            settings.TWITTER_API_SECRET,
            settings.TWITTER_ACCESS_TOKEN,
            settings.TWITTER_ACCESS_SECRET,
        )
        api = tweepy.API(auth)
        tweet = (
            f"New article: {instance.title} by {instance.posted_by.username} "
            f"Read here: {article_url}"
        )
        api.update_status(tweet)
        print("Tweeted approved article.")
    except Exception as e:
        print(f"Twitter post failed: {e}")

    publishers = Publisher.objects.filter(journalists=instance.posted_by)
    sub_to_journalist = Subscription.objects.filter(
        journalist=instance.posted_by
        )
    sub_to_publisher = Subscription.objects.filter(
        publisher__in=publishers
        )

    emails = set()
    emails.update(sub.subscriber.email for sub in sub_to_journalist)
    emails.update(sub.subscriber.email for sub in sub_to_publisher)

    for email in emails:
        send_mail(
            subject=f"New Article: {instance.title}",
            message=f"{instance.title}\n{instance.content}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )
