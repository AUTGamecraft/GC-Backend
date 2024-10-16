from django.contrib import admin
from django.http import JsonResponse
from excel_response import ExcelResponse

from game.models import Game, Comment, Like


# Register your models here.


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    def export_games(self, request, queryset):
        data = []
        headers = ['title', 'team', 'game_link', 'timestamp', 'is_verified', 'members']
        data.append(headers)

        for game in queryset.all():
            members = ""
            for member in game.team.members.all():
                members += member.first_name + ", "

            data.append([game.title, game.team.name, game.game_link, game.timestamp, game.is_verified, members])

        if not data:
            return JsonResponse({"message": "Nothing Found"})
        else:
            return ExcelResponse(data=data, worksheet_name="games", output_filename="games")

    def export_likes(self, request, queryset):
        data = []
        headers = ['game', 'liker_name', 'liker_email', 'timestamp']
        data.append(headers)

        for game in queryset.all():
            for like in game.likes.all():
                data.append([game.title, like.user.first_name, like.user.email, like.timestamp])

        if not data:
            return JsonResponse({"message": "Nothing Found"})
        else:
            return ExcelResponse(data=data, worksheet_name="likes", output_filename="games")

    actions = ['export_games', 'export_likes']
    export_games.short_description = 'Export Games'
    export_likes.short_description = 'Export Likes'
    actions_on_top = True

    search_fields = ("title", "team")
    list_display = ("id", "title", "team", "timestamp", "is_verified")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "timestamp", "text")


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "timestamp", "game")
