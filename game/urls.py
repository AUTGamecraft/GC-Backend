
from django.contrib import admin
from django.urls import path , include
from game.views import GameViewAPI, CommentViewAPI, LikeViewAPI

urlpatterns = [
    path('game/', GameViewAPI.as_view({'post': 'post', 'get':'list'})),
    path('game/my-game/', GameViewAPI.as_view({'get':'retrieve'})),
    path('game/comment/', CommentViewAPI.as_view({'post': 'post'})),
    path('game/<pk>/comments/', CommentViewAPI.as_view({'get': 'list'})),
    path('game/like/', LikeViewAPI.as_view({'post': 'post'})),
]
