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


class ResponseInfo(object):
    def __init__(self, user=None, **args):
        self.response = {
            "status": args.get('status', 200),
            "error": args.get('error', False),
            "data": args.get('data', []),
            "message": args.get('message', 'success')
        }


class ResponseGenericViewSet(viewsets.GenericViewSet):
    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(ResponseModelViewSet, self).__init__(**kwargs)


class ResponseModelViewSet(viewsets.ModelViewSet):

    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(ResponseModelViewSet, self).__init__(**kwargs)

    def list(self, request, *args, **kwargs):
        response_data = super(ResponseModelViewSet, self).list(
            request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        self.response_format["status"] = 200
        if not response_data.data:
            self.response_format["message"] = "List empty"
        return Response(self.response_format)

    def create(self, request, *args, **kwargs):
        response_data = super(ResponseModelViewSet, self).create(
            request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        self.response_format["status"] = 200
        return Response(self.response_format)

    def retrieve(self, request, *args, **kwargs):
        response_data = super(ResponseModelViewSet, self).retrieve(
            request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        self.response_format["status"] = 200
        if not response_data.data:
            self.response_format["message"] = "Empty"
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

    def set_response(message="", error=False, data=[], status=200, status_code=status.HTTP_200_OK):
        self.response_format['message'] = message
        self.response_format['error'] = error
        self.response_format['data'] = data
        self.response_format['status'] = status
        return Response(self.response_format, status=status_code)


class ServicesModelViewSet(ResponseModelViewSet):
    model = None
    service_type = None

    permission_classes_by_action = {
        'create': [IsAdminUser],
        'list': [AllowAny],
        'retrive': [IsAdminUser],
        'destroy': [IsAdminUser],
        'update': [IsAdminUser],
    }

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def enroll(self, request, pk):
        model_name = str(self.model.__name__).lower()
        try:
            obj = get_object_or_404(self.model, pk=pk)
            obj = self.model.objects.get(pk=pk)
            user = request.user

            args = {
                'user': user,
                model_name: obj
            }

            query = EventService.objects.filter(**args)
            if query.exists():
                return self.set_response(
                    message="user has already enrolled in this course",
                    status=208,
                    status_code=status.HTTP_208_ALREADY_REPORTED,
                    data=EventServiceSerializer(query.get(0)).data
                )

            args['service_type'] = self.service_type

            ev_service = EventService.objects.create(**args)
            ev_service.save()
            return self.set_response(
                message=f'{model_name} successfully added',
                data=EventServiceSerializer(ev_service).data,
            )
        except self.model.DoesNotExist:
            return self.set_response(
                message=f"requested {model_name} doesn't exist",
                error=True,
                status=404,
                status_code=status.HTTP_404_NOT_FOUND
            )
            

    @action(methods=['GET'], detail=True, permission_classes=[IsAdminUser])
    def services(self, request, pk):
        
        model_name = str(self.model.__name__).lower()
        args = {
            f'{model_name}__pk': pk
        }
        services = EventService.objects.filter(**args)
        serialzer = EventServiceSerializer(services, many=True)
        message = ""
        if not serialzer.data:
            message = f"there is no {model_name} service!!!"
        return self.set_response(
            message = message,
            data=serialzer.data
        )

    def get_permissions(self):
        try:
            # return permission_classes depending on `action`
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            # action is not set return default permission_classes
            return [permission() for permission in self.permission_classes]
