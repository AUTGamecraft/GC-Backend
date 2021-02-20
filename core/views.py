import json
from datetime import datetime

from rest_framework import generics, mixins, views
from .idpay import IdPayRequest, IDPAY_PAYMENT_DESCRIPTION, \
    IDPAY_CALL_BACK, IDPAY_STATUS_201, IDPAY_STATUS_100, IDPAY_STATUS_101, \
    IDPAY_STATUS_200, IDPAY_STATUS_10

from django.shortcuts import get_object_or_404 , redirect
from .viewsets import *
from tasks.tasks import send_team_requests_task
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode , urlsafe_base64_encode
from .tools import team_activation_code
from django.utils.encoding import force_bytes


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
            services = user.services
            data = EventServiceSerializer(services, many=True)
            return Response(data.data)
        except EventService.DoesNotExist:
            return Http404

    @action(methods=['POST'] , detail=False , permission_classes=[IsAuthenticated])
    def payment(self, request):
        user = request.user
        services = EventService.objects.filter(user=user).select_related('talk' , 'workshop')
        total_price = 0
        # check capacity to register
        for service in services:
            if service.payment_state == 'PN':
                event = service.talk if service.service_type == 'TK' else service.workshop
                if event.get_remain_capacity() > 0:
                    total_price += event.cost
                else:
                    return self.set_response(message=f"event {event.title} is full you must remove it!!!",status_code=status.HTTP_406_NOT_ACCEPTABLE,error=f"event {event.title} is full you must remove it!!!")
        # create payment object
        payment = Payment.objects.create(
            total_price=total_price,
            user=user
        )


        result = IdPayRequest().create_payment(
             order_id=payment.pk,
            amount=total_price ,
             desc=IDPAY_PAYMENT_DESCRIPTION,
            mail=user.email,
            phone=user.phone_number,
            callback=IDPAY_CALL_BACK,
            name=user.first_name
        )
        if result['status'] == IDPAY_STATUS_201:
            payment.services.set(services)
            payment.created_date=datetime.now()
            payment.IDPAY_ID=result['id']
            payment.payment_link=result['link']
            payment.save()
            print("pk***********",payment.pk)
            return self.set_response(
                message=None
                ,data=result
                ,status_code=status.HTTP_200_OK
            )
            # return redirect('http://gamecraft.ce.aut.ac.ir')
        else:
            payment.delete()
            return self.set_response(
                message="request for payment wasn't successfull!!!"
                ,data=result
                ,status_code=status.HTTP_400_BAD_REQUEST,
                error=[{"error_code":result['status']}]

            )
                
    @action(methods=['POST'] , detail=False , permission_classes=[AllowAny])
    def verify(self, request):
        try:
            request_body=request.data
            idPay_payment_id = request_body['id']
            order_id=request_body['order_id']
            payment = Payment.objects.get(pk=order_id)
            payment.card_number=request_body['card_no']
            payment.hashed_card_number=request_body['hashed_card_no']
            payment.payment_trackID=request_body['track_id']
            result = IdPayRequest().verify_payment(
                order_id=order_id,
                payment_id=idPay_payment_id,
            )
            result_status=result['status']

            if any(result_status == status_code for status_code in (IDPAY_STATUS_100,IDPAY_STATUS_101,IDPAY_STATUS_200)):
                services = EventService.objects.select_related('workshop' , 'talk').filter(payment=payment)
                for service in services:
                    service.payment_state = 'CM'
                    if service.workshop:
                        service.workshop.participant_count += 1
                        service.workshop.save()
                    elif service.talk:
                        service.talk.participant_count += 1
                        service.talk.save()
                    else:
                        CompetitionMember.objects.create(user=user).save()
                    service.save()
                payment.status = result_status
                payment.original_data=json.dumps(result)
                payment.verify_trackID = result['track_id']
                payment.finished_date = result['date']
                payment.verified_date = result['verify']['date']
                payment.save()
                return redirect('http://gamecraft.ce.aut.ac.ir/dashboard-event')
            else:
                payment.status = result_status
                payment.original_data = json.dumps(result)
                payment.save()
                return self.set_response(message='failed',error='failed')
            

        except Payment.DoesNotExist as e1:
            raise ValidationError('no any payment with this order_id')


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
            
    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated])
    def register(self, request):
        user = request.user
        if not CompetitionMember.objects.filter(user=user).exists():
            member = CompetitionMember.objects.create(user=user, has_team=False, is_head=False)
            member.save()
            serializer = self.serializer_class(member)
            return self.set_response(data=serializer.data, message="user added to competition")
        return self.set_response(data=[] , message='user already registered in the competition')
        

    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
    def is_registered(self, request):
        try:
            email = request.data['email']
            result = CompetitionMember.objects.filter(
                user__email=email, has_team=False).exists()
            if result:
                return self.set_response(data={
                    'available': True
                })
            else:
                return self.set_response(data={
                    'available': False
                }, message="requested user is not registered or already has a team")
        except KeyError as e:
            return self.set_response(error='bad request', status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e1:
            return self.set_response(error=str(e1), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(methods=['GET'] , detail=False , permission_classes=[IsAuthenticated])
    def registered_list(self,request):
        cmembers = CompetitionMember.objects.filter(has_team=False)
        serialized = self.serializer_class(cmembers,many=True)
        return self.set_response(
            data= serialized.data 
        )



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

    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated])
    def create_team(self, request):
        print(request.data)
        try:
            head = CompetitionMember.objects.select_related('user').get(user=request.user)
            if head.has_team:
                raise ValidationError(f"you already have a team !!!")
            head.is_head = True
            head.has_team = True
            team = Team.objects.create(name=request.data['name'],team_activation=team_activation_code(request.data['name']))
            members = CompetitionMember.objects.select_related('user').filter(
                user__email__in=request.data['emails'])
            if len(members) > 5 or len(members) < 3:
                raise ValidationError(
                    "count of user members must be between 3 and 5 ")
            for mem in members:
                if mem.has_team:
                    raise ValidationError(
                        f"user {mem.user.user_name} has team")
            head.team = team
            head.save()
            team.save()
            for mem in members:
                team_data = {
                    'head_name': head.user.user_name,
                    'team_name': team.name,
                    'email': mem.user.email,
                    'first_name':mem.user.first_name,
                    'tid':team.team_activation,
                    'mid':urlsafe_base64_encode(force_bytes(mem.pk))
                }
                send_team_requests_task.delay(team_data)
            return Response(data=self.serializer_class(team).data)
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


class VerifyTeamRequestView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = CompetitionMember
    def get(self, request, tid, mid):
        mid = force_text(urlsafe_base64_decode(mid))
        try:
            member = CompetitionMember.objects.get(pk=mid)
            team = Team.objects.get(team_activation=tid)
            if member.has_team:
                data = {
                    'message': 'User already has a team!!!',
                    'error': None,
                    'status': 200,
                    'data': []
                }
                return Response(data=data, status=status.HTTP_200_OK)  
            members_num = team.members.count()
            if members_num > 5:
                data = {
                    'message': 'team is full!!!',
                    'error': None,
                    'status': 200,
                    'data': []
                }
                return Response(data=data, status=status.HTTP_200_OK)  
            member.has_team = True
            member.team = team
            member.save()
            if members_num >=3:
                team.state = 'AC'
            team.save()
            data = {
                'message': 'user activated',
                'error': None,
                'status': 202,
                'data': CompetitionMemberSerializer(member).data
            }
            return Response(data=data, status=status.HTTP_202_ACCEPTED)
        except CompetitionMember.DoesNotExist as e:
            data = {
                'message': 'user not found',
                'error': str(e),
                'status': 400,
                'data': []
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        except Team.DoesNotExist as e1:
            data = {
                'message': 'team not found',
                'error': str(e1),
                'status': 400,
                'data': []
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e2:
            data = {
                'message': 'something went wrong',
                'error': str(e2),
                'status': 400,
                'data': []
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        