from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LogoutView
from indiego_news.views import(
    review_articles,
    approve_article,
    article_detail,
    homepage,
    register,
    profile_view,
    create_article,
    edit_article,
    delete_article,
    CustomLoginView,
    subscribe,
    author_articles,
    update_publisher,
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', homepage, name='home'),
    path('editor/review/', review_articles, name='review_articles'),
    path('editor/approve/<int:article_id>/', approve_article,
         name='approve_article'),
    path("articles/<int:pk>/<slug:slug>/", article_detail,
         name="article_detail"),
    path('register/', register, name='register'),
    path('profile/', profile_view, name='profile'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('create/', create_article, name='create_article'),
    path('articles/<int:article_id>/<slug:article_slug>/edit/',
         edit_article, name='edit_article'),
    path('articles/<int:article_id>/<slug:article_slug>/delete/',
         delete_article, name='delete_article'),
    path('subscribe/<int:id>/', subscribe, name='subscribe'),
    path('author/<int:author_id>/articles/', author_articles,
         name='author_articles'),
    path('update-publisher/', update_publisher, name='update_publisher'),
]
