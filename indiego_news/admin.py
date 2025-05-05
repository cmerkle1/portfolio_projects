from django.contrib import admin
from .models import Article, Publisher, Subscription, CustomUser
from django.apps import apps

admin.site.register(Article)
admin.site.register(Publisher)
admin.site.register(Subscription)
admin.site.register(CustomUser)

print("Registered models:", apps.get_models())
