from rest_framework.viewsets import mixins, GenericViewSet
from rest_framework import permissions
from rest_framework.pagination import LimitOffsetPagination
from game.models import Game, Comment, Like
from user.models import Team
from game.serializers import GameSerializer, CommentSerializer, LikeSerializer
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.views import exception_handler
from rest_framework import status
from decouple import config

CAN_CREATE_LIKE = config("CAN_CREATE_LIKE", cast=bool)

def custom_exception_handler(exc, context):

    response = exception_handler(exc, context)

    if response is None:
        response = Response(data={"error":{"detail": "some error occurred"}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response


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

class GameUserPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        print(view.action)
        if view.action in ["list"]:
            return True
        elif view.action in ["post", "update", "partial_update", "destroy", "retrieve"]:
            # print(request.user.is_authenticated())
            return bool(request.user and request.user.is_authenticated)
        else:
            return False


class GameViewAPI(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    permission_classes = [
        GameUserPermission,
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

    def get_object(self):
        user = self.request.user
        try:
            team = user.team
            if team:
                game = user.team.game
                return game
            
            raise ValidationError(detail='team does not exist', code=status.HTTP_404_NOT_FOUND)
        except Game.DoesNotExist:
            raise ValidationError(detail='game does not exist', code=status.HTTP_404_NOT_FOUND)            

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
        if not CAN_CREATE_LIKE:
            return Response(data={"error":"Like submit time is over"})
        
        self.set_request_context()
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            if "The fields user, game must make a unique set" in str(e):
                print("wants to update")
                return super().update(request, *args, **kwargs)
            
            return custom_exception_handler(e, None)
                