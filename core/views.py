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
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin):
    queryset = CompetitionMember.objects.all()
    serializer_class = CompetitionMemberSerializer
    permission_classes_by_action = {
        'list': [IsAuthenticated],
        'retrive': [IsAuthenticated],
        'destroy': [IsAdminUser],
        'update': [IsAdminUser],
    }


    def retrieve(self, request, *args, **kwargs):
        response_data = super(CompetitionMemberViewSet, self).retrieve(
            request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        self.response_format["status"] = 200
        if not response_data.data:
            self.response_format["message"] = "Empty"
        return Response(self.response_format)
        
    def list(self, request, *args, **kwargs):
        response_data = super(CompetitionMemberViewSet, self).list(
            request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        self.response_format["status"] = 200
        if not response_data.data:
            self.response_format["message"] = "List empty"
        return Response(self.response_format)

    def update(self, request, *args, **kwargs):
        response_data = super(CompetitionMemberViewSet, self).update(
            request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        self.response_format["status"] = 200

        return Response(self.response_format)

    def destroy(self, request, *args, **kwargs):
        response_data = super(CompetitionMemberViewSet, self).destroy(
            request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        self.response_format["status"] = 200
        return Response(self.response_format)

    @action(methods=['POST'] , detail=False , permission_classes=[IsAuthenticated])
    def register(self,request):
        user = request.user
        member = CompetitionMember(user=user , has_team=False,is_head=False,request_state='RE')
        member.save()
        serializer = self.serializer_class(member)
        # put payment module 
        return self.set_response(data=serializer.data ,message="user added to competition")
    
    @action(methods=['GET'] , detail=False , permission_classes=[IsAuthenticated])
    def is_registered(self,request):
        try:
            email = request.data['email']
            result = CompetitionMember.objects.filter(user__email=email,has_team=False).exists()
            if result:
                return self.set_response(data={
                    'available':True
                })
            else:
                return self.set_response(data={
                    'available':False
                },message="requested user is not registered or already has a team")
        except KeyError as e:
            return self.set_response(error='bad request' , status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e1:
            return self.set_response(error=str(e1) , status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    

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
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin):
    queryset = Team.objects.all()
    serializer_class = TeamSerialzer
    permission_classes_by_action = {
        'list': [IsAuthenticated],
        'retrive': [IsAuthenticated],
        'destroy': [IsAdminUser],
        'update': [IsAdminUser],
    }
    
    def retrieve(self, request, *args, **kwargs):
        response_data = super(TeamViewSet, self).retrieve(
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
            if head.has_team:
                raise ValidationError(f"you already have a team !!!")
            head.is_head = True
            head.has_team = True
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
            head.team = team
            head.save()
            team.save()
            send_team_requests_task.delay({})
            return Response(data=ser.data)
        except CompetitionMember.DoesNotExist as e:
            return self.set_response(error=str(e))
        except ValidationError as e1:
            return self.set_response(error=str(e1))
        except Exception as e2:
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
        'list': [AllowAny],
        'retrive': [AllowAny],
        'destroy': [IsAdminUser],
        'update': [IsAdminUser],
    }
