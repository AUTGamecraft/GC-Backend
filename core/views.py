from django.shortcuts import render
from django.http import Http404
from rest_framework.response import Response
from rest_framework import status

import user
from .models import *
from .serializers import *
from rest_framework.permissions import (
    IsAuthenticated,
    IsAdminUser,
    AllowAny
)
from rest_framework.decorators import action
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from collections import defaultdict
from .viewsets import *



class TalkViewSet(ServicesModelViewSet):
    queryset = Talk.objects.all()
    serializer_class = TalksPageSerializer
    model=Talk
    service_type = 'TK'

class WorkshopViewSet(ServicesModelViewSet):
    queryset = Workshop.objects.all()
    serializer_class = WorkshopPageSerializer
    model = Workshop
    service_type = 'WS'

class UserServicesViewSet(ResponseGenericViewSet):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = EventService.objects.all()
    serializer_class = EventServiceSerializer

    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
    def services(self, request):
        try:
            user = request.user
            services = EventService.objects.filter(user=user)
            data = EventServiceSerializer(services, many=True)
            return Response(data.data)
        except EventService.DoesNotExist:
            return Http404

class PresenterViweSet(ResponseModelViewSet):
    queryset = Presenter.objects.all()
    serializer_class = PresenterSerializer
    # set permission for built_in routes
    permission_classes_by_action = {
        'create': [IsAdminUser],
        'list': [IsAdminUser],
        'retrive': [IsAdminUser],
        'destroy': [IsAdminUser],
        'update': [IsAdminUser],
    }
