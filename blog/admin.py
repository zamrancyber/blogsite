from django.contrib import admin
from .models import Post, Comment

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'date_posted', 'image_preview')
    list_filter = ('status', 'author', 'date_posted')
    search_fields = ('title', 'content')
    readonly_fields = ('date_posted',)
    actions = ['approve_posts']

    def approve_posts(self, request, queryset):
        queryset.update(status='published')
    approve_posts.short_description = "Approve selected posts (set status to Published)"

    def image_preview(self, obj):
        if obj.image:
            from django.utils.html import mark_safe
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" />')
        return 'No image'
    image_preview.short_description = 'Image'

class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'post', 'created', 'active')
    list_filter = ('active', 'created')
    search_fields = ('name', 'email', 'body')
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(active=True)
    approve_comments.short_description = "Approve selected comments"

admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)