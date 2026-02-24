from django.contrib import admin
from .models import Seller, Buyer, Store, Item, Cart, CartItem, Review

# Register your models here.
admin.site.register(Seller)
admin.site.register(Buyer)
admin.site.register(Store)
admin.site.register(Item)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Review)
