from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('events/', views.events, name='events'),
    path('menu/', views.menu, name='menu'),
    path('newsletter/', views.newsletter_signup, name='newsletter_signup'),

]
