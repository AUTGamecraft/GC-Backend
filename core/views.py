from django.shortcuts import render
from django.http import Http404
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from collections import defaultdict


class TalkViewSet(viewsets.ModelViewSet):
    queryset = Talk.objects.all()
    serializer_class = TalksPageSerializer

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def enroll(self, request, pk):
        talk = get_object_or_404(Talk, pk=pk)
        user = request.user
        service_type = 'TK'
        ev_service = EventService.objects.create(
            talk=talk,
            service=service_type
        )
        user.service_set.add(ev_service)
        user.save()
        data = {'message': 'talk successfully added'}
        return Response(data=data)


class WorkshopViewSet(viewsets.ModelViewSet):
    queryset = Workshop.objects.all()
    serializer_class = WorkshopPageSerializer

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def enroll(self, request, pk):
        workshop = get_object_or_404(Workshop, pk=pk)
        user = request.user
        service_type = 'WS'
        ev_service = EventService.objects.create(
            workshop=workshop,
            service=service_type
        )
        user.service_set.add(ev_service)
        user.save()
        data = {'message': 'workshop successfully added'}
        return Response(data=data)

class UserServicesViewSet(viewsets.GenericViewSet):
    permission_classes=[IsAuthenticated,IsAdminUser]
    queryset=EventService.objects.all()
    serializer_class=EventServiceSerializer

    @action(methods=['GET'] , detail=False,permission_classes=[IsAuthenticated])
    def services(self , request):
        try:
            services = EventService.objects.filter(user=user)
            data = EventServiceSerializer(services,many=True)
            return Response(data.data)
        except EventService.DoesNotExist:
            return Http404




