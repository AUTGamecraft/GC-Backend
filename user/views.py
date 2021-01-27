from django.db import IntegrityError
from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
    )

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from django.contrib.auth import get_user_model
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



class UserViewSet(ResponseGenericViewSet):

    permission_classes = [AllowAny]
    queryset = get_user_model().objects.all()
    serializer_class = CustomUserSerializer

    @action(methods=['POST'] , detail=False)
    def sign_up(self, request ):

        serializer = CustomUserSerializer(data = request.data)

        if serializer.is_valid():
            try:
                user = serializer.save()
            except IntegrityError as e:
                return self.set_response(
                    message=str(e),
                    status=409,
                    status_code=status.HTTP_409_CONFLICT
                )
            if user:
                # send_email_task.delay(user_data)
                return self.set_response(
                    message= 'user created',
                    status=201,
                    status_code=status.HTTP_201_CREATED,
                    error=False,
                    data=serializer.data
                )
        return self.set_response(
            message=str(serializer.errors),
            status=400,
            status_code=status.HTTP_400_BAD_REQUEST,
            error=True
        ) 
        

    
    @action(methods=['POST'] , detail=False)
    def log_out(self,request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return self.set_response(
                message='user loged out successfully',
                status=205,
                status_code=status.HTTP_205_RESET_CONTENT,
                data={
                    'refresh_token':str(refresh_token)
                }
            )
        except Exception as e:
            return self.set_response(
                message=str(e),
                status=400,
                status_code=status.HTTP_400_BAD_REQUEST
            )


class VerfiyUserView(generics.GenericAPIView):
    permission_classes=[AllowAny]
    def post(self , request , uid):
        userid = force_text(urlsafe_base64_decode(uid))
        try:            
            user = get_user_model().objects.get(pk=userid)
            user.is_active = True
            user.save()
            data = {
                'message':'user activated',
                'error':False,
                'status':202,
                'status_code': status.HTTP_202_ACCEPTED,
                'data':CustomUserSerializer(user).data
            }
            return Response(data=data , status=status.HTTP_202_ACCEPTED)
        except get_user_model().DoesNotExist:
            data = {
                'message':'user not found',
                'error':True,
                'status':400,
                'status_code': status.HTTP_400_BAD_REQUEST,
                'data':[]
            }
            return Response(data=data , status=status.HTTP_400_BAD_REQUEST)