from django.contrib import admin
from django.contrib.admin.filters import ListFilter
from .models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['postuserid', 'postusername', 'postmessage', 'poststatus', 'is_allowed']
    list_filter = ['postuserid', 'postusername', 'postmessage', 'poststatus', 'is_allowed']
