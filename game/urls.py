
from django.contrib import admin
from django.urls import path , include
from game.views import GameViewAPI, CommentViewAPI

urlpatterns = [
    path('game/', GameViewAPI.as_view({'post': 'post', 'get':'list'})),
    path('game/comment/', CommentViewAPI.as_view({'post': 'post'})),
    path('game/<pk>/comments/', CommentViewAPI.as_view({'get': 'list'}))
]
