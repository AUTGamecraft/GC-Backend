from datetime import datetime
from logging import exception

from django.db import IntegrityError
from rest_framework.permissions import (
    IsAuthenticated,
    IsAdminUser,
    AllowAny,
)
from rest_framework import generics, mixins, views
from rest_framework.exceptions import ValidationError

from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes

from GD.settings.base import PAYWALL
from core.idpay import IdPayRequest, IDPAY_PAYMENT_DESCRIPTION, IDPAY_CALL_BACK, IDPAY_STATUS_201
from core.models import SingletonCompetition, EventService, Payment
from core.payping import PayPingRequest, PayPing_PAYMENT_DESCRIPTION, PayPing_CALL_BACK, PAYPING_STATUS_OK, \
    PayPingPeymentLinkGenerator
from core.serializers import EventServiceSerializer
from tasks.tasks import (
    send_team_requests_task,
    send_email_task,
    change_pass_email_task
)

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from django.contrib.auth import get_user_model

from GD.messages import *
from .serializers import (
    CustomUserSerializer
)
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from core.viewsets import ResponseGenericViewSet
from .utils import activation_code, team_activation_code
from .models import (
    Team,
)
from .serializers import (
    TeamSerializer,
    UserTeamSerializer
)
from django.db import transaction
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        response = Response(data={"error": {"detail": "some error occurred"}},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response


class UserViewSet(ResponseGenericViewSet,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin):
    queryset = get_user_model().objects.all()
    serializer_class = CustomUserSerializer
    permission_classes_by_action = {
        'list': [IsAdminUser],
        'retrieve': [IsAuthenticated],
        'destroy': [IsAuthenticated],
        'update': [IsAdminUser],
    }

    def retrieve(self, request, *args, **kwargs):
        response_data = super(UserViewSet, self).retrieve(
            request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        self.response_format["status"] = 200
        if not response_data.data:
            self.response_format["message"] = "Empty"
        return Response(self.response_format)

    def list(self, request, *args, **kwargs):
        response_data = super(UserViewSet, self).list(
            request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        self.response_format["status"] = 200
        if not response_data.data:
            self.response_format["message"] = "List empty"
        return Response(self.response_format)

    def update(self, request, *args, **kwargs):
        response_data = super(UserViewSet, self).update(
            request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        self.response_format["status"] = 200

        return Response(self.response_format)

    def destroy(self, request, *args, **kwargs):
        response_data = super(UserViewSet, self).destroy(
            request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        self.response_format["status"] = 200
        return Response(self.response_format)

    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
    def profile(self, request):
        serializer = self.serializer_class(request.user)
        return self.set_response(
            data=serializer.data
        )

    @action(methods=['PUT'], detail=False, permission_classes=[IsAuthenticated], url_path='profile/update')
    def update_profile(self, request):
        try:
            update_data = request.data
            user = request.user
            serializer = self.serializer_class(user)
            serializer.update(instance=user, validated_data=update_data)
            return self.set_response(
                data=serializer.data
            )
        except Exception as e:
            return self.set_response(
                error=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(methods=['DELETE'], detail=False, permission_classes=[IsAuthenticated], url_path='profile/delete')
    def delete_profile(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            user = request.user
            data = self.serializer_class(user).data
            user.delete()
            return self.set_response(
                message=USER_DELETED_SUCCESSFULLY,
                data=data,
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            return self.set_response(
                message=LOG_OUT_FAILD,
                status=400,
                status_code=status.HTTP_400_BAD_REQUEST,
                error=str(e)
            )

    @action(methods=['GET'], detail=False, permission_classes=[AllowAny])
    def count(self, request):
        count = get_user_model().objects.filter(is_active=True).count()
        return self.set_response(
            data={
                'count': count
            }
        )

    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
    def team(self, request):
        try:
            serializer = TeamSerializer(
                get_user_model().objects.get(pk=request.user.pk).team)
            return self.set_response(
                data=serializer.data
            )
        except AttributeError as e:
            return self.set_response(
                error=str(e),
                status_code=status.HTTP_404_NOT_FOUND,
                status=404,
                message='شما تیم ندارید!!!'
            )

    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated])
    def available(self, request):
        try:
            email = request.data['email']
            result = get_user_model().objects.filter(
                email=email, team_role='NO', is_active=True).exists()
            if result:
                return self.set_response(data={
                    'available': True
                })
            else:
                return self.set_response(data={
                    'available': False
                }, message=REQUESTED_USER_IS_NOT_REGISTERED_OR_ALREADY_HAS_A_TEAM)
        except KeyError as e:
            return self.set_response(error='bad request', status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e1:
            return self.set_response(error=str(e1), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
    def available_list(self, request):
        cmembers = get_user_model().objects.filter(
            team_role='NO', is_active=True, is_staff=False)
        serialized = UserTeamSerializer(cmembers, many=True)
        return self.set_response(
            data=serialized.data
        )

    @action(methods=['POST'], detail=False, permission_classes=[AllowAny])
    def sign_up(self, request):

        serializer = CustomUserSerializer(data=request.data)

        if serializer.is_valid():
            try:
                user = serializer.save()
            except IntegrityError as e:
                return self.set_response(
                    message=DUPLICATE_USER_ERROR,
                    status=409,
                    status_code=status.HTTP_409_CONFLICT,
                    error=str(e)
                )
            if user:
                user.activation_code = activation_code(user.user_name, length=32)
                user.save()
                user_data = {
                    'user_name': user.user_name,
                    'first_name': user.first_name,
                    'email': user.email,
                    'uid': user.activation_code
                }
                print("hey 1")
                send_email_task.delay(user_data)
                print("hey 2")
                return self.set_response(
                    message=USER_CREATED_SUCCESSFULLY,
                    status=201,
                    status_code=status.HTTP_201_CREATED,
                    error=None,
                    data=serializer.data
                )
        return self.set_response(
            message=CORRECT_THE_ERRORS,
            status=400,
            status_code=status.HTTP_400_BAD_REQUEST,
            error=serializer.errors
        )

    @action(methods=['POST'], detail=False, permission_classes=[AllowAny])
    def reset_pass(self, request):
        try:
            email = request.data['email']
            user = get_user_model().objects.get(email=email)
            user.activation_code = activation_code(user.user_name)
            user.save()
            user_data = {
                'user_name': user.user_name,
                'first_name': user.first_name,
                'email': user.email,
                'uid': user.activation_code
            }
            change_pass_email_task.delay(user_data)
            return self.set_response(
                message="ایمیل برای تغییر رمزعبور فرستاده شد",
                status=200,
                status_code=status.HTTP_200_OK
            )
        except KeyError as e:
            return self.set_response(
                message='bad request',
                status_code=status.HTTP_400_BAD_REQUEST,
                status=400
            )
        except get_user_model().DoesNotExist as e2:
            return self.set_response(
                message='کاربری با ایمیل وارد شده وجود ندارد',
                status=404,
                status_code=status.HTTP_404_NOT_FOUND
            )

    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated])
    def log_out(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return self.set_response(
                message=USER_LOGED_OUT_SUCCESSFULLY,
                status=205,
                status_code=status.HTTP_205_RESET_CONTENT,
                data={
                    'refresh_token': str(refresh_token)
                },
                error=None
            )
        except Exception as e:
            return self.set_response(
                message=LOG_OUT_FAILD,
                status=400,
                status_code=status.HTTP_400_BAD_REQUEST,
                error=str(e)
            )

    def get_permissions(self):
        try:
            # return permission_classes depending on `action`
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            # action is not set return default permission_classes
            return [permission() for permission in self.permission_classes]


class VerfiyUserView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = CustomUserSerializer

    def get(self, request, uid):
        try:
            user = get_user_model().objects.get(activation_code=uid)
            user.is_active = True
            user.save()
            data = {
                'message': USER_ACTIVED,
                'error': None,
                'status': 202,
                'data': CustomUserSerializer(user).data
            }
            return Response(data=data, status=status.HTTP_202_ACCEPTED)
        except get_user_model().DoesNotExist as e:
            data = {
                'message': USER_NOT_FOUND,
                'error': str(e),
                'status': 404,
                'data': []
            }
            return Response(data=data, status=status.HTTP_404_NOT_FOUND)


class VerfiyResetPasswordUserView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = CustomUserSerializer

    def put(self, request, uid):
        try:
            user = get_user_model().objects.get(activation_code=uid)
            password = request.data['password']
            user.set_password(password)
            user.save()
            data = {
                'message': "رمز عبور با موقفیت عوض شد",
                'error': None,
                'status': 200,
                'data': CustomUserSerializer(user).data
            }
            return Response(data=data, status=status.HTTP_200_OK)
        except get_user_model().DoesNotExist as e:
            data = {
                'message': USER_NOT_FOUND,
                'error': str(e),
                'status': 404,
                'data': []
            }
            return Response(data=data, status=status.HTTP_404_NOT_FOUND)


class TeamViewSet(ResponseGenericViewSet,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes_by_action = {
        'list': [IsAuthenticated],
        'retrieve': [IsAuthenticated],
        'destroy': [IsAdminUser],
        'update': [IsAdminUser],
    }

    def retrieve(self, request, *args, **kwargs):
        response_data = super(TeamViewSet, self).retrieve(request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        self.response_format["status"] = 200
        if not response_data.data:
            self.response_format["message"] = EMPTY
        return Response(self.response_format)

    def list(self, request, *args, **kwargs):
        response_data = super(TeamViewSet, self).list(request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        self.response_format["status"] = 200
        if not response_data.data:
            self.response_format["message"] = EMPTY
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
        try:
            head = request.user
            if head.team_role != 'NO':
                # raise ValidationError(YOU_ALREADY_HAVE_A_TEAM)
                return self.set_response(
                    message=YOU_ALREADY_HAVE_A_TEAM,
                    status_code=status.HTTP_400_BAD_REQUEST,
                    status=400)

            members = get_user_model().objects.filter(
                email__in=request.data['emails'])
            if len(members) > 4 or len(members) < 1:
                return self.set_response(
                    message=COUNT_OF_USER_MEMBERS_MUST_BE_BETWEEN,
                    status_code=status.HTTP_409_CONFLICT,
                    status=409)
            for mem in members:
                if mem.team_role != 'NO':
                    return self.set_response(
                        message=USER_X_HAS_TEAM.format(user=mem.user_name),
                        status_code=status.HTTP_409_CONFLICT,
                        status=409)

            with transaction.atomic():

                team = Team.objects.create(
                    name=request.data['name'], team_activation=team_activation_code(request.data['name']))
                head.team_role = 'HE'
                head.team = team
                head.save()
                for mem in members:
                    team_data = {
                        'head_name': head.user_name,
                        'team_name': team.name,
                        'email': mem.email,
                        'first_name': mem.first_name,
                        'tid': team.team_activation,
                        'mid': urlsafe_base64_encode(force_bytes(mem.pk))
                    }
                    send_team_requests_task.delay(team_data)
                return self.set_response(data=self.serializer_class(team).data)

        except get_user_model().DoesNotExist as e:
            return self.set_response(error=str(e), status=400, status_code=400)

        except Exception as e2:
            return self.set_response(error=str(e2), status=500, status_code=500)

    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated])
    def enroll(self, request):
        competition = SingletonCompetition.get_solo()
        model_name = 'competition'
        service_type = 'CP'

        if not competition.is_registration_active:
            return self.set_response(
                error=f"{model_name} is inactive",
                status=406,
                message=INACTIVE,
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
            )
        if competition.get_remain_capacity() <= 0:
            return self.set_response(
                error=f"this {model_name} is full",
                status=406,
                message=CAPACITY_IS_FULL,
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
            )

        user = request.user
        team = request.user.team
        if not team or team.state != 'AC':
            return self.set_response(
                error=f"this team is not accepted",
                status=406,
                message=TEAM_NOT_ACCEPTED,
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
            )

        for member in team.members.all():
            args = {'user': member, model_name: competition, 'service_type': service_type, 'payment_state': 'CM'}
            query = EventService.objects.filter(**args)
            if query.exists():
                return self.set_response(
                    error=f"user has already enrolled in the {model_name}",
                    status=409,
                    message=USER_HAS_ALREADY_ENROLLED,
                    status_code=status.HTTP_409_CONFLICT,
                )

        args = {'user': user, model_name: competition, 'service_type': service_type, 'payment_state': 'PN'}
        ev_service = EventService.objects.create(**args)

        if competition.cost < 1:
            ev_service.payment_state = 'CM'
            ev_service.save()

            return self.set_response(
                message=SUCCESSFULLY_ADDED,
                data=EventServiceSerializer(ev_service).data,
            )
        else:
            total_price = competition.cost
            PayWallRequest = IdPayRequest if PAYWALL == "idpay" else PayPingRequest
            payment = Payment.objects.create(total_price=total_price, user=user)

            result = PayWallRequest().create_payment(
                order_id=payment.pk,
                amount=int(total_price * 10 if PAYWALL == "idpay" else total_price),
                desc=IDPAY_PAYMENT_DESCRIPTION if PAYWALL == 'idpay' else PayPing_PAYMENT_DESCRIPTION,
                mail=user.email,
                phone=user.phone_number,
                callback=IDPAY_CALL_BACK if PAYWALL == 'idpay' else PayPing_CALL_BACK,
                name=user.first_name
            )

            success_status = IDPAY_STATUS_201 if PAYWALL == "idpay" else PAYPING_STATUS_OK
            if result['status'] == success_status:
                ev_service.payment = payment
                ev_service.save()

                payment.created_date = datetime.now()
                payment.payment_link = (
                    result)['link'] if PAYWALL == "idpay" else PayPingPeymentLinkGenerator(result['code'])
                payment.save()

                if PAYWALL != 'idpay':
                    _status = result['status']
                    _code = result['code']
                    result = {
                        "link": PayPingPeymentLinkGenerator(_code),
                        "status": _status
                    }
                    return self.set_response(message=None, data=result, status_code=status.HTTP_200_OK)
            else:
                payment.delete()
                return self.set_response(
                    message=CREATING_PAYMENT_UNSUCCESS, data=result, status_code=status.HTTP_400_BAD_REQUEST,
                    error=[{"error_code": result['status']}])


def get_permissions(self):
    try:
        # return permission_classes depending on `action`
        return [permission() for permission in self.permission_classes_by_action[self.action]]
    except KeyError:
        # action is not set return default permission_classes
        return [permission() for permission in self.permission_classes]


class VerifyTeamRequestView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = get_user_model()

    def get(self, request, tid, mid):
        try:
            mid = force_str(urlsafe_base64_decode(mid))
            member = get_user_model().objects.get(pk=mid)
            team = Team.objects.get(team_activation=tid)

            if team.state == 'RJ':
                data = {
                    'message': TEAM_IS_REJECTED,
                    'error': None,
                    'status': 406,
                    'data': []
                }
                return Response(data=data, status=status.HTTP_406_NOT_ACCEPTABLE)

            if member.team_role != 'NO':
                data = {
                    'message': USER_ALREADY_HAS_A_TEAM,
                    'error': None,
                    'status': 409,
                    'data': []
                }
                return Response(data=data, status=status.HTTP_409_CONFLICT)
            members_num = team.members.count()
            if members_num >= 5:
                data = {
                    'message': TEAM_IS_FULL,
                    'error': None,
                    'status': 406,
                    'data': []
                }
                return Response(data=data, status=status.HTTP_406_NOT_ACCEPTABLE)

            with transaction.atomic():
                if team.state == 'RE' and members_num >= 1:
                    team.state = 'AC'
                    team.save()

                member.team_role = 'ME'
                member.team = team
                member.save()

            data = {
                'message': TEAM_ACTIVED,
                'error': None,
                'status': 202,
                'data': UserTeamSerializer(member).data
            }
            return Response(data=data, status=status.HTTP_202_ACCEPTED)
        except get_user_model().DoesNotExist as e:
            data = {
                'message': USER_NOT_FOUND,
                'error': str(e),
                'status': 400,
                'data': []
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        except Team.DoesNotExist as e1:
            data = {
                'message': TEAM_NOT_FOUND,
                'error': str(e1),
                'status': 400,
                'data': []
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e2:
            data = {
                'message': SOMETHING_IS_WRONG,
                'error': str(e2),
                'status': 400,
                'data': []
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
