from django.shortcuts import render
from django.http import Http404
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics, mixins, views
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
from tasks.tasks import send_team_requests_task


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


class CompetitionMemberViewSet(ResponseGenericViewSet,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  mixins.ListModelMixin):
    queryset = CompetitionMember.objects.all()
    serializer_class = CompetitionMemberSerializer
    permission_classes_by_action = {
        'list': [IsAuthenticated],
        'retrive': [IsAdminUser],
        'destroy': [IsAdminUser],
        'update': [IsAdminUser],
    }


    def retrieve(self, request, *args, **kwargs):
        response_data = super(ResponseModelViewSet, self).retrieve(
            request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        self.response_format["status"] = 200
        if not response_data.data:
            self.response_format["message"] = "Empty"
        return Response(self.response_format)
        
    def list(self, request, *args, **kwargs):
        response_data = super(TeamViewSet, self).list(
            request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        self.response_format["status"] = 200
        if not response_data.data:
            self.response_format["message"] = "List empty"
        return Response(self.response_format)

    def update(self, request, *args, **kwargs):
        response_data = super(TeamViewSet, self).update(
            request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        self.response_format["status"] = 200

        return Response(self.response_format)

    def destroy(self, request, *args, **kwargs):
        response_data = super(TeamViewSet, self).destroy(
            request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        self.response_format["status"] = 200
        return Response(self.response_format)


    def get_permissions(self):
        try:
            # return permission_classes depending on `action`
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            # action is not set return default permission_classes
            return [permission() for permission in self.permission_classes]



class TeamViewSet(ResponseGenericViewSet,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  mixins.ListModelMixin):
    queryset = Team.objects.all()
    serializer_class = TeamSerialzer
    permission_classes_by_action = {
        'list': [IsAuthenticated],
        'retrive': [IsAdminUser],
        'destroy': [IsAdminUser],
        'update': [IsAdminUser],
    }
    
    def retrieve(self, request, *args, **kwargs):
        response_data = super(ResponseModelViewSet, self).retrieve(
            request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        self.response_format["status"] = 200
        if not response_data.data:
            self.response_format["message"] = "Empty"
        return Response(self.response_format)

    def list(self, request, *args, **kwargs):
        response_data = super(TeamViewSet, self).list(
            request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        self.response_format["status"] = 200
        if not response_data.data:
            self.response_format["message"] = "List empty"
        return Response(self.response_format)

    def update(self, request, *args, **kwargs):
        response_data = super(TeamViewSet, self).update(
            request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        self.response_format["status"] = 200

        return Response(self.response_format)

    def destroy(self, request, *args, **kwargs):
        response_data = super(TeamViewSet, self).destroy(
            request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        self.response_format["status"] = 200
        return Response(self.response_format)

    @action(methods=['POST'] , detail=False , permission_classes=[IsAuthenticated])
    def create_team(self,request):
        try:
            head = CompetitionMember.objects.get(user=request.user)
            head.is_head = True
            ser = self.serializer_class(data=request.data)
            if not ser.is_valid():
                raise ValidationError("data is not valid")
            team = ser.save()
            members = CompetitionMember.objects.filter(user__email__in=request.data['emails'])
            for mem in members:
                if mem.has_team:
                    raise ValidationError(f"user {mem.user.user_name} has team")
                else:
                    mem.has_team = True
                    mem.team = team
                    mem.save()
            team.save()
            print(f"-----------{team.members}--------------")
            send_team_requests_task.delay({})
            return Response(data=ser.data)
        except CompetitionMember.DoesNotExist as e:
            return self.set_response(error=str(e))
        except ValidationError as e1:
            return self.set_response(error=str(e1))
        except Exception e2:
            return self.set_response(error=str(e2))

    def get_permissions(self):
        try:
            # return permission_classes depending on `action`
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            # action is not set return default permission_classes
            return [permission() for permission in self.permission_classes]




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
