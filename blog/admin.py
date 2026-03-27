from django.contrib import admin

from .models import Comment, Like, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "created_date", "likes_count")
    list_filter = ("created_date", "author")
    search_fields = ("title", "content", "author__username")
    raw_id_fields = ("author",)

    def likes_count(self, obj: Post) -> int:
        return obj.likes.count()

    likes_count.short_description = "Likes"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("content", "post", "author", "created_date")
    list_filter = ("created_date", "author")
    search_fields = ("content", "post__title", "author__username")
    raw_id_fields = ("post", "author")


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("post", "user", "created_date")
    list_filter = ("created_date", "user")
    search_fields = ("post__title", "user__username")
    raw_id_fields = ("post", "user")
