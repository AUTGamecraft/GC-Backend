from django.shortcuts import render
from .models import (
    Talk
    )
from .serializers import (
    TalkSerializer
)
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated



class TalkList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Talk.objects.all()
    serializer_class = TalkSerializer