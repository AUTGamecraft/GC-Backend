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

class UserViewSet(viewsets.GenericViewSet):

    permission_classes = [AllowAny]
    queryset = get_user_model().objects.all()
    serializer_class = CustomUserSerializer

    @action(methods=['POST'] , detail=False)
    def sign_up(self, request ):
        serializer = serializer_class(data = request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                json = serializer.data
                return Response(json , status=status.HTTP_201_CREATED)
            return  Response(serializer.errors , status=status.HTTP_400_BAD_REQUEST) 

    
    @action(methods=['POST'] , detail=False):
    def log_out(self,request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
