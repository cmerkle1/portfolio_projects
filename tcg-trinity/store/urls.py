from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),               # homepage
    path('events/', views.events, name='events'),    # events page
    path('store/', views.product_list, name='product_list'),  # store page
    path('open_play/', views.open_play, name='open_play'), # open play page
    path('contact/', views.contact, name='contact'), #contact page
]
