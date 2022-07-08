from django.forms import ValidationError
from rest_framework.viewsets import mixins, GenericViewSet
from rest_framework import permissions
from rest_framework.pagination import LimitOffsetPagination
from game.models import Game, Comment, Like
from game.serializers import GameSerializer, CommentSerializer, LikeSerializer
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler


class UserPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        print(view.action)
        if view.action in ["list", "retrieve"]:
            return True
        elif view.action in ["post", "update", "partial_update", "destroy"]:
            # print(request.user.is_authenticated())
            return bool(request.user and request.user.is_authenticated)
        else:
            return False


class GameViewAPI(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    permission_classes = [
        UserPermission,
    ]
    serializer_class = GameSerializer
    pagination_class = LimitOffsetPagination


    def get_queryset(self):
        return Game.objects.filter(is_verified=True)

    def set_request_context(self):
        request = self.request

        mutable = request.data._mutable
        request.data._mutable = True
        request.data["creator"] = self.request.user.pk
        request.data._mutable = mutable

    # TODO: for later on, update or remove document
    # def get_object(self):
    #     game_id = self.kwargs["pk"]
    #     user = self.request.user
    #     return Game.objects.get(pk=game_id, user=user)

    def post(self, request, *args, **kwargs):
        self.set_request_context()
        return super().create(request, *args, **kwargs)


class CommentViewAPI(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    permission_classes = [
        UserPermission,
    ]
    serializer_class = CommentSerializer
    pagination_class = LimitOffsetPagination
    
    def get_queryset(self):
        game = self.kwargs['pk']
        return Comment.objects.filter(game=game, game__is_verified=True)

    def set_request_context(self):
        request = self.request

        mutable = request.data._mutable
        request.data._mutable = True
        request.data["user"] = self.request.user.pk
        request.data._mutable = mutable

    def post(self, request, *args, **kwargs):
        self.set_request_context()
        return super().create(request, *args, **kwargs)

class LikeViewAPI(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    permission_classes = [
        UserPermission,
    ]
    serializer_class = LikeSerializer
    
    
    def get_object(self):
        game_id = self.request.data["game"]
        like = Like.objects.get(user=self.request.user, game=game_id)
        
        return like
    
    def set_request_context(self):
        request = self.request

        mutable = request.data._mutable
        request.data._mutable = True
        request.data["user"] = self.request.user.pk
        request.data._mutable = mutable

    def post(self, request, *args, **kwargs):
        self.set_request_context()
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            if "The fields user, game must make a unique set" in str(e):
                print("wants to update")
                return super().update(request, *args, **kwargs)
           
            return exception_handler(e, self.get_serializer_context())
                