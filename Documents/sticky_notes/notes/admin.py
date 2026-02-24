# notes/admin.py
from django.contrib import admin
from .models import Note
from .models import Author

# Post model
admin.site.register(Note)

# Author model
admin.site.register(Author)
