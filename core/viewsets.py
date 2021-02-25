from django.shortcuts import render
from django.http import Http404
from rest_framework.response import Response
from rest_framework import status

import user
from GD.messages import CAPACITY_IS_FULL, USER_HAS_ALREADY_ENROLLED, SUCCESSFULLY_ADDED, EMPTY
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
            "error": args.get('error', None),
            "data": args.get('data', []),
            "message": args.get('message', None)
        }


class ResponseGenericViewSet(viewsets.GenericViewSet):
    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(viewsets.GenericViewSet, self).__init__(**kwargs)

    def set_response(self,message=None, error=None, data=[], status=200, status_code=status.HTTP_200_OK):
        self.response_format['message'] = message
        self.response_format['error'] = error
        self.response_format['data'] = data
        self.response_format['status'] = status
        return Response(self.response_format, status=status_code)


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
            self.response_format["message"] = EMPTY
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
            self.response_format["message"] = EMPTY
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

    def set_response(self,message=None, error=None, data=[], status=200, status_code=status.HTTP_200_OK):
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
        'retrive': [AllowAny],
        'destroy': [IsAdminUser],
        'update': [IsAdminUser],
    }

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def enroll(self, request, pk):
        model_name = str(self.model.__name__).lower()
        try:
            obj = self.model.objects.get(pk=pk)
            if obj.get_remain_capacity() == 0:
                return self.set_response(
                    error=f"this {model_name} is full",
                    status=200,
                    message=CAPACITY_IS_FULL,
                    status_code=status.HTTP_200_OK,
                )
            user = request.user
            args = {
                'user': user,
                model_name: obj,
                'service_type':self.service_type
            }
            query = EventService.objects.filter(**args)
            if query.exists():
                return self.set_response(
                    error=f"user has already enrolled in this {model_name}",
                    status=410,
                    message=USER_HAS_ALREADY_ENROLLED,
                    status_code=status.HTTP_208_ALREADY_REPORTED,
                    # data=EventServiceSerializer(query[0]).data
                )
            ev_service = EventService.objects.create(**args)
            if obj.cost <=0:
                ev_service.payment_state='CM'
            ev_service.save()
            return self.set_response(
                message=SUCCESSFULLY_ADDED,
                data=EventServiceSerializer(ev_service).data,
            )
        except self.model.DoesNotExist:
            return self.set_response(
                message=f"requested {model_name} doesn't exist",
                error=f"requested {model_name} doesn't exist",
                status=404,
                status_code=status.HTTP_404_NOT_FOUND
            )
            

    @action(methods=['GET'], detail=True, permission_classes=[IsAdminUser])
    def services(self, request, pk):
        model_name = str(self.model.__name__).lower()

        services = self.model.services
        serializer = EventServiceSerializer(services, many=True)
        message = ""
        if not serializer.data:
            message = NO_ANY_SERVICES
        return self.set_response(
            message = message,
            data=serializer.data
        )

    

    def get_permissions(self):
        try:
            # return permission_classes depending on `action`
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            # action is not set return default permission_classes
            return [permission() for permission in self.permission_classes]
