from django.db import IntegrityError
from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import (
    IsAuthenticated,
    IsAdminUser,
    AllowAny,
)
from rest_framework import generics, mixins, views


from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from django.contrib.auth import get_user_model

from GD.messages import USER_DELETED_SUCCESSFULLY, DUPLICATE_USER_ERROR, LOG_OUT_FAILD, USER_ACTIVED, USER_NOT_FOUND, \
    CORRECT_THE_ERRORS, USER_CREATED_SUCCESSFULLY, USER_LOGED_OUT_SUCCESSFULLY
from .serializers import (
    CustomUserSerializer
)
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from tasks.tasks import send_email_task
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from core.viewsets import ResponseGenericViewSet
from .utils import activation_code
from core.models import (
    Team,
    CompetitionMember
)
from core.serializers import (
    TeamSerialzer
)

class UserViewSet(ResponseGenericViewSet,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin):

    queryset = get_user_model().objects.all()
    serializer_class = CustomUserSerializer
    permission_classes_by_action = {
        'list': [IsAdminUser],
        'retrive': [IsAuthenticated],
        'destroy': [IsAuthenticated],
        'update': [IsAdminUser],
    }
    def retrieve(self, request, *args, **kwargs):
        response_data = super(UserViewSet, self).retrieve(
            request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        self.response_format["status"] = 200
        if not response_data.data:
            self.response_format["message"] = "Empty"
        return Response(self.response_format)

    def list(self, request, *args, **kwargs):
        response_data = super(UserViewSet, self).list(
            request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        self.response_format["status"] = 200
        if not response_data.data:
            self.response_format["message"] = "List empty"
        return Response(self.response_format)

    def update(self, request, *args, **kwargs):
        response_data = super(UserViewSet, self).update(
            request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        self.response_format["status"] = 200

        return Response(self.response_format)

    def destroy(self, request, *args, **kwargs):
        response_data = super(UserViewSet, self).destroy(
            request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        self.response_format["status"] = 200
        return Response(self.response_format)


    @action(methods=['GET'] , detail=False , permission_classes=[IsAuthenticated])
    def profile(self , request):
        serializer = self.serializer_class(request.user)
        return self.set_response(
            data=serializer.data
        )

    @action(methods=['PUT'] , detail=False , permission_classes=[IsAuthenticated],url_path='profile/update')
    def update_profile(self,request):
        try:
            update_data = request.data
            user = request.user
            serializer = self.serializer_class(user)
            serializer.update(instance=user,validated_data=update_data)
            return self.set_response(
                data=serializer.data
            )
        except Exception as e:
            return self.set_response(
                error=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    @action(methods=['DELETE'] , detail=False , permission_classes=[IsAuthenticated],url_path='profile/delete')
    def delete_profile(self,request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            user = request.user
            data = self.serializer_class(user).data
            user.delete()
            return self.set_response(
                message=USER_DELETED_SUCCESSFULLY,
                data = data,
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            return self.set_response(
                message=LOG_OUT_FAILD,
                status=400,
                status_code=status.HTTP_400_BAD_REQUEST,
                error=str(e)
            )

    @action(methods=['GET'] , detail=False , permission_classes=[AllowAny])
    def count(self,request):
        count = get_user_model().objects.count()
        return self.set_response(
            data={
                'count':count
            }
        )

    @action(methods=['GET'] , detail=False , permission_classes=[IsAuthenticated])
    def team(self,request):
        member = CompetitionMember.objects.select_related('team').get(user=request.user)
        serializer = TeamSerialzer(member.team)
        return self.set_response(
            data=serializer.data
        )
        

    

    @action(methods=['POST'], detail=False, permission_classes=[AllowAny])
    def sign_up(self, request):

        serializer = CustomUserSerializer(data=request.data)

        if serializer.is_valid():
            try:
                user = serializer.save()
            except IntegrityError as e:
                return self.set_response(
                    message=DUPLICATE_USER_ERROR,
                    status=409,
                    status_code=status.HTTP_409_CONFLICT,
                    error=str((e))
                )
            if user:
                user.activation_code = activation_code(
                    user.user_name, length=32)
                user.save()
                user_data = {
                    'user_name': user.user_name,
                    'first_name': user.first_name,
                    'email': user.email,
                    'uid': user.activation_code
                }
                send_email_task.delay(user_data)
                return self.set_response(
                    message=USER_CREATED_SUCCESSFULLY,
                    status=201,
                    status_code=status.HTTP_201_CREATED,
                    error=None,
                    data=serializer.data
                )
        return self.set_response(
            message=CORRECT_THE_ERRORS,
            status=400,
            status_code=status.HTTP_400_BAD_REQUEST,
            error=serializer.errors
        )

    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated])
    def log_out(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return self.set_response(
                message=USER_LOGED_OUT_SUCCESSFULLY,
                status=205,
                status_code=status.HTTP_205_RESET_CONTENT,
                data={
                    'refresh_token': str(refresh_token)
                },
                error=None
            )
        except Exception as e:
            return self.set_response(
                message=LOG_OUT_FAILD,
                status=400,
                status_code=status.HTTP_400_BAD_REQUEST,
                error=str(e)
            )

    def get_permissions(self):
        try:
            # return permission_classes depending on `action`
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            # action is not set return default permission_classes
            return [permission() for permission in self.permission_classes]




class VerfiyUserView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = CustomUserSerializer

    def get(self, request, uid):
        try:
            user = get_user_model().objects.get(activation_code=uid)
            user.is_active = True
            user.save()
            data = {
                'message': USER_ACTIVED,
                'error': None,
                'status': 202,
                'data': CustomUserSerializer(user).data
            }
            return Response(data=data, status=status.HTTP_202_ACCEPTED)
        except get_user_model().DoesNotExist as e:
            data = {
                'message': USER_NOT_FOUND,
                'error': str(e),
                'status': 404,
                'data': []
            }
            return Response(data=data, status=status.HTTP_404_NOT_FOUND)
