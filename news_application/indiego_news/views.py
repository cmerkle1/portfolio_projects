from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from .forms import CustomUserCreationForm, ArticleForm
from .models import Article, Subscription, CustomUser, Publisher
import tweepy
from decouple import config
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer, PublisherSerializer, ArticleSerializer, SubscriptionSerializer
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


def is_editor(user):
    """A user is an editor if they are both
    logged in and registered as editor."""
    return user.is_authenticated and user.role == 'editor'


def review_articles(request):
    """Fetches articles that are pending approval
    by the editor"""
    articles = Article.objects.filter(approved=False)
    return render(request, 'review_articles.html', {'articles': articles})


def approve_article(request, article_id):
    """Gets article to approve, or redirect to
    home if already approved. Calls post_to_Twitter and
    redirect to profile to continue reviews"""
    article = get_object_or_404(Article, id=article_id)

    if article.approved:
        return redirect('profile')

    if request.method == 'POST':
        article.approved = True
        article.reviewed_by = request.user
        article.save()

        post_to_twitter(article)

        return redirect('review_articles')

    return render(request, 'indiego_news/approve_article.html',
                  {'article': article})


def post_to_twitter(article):
    """Posts a line to Twitter with a link to the
    article url."""
    client = tweepy.Client(
        consumer_key=config('TWITTER_API_KEY'),
        consumer_secret=config('TWITTER_API_SECRET'),
        access_token=config('TWITTER_ACCESS_TOKEN'),
        access_token_secret=config('TWITTER_ACCESS_SECRET')
    )

    tweet_content = (
        f"Check out this article: "
        f"{article.title}\n{article.get_absolute_url()}"
    )

    try:
        client.create_tweet(text=tweet_content)
        print("Article posted to Twitter/X successfully!")
    except tweepy.TweepyException as e:
        print(f"Error posting to Twitter/X: {e}")


def article_detail(request, pk, slug):
    """Allows access to approved articles
    so readers can view on homepage. Also
    allows access to journalist author"""
    article = get_object_or_404(Article, pk=pk, slug=slug)

    if article.approved:
        return render(request, 'indiego_news/article_detail.html',
                      {'article': article})

    if request.user.is_authenticated and request.user == article.posted_by:
        return render(request, 'indiego_news/article_detail.html',
                      {'article': article})

    if not article.approved and not request.user.is_staff:
        return render(request, '403.html', status=403)

    return render(request, 'article_detail.html', {'article': article})


def homepage(request):
    """View to display the homepage with articles
    filtered and sorted by JOURNALIST."""

    # 1. Fetch all users who are marked as Journalists
    journalists = CustomUser.objects.filter(role=CustomUser.JOURNALIST)

    selected_journalist_id = request.GET.get('journalist')

    try:
        selected_journalist_id = int(selected_journalist_id)
    except (TypeError, ValueError):
        selected_journalist_id = None

    articles = Article.objects.filter(approved=True)

    if selected_journalist_id:
        articles = articles.filter(posted_by__id=selected_journalist_id)

    articles = articles.order_by('-created_at')

    return render(request, 'home.html', {
        'articles': articles,
        'journalists': journalists,  # Sending the list of journalists
        'selected_journalist_id': selected_journalist_id
    })


def register(request):
    """Leads user to a sign up form to collect
    email, name, password, and role"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile')
        else:
            print("Form errors:", form.errors)
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def profile_view(request):
    """Takes the user to their profile view
    based on their role."""
    user = request.user
    role = user.role.lower()
    context = {}

    if role == 'reader':
        subscriptions = Subscription.objects.filter(subscriber=user)
        context['subscriptions'] = subscriptions
        template = 'profiles/reader.html'

    elif role == 'editor':
        pending_articles = Article.objects.filter(approved=False)
        context['pending_articles'] = pending_articles
        template = 'profiles/editor.html'

    elif role == 'journalist':
        my_articles = Article.objects.filter(posted_by=user)
        context['my_articles'] = my_articles
        template = 'profiles/journalist.html'

    return render(request, template, context)


@login_required
def create_article(request):
    if (not request.user.is_authenticated or
       request.user.role != CustomUser.JOURNALIST):
        return redirect('profile')

    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.posted_by = request.user
            article.status = 'submitted'
            article.save()
            return redirect('profile')
    else:
        form = ArticleForm()

    return render(request, 'create_article.html', {'form': form})


@login_required
def edit_article(request, article_id, article_slug):
    article = get_object_or_404(Article, pk=article_id, slug=article_slug)

    if (request.user.role == CustomUser.JOURNALIST and
       article.posted_by != request.user):
        return redirect('profile')
    elif request.user.role not in [CustomUser.JOURNALIST, CustomUser.EDITOR]:
        return redirect('profile')

    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            article = form.save(commit=False)
            if (request.user.role == CustomUser.EDITOR and
               'approve' in request.POST):
                article.approved = True
                article.reviewed = request.user
            article.save()
            return redirect('profile')
    else:
        form = ArticleForm(instance=article)

    return render(request, 'indiego_news/edit_article.html', {
        'form': form,
        'article': article,
        'is_editor': request.user.role == CustomUser.EDITOR
    })


def delete_article(request, article_id, article_slug):
    article = get_object_or_404(Article, pk=article_id, slug=article_slug)

    if request.user != article.posted_by and request.user.role != CustomUser.EDITOR:
        return redirect('profile')

    if request.method == 'POST':
        article.delete()
        return redirect('profile')

    return render(
          request, 'indiego_news/confirm_delete.html',
          {'article': article}
          )


@method_decorator(csrf_exempt, name='dispatch')
class CustomLoginView(LoginView):
    template_name = 'login.html'
    authentication_form = AuthenticationForm

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        print(f"Redirecting {user.username} with role {user.role} to /profile/")
        return redirect('profile')

    def form_invalid(self, form):
        print("LOGIN FAILED")
        print(form.errors)
        return super().form_invalid(form)

    def get_redirect_url(self):
        return None

    def get_success_url(self):
        user = self.request.user
        if user.role == 'editor':
            return '/profile/'
        elif user.role == 'journalist':
            return '/profile/'
        elif user.role == 'reader':
            return '/profile/'
        return '/'


class CustomLogoutView(LogoutView):
    next_page = 'home'
    http_method_names = ['get', 'head', 'options']


def subscribe(request, id):
    if not request.user.is_authenticated:
        return redirect('login')

    target = get_object_or_404(CustomUser, id=id)

    if request.user.role != CustomUser.READER:
        return HttpResponse("Only readers can subscribe.", status=403)

    if Subscription.objects.filter(subscriber=request.user, journalist=target).exists():
        return HttpResponse("You're already subscribed.", status=400)

    Subscription.objects.create(subscriber=request.user, journalist=target)

    return redirect('home')


def author_articles(request, author_id):
    author = CustomUser.objects.filter(id=author_id, role=CustomUser.JOURNALIST).first()

    if author:
        articles = Article.objects.filter(posted_by=author, approved=True)
        author_name = author.username
    else:
        publisher = get_object_or_404(Publisher, id=author_id)
        journalists = publisher.journalists.all()
        articles = Article.objects.filter(posted_by__in=journalists, approved=True)
        author_name = publisher.name

    return render(request, 'author_articles.html', {
        'articles': articles,
        'author_name': author_name,
    })


class PublisherSelectionForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['publisher']
        widgets = {
            'publisher': forms.Select(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.get('instance')
        super().__init__(*args, **kwargs)

        if user and user.role == CustomUser.EDITOR:
            self.fields['publisher'].queryset = Publisher.objects.filter(editors=user)
        elif user and user.role == CustomUser.JOURNALIST:
            self.fields['publisher'].queryset = Publisher.objects.filter(journalists=user)
        else:
            self.fields['publisher'].queryset = Publisher.objects.none()


@login_required
def update_publisher(request):
    user = request.user

    if user.role not in [CustomUser.EDITOR, CustomUser.JOURNALIST]:
        return HttpResponse("Only editors or journalists can set a publisher.", status=403)

    if request.method == 'POST':
        form = PublisherSelectionForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = PublisherSelectionForm(instance=user)

    return render(request, 'profiles/update_publisher.html', {'form': form})


class PublisherViewSet(viewsets.ModelViewSet):
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer
    permission_classes = [IsAuthenticated]


class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]


class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_get_articles(request, journalist_id=None, publisher_id=None):
    if journalist_id:
        articles = Article.objects.filter(journalist_id=journalist_id)
    elif publisher_id:
        articles = Article.objects.filter(publisher_id=publisher_id)
    else:
        return Response({"detail": "Either journalist_id or publisher_id must be provided."},
                        status=status.HTTP_400_BAD_REQUEST)

    serializer = ArticleSerializer(articles, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_subscribe(request):
    user = request.user
    journalist_id = request.data.get('journalist_id')
    publisher_id = request.data.get('publisher_id')

    if not journalist_id and not publisher_id:
        return Response({"detail": "Either journalist_id or publisher_id must be provided."},
                        status=status.HTTP_400_BAD_REQUEST)

    if journalist_id:
        journalist = get_object_or_404(CustomUser, id=journalist_id, role='journalist')
        if Subscription.objects.filter(subscriber=user, journalist=journalist).exists():
            return Response({"detail": "Already subscribed to this journalist."},
                            status=status.HTTP_400_BAD_REQUEST)
        Subscription.objects.create(subscriber=user, journalist=journalist)
    elif publisher_id:
        publisher = get_object_or_404(Publisher, id=publisher_id)
        if Subscription.objects.filter(subscriber=user, publisher=publisher).exists():
            return Response({"detail": "Already subscribed to this publisher."},
                            status=status.HTTP_400_BAD_REQUEST)
        Subscription.objects.create(subscriber=user, publisher=publisher)

    return Response({"detail": "Subscribed successfully!"}, status=status.HTTP_201_CREATED)