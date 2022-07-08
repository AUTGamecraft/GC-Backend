from django.contrib import admin

from game.models import Game, Comment, Like

# Register your models here.


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "timestamp", "is_verified")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "timestamp", "text")
@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "timestamp", "game")
