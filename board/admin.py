from django.contrib import admin
from .models import *


class PostAdmin(admin.ModelAdmin):
    list_display = ('user', 'dateCreation', 'title', 'category')
    list_filter = ('user', 'dateCreation', 'category')
    search_fields = ('user', 'dateCreation', 'title', 'category')


class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'dateCreation', 'post', 'status')
    list_filter = ('user', 'dateCreation', 'post', 'status')
    search_fields = ('user', 'dateCreation', 'post', 'status')


admin.site.register(Post, PostAdmin)
admin.site.register(CommentPost, CommentAdmin)

