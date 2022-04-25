from django.contrib import admin

from game.models import Game, Comment

# Register your models here.


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "timestamp", "is_verified")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "timestamp", "text")
