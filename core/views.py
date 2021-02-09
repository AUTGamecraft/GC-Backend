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
    model = Talk
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


class CompetitionMemberViewSet(ResponseModelViewSet):
    queryset = CompetitionMember.objects.all()
    serializer_class = CompetitionMemberSerializer
    permission_classes_by_action = {
        'create': [IsAdminUser],
        'list': [IsAuthenticated],
        'retrive': [IsAdminUser],
        'destroy': [IsAdminUser],
        'update': [IsAdminUser],
    }


class TeamViewSet(ResponseGenericViewSet,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  mixins.ListModelMixin):
    queryset = Team.objects.all()
    serializer_class = TeamSerialzer
    permission_classes_by_action = {
        'list': [IsAuthenticated],
        'destroy': [IsAdminUser],
        'update': [IsAdminUser],
    }

    def list(self, request, *args, **kwargs):
        response_data = super(ResponseModelViewSet, self).list(
            request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        self.response_format["status"] = 200
        if not response_data.data:
            self.response_format["message"] = "List empty"
        return Response(self.response_format)

    def update(self, request, *args, **kwargs):
            response_data = super(ResponseModelViewSet, self).update(
                request, *args, **kwargs)
            self.response_format["data"] = response_data.data
            self.response_format["status"] = 200

        return Response(self.response_format)

    def destroy(self, request, *args, **kwargs):
        response_data = super(ResponseModelViewSet, self).destroy(
            request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        self.response_format["status"] = 200
        return Response(self.response_format)

    @action(methods=['POST'] , detail=True , permission_classes=[IsAuthenticated])
    def create(self,request):
        
    

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
