import json
from datetime import datetime

from rest_framework import generics, mixins, views

from GD.messages import WORKSHOP_CAPACITY_IS_FULL, SHOPPING_CART_EMPTY, COUPON_FINISHED, COUPON_DOSE_NOT_EXIST, \
    CREATING_PAYMENT_UNSUCCESS, EMPTY, ADDED_TO_COMPETITION, ALREADY_REGISTERED_IN_THE_COMPETITION, \
    REQUESTED_USER_IS_NOT_REGISTERED_OR_ALREADY_HAS_A_TEAM, YOU_ALREADY_HAVE_A_TEAM, \
    COUNT_OF_USER_MEMBERS_MUST_BE_BETWEEN, USER_X_HAS_TEAM, USER_ALREADY_HAS_A_TEAM, TEAM_ACTIVED, USER_NOT_FOUND, \
    TEAM_NOT_FOUND, SOMETHING_IS_WRONG, TEAM_IS_FULL
from .idpay import IdPayRequest, IDPAY_PAYMENT_DESCRIPTION, \
    IDPAY_CALL_BACK, IDPAY_STATUS_201, IDPAY_STATUS_100, IDPAY_STATUS_101, \
    IDPAY_STATUS_200, IDPAY_STATUS_10
from .payping import *
from GD.settings.base import PAYWALL
from django.shortcuts import get_object_or_404, redirect
from .viewsets import *
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from itertools import chain


class TalkViewSet(ServicesModelViewSet):
    queryset = Talk.objects.all().order_by("start")
    serializer_class = TalksPageSerializer
    model = Talk
    service_type = 'TK'


class WorkshopViewSet(ServicesModelViewSet):
    queryset = Workshop.objects.all().order_by('start')
    serializer_class = WorkshopPageSerializer
    model = Workshop
    service_type = 'WS'


class UserServicesViewSet(ResponseModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = EventService.objects.all()
    serializer_class = EventServiceSerializer

    permission_classes_by_action = {
        'create': [IsAdminUser],
        'list': [IsAdminUser],
        'retrive': [IsAuthenticated],
        'destroy': [IsAuthenticated],
        'update': [IsAuthenticated],
    }

    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
    def cart(self, request):
        user = request.user
        services = EventService.objects.filter(
            user=user, payment_state='PN', service_type='WS')
        data = EventServiceSerializer(services, many=True)
        return self.set_response(data=data.data)

    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
    def dashboard(self, request):
        user = request.user
        query1 = EventService.objects.filter(
            user=user, payment_state='CM', service_type='WS').order_by('workshop__start')
        query2 = EventService.objects.filter(
            user=user, service_type='TK').order_by('talk__start')
        services = list(chain(query2, query1))
        data = EventServiceSerializer(services, many=True)
        return self.set_response(data=data.data)

    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated])
    def payment(self, request):
        # return Response({"paywall": PAYWALL})
        data = defaultdict(lambda:None , request.data)
        user = request.user
        services = EventService.objects.filter(
            user=user, service_type='WS',payment_state='PN').select_related('workshop')
        total_price = 0
        # check capacity to register
        for service in services:
            event = service.workshop
            if event.get_remain_capacity() > 0:
                total_price += event.cost
            else:
                return self.set_response(message=event.title+WORKSHOP_CAPACITY_IS_FULL, status_code=status.HTTP_406_NOT_ACCEPTABLE, error=f"event {event.title} is full you must remove it!!!")
        # create payment object
        if total_price <= 0:
            return self.set_response(message=SHOPPING_CART_EMPTY)
        coupon = None
        if data['coupon']:
            try:
                coupon = Coupon.objects.get(name=data['coupon'])
                # if Payment.objects.filter(user=user , coupon=coupon,status__in=[IDPAY_STATUS_100, IDPAY_STATUS_101, IDPAY_STATUS_200]).exists():
                #     return self.set_response(
                #         message="شما از این کد تخفیف قبلا استفاده کرده اید.",
                #         error="coupon already used !!!",
                #         status_code=status.HTTP_406_NOT_ACCEPTABLE,
                #         status=406
                #     )
                if coupon.count > 0:
                    total_price = total_price * ((100 - coupon.percentage)/100)
                    coupon.count -= 1
                    coupon.save()
                else:
                    return self.set_response(
                        message=COUPON_FINISHED,
                        error="coupon finished",
                        status_code=status.HTTP_406_NOT_ACCEPTABLE,
                        status=406
                    )
            except Coupon.DoesNotExist as e:
                return self.set_response(
                    message=COUPON_DOSE_NOT_EXIST,
                    error="coupon does not exist",
                    status_code=status.HTTP_406_NOT_ACCEPTABLE,
                    status=406
                )
        payment = Payment.objects.create(
            total_price=total_price,
            user=user
        )

        PayWallRequest = IdPayRequest if PAYWALL=="idpay" else PayPingRequest
        
        result = PayWallRequest().create_payment(
            order_id=payment.pk,
            amount=int(total_price*10 if PAYWALL=="idpay" else total_price),
            desc=IDPAY_PAYMENT_DESCRIPTION if PAYWALL=='idpay' else PayPing_PAYMENT_DESCRIPTION,
            mail=user.email,
            phone=user.phone_number,
            callback= IDPAY_CALL_BACK if PAYWALL=='idpay' else PayPing_CALL_BACK,
            # mail=user.email,
            name=user.first_name
        ) 
        # return Response(result)

        success_status = IDPAY_STATUS_201 if PAYWALL=="idpay" else PAYPING_STATUS_OK
        if result['status'] == success_status:
            payment.services.set(services)
            payment.created_date = datetime.now()
            payment.payment_id = result['id'] if PAYWALL == "idpay" else result['data']['order']
            payment.payment_link = result['link'] if PAYWALL=="idpay" else PayPingPeymentLinkGenerator(result['data']['order'])
            payment.coupon = coupon
            payment.save()
        if PAYWALL != 'idpay':
            _code = result['data']['order']
            _status = result['status']
            result = {
                "link": PayPingPeymentLinkGenerator(_code),
                "status": _status
            }
            return self.set_response(
                message=None, data=result, status_code=status.HTTP_200_OK
            )
            # return redirect('http://autgamecraft.ir')
        else:
            payment.delete()
            if coupon:
                coupon.count += 1
                coupon.save()
            return self.set_response(
                message=CREATING_PAYMENT_UNSUCCESS, data=result, status_code=status.HTTP_400_BAD_REQUEST,
                error=[{"error_code": result['status']}]

            )

    @action(methods=['GET'], detail=False, permission_classes=[AllowAny])
    def verify(self, request):
        if PAYWALL == 'idpay':
            try:
                request_body = request.data
                idPay_payment_id = request_body['id']
                order_id = request_body['order_id']
                payment = Payment.objects.get(pk=order_id)
                payment.card_number = request_body['card_no']
                payment.hashed_card_number = request_body['hashed_card_no']
                payment.payment_trackID = request_body['track_id']
                result = IdPayRequest().verify_payment(
                    order_id=order_id,
                    payment_id=idPay_payment_id,
                )
                result_status = result['status']

                if any(result_status == status_code for status_code in (IDPAY_STATUS_100, IDPAY_STATUS_101, IDPAY_STATUS_200)):
                    services = EventService.objects.select_related(
                        'workshop').filter(payment=payment)
                    for service in services:
                        service.payment_state = 'CM'
                        service.workshop.save()
                        service.save()
                    payment.status = result_status
                    payment.original_data = json.dumps(result)
                    payment.verify_trackID = result['track_id']
                    payment.finished_date = datetime.utcfromtimestamp(
                        int(result['date']))
                    payment.verified_date = datetime.utcfromtimestamp(
                        int(result['verify']['date']))
                    payment.save()
                    return redirect('https://autgamecraft.ir/dashboard-event/?status=true')
                else:
                    if payment.coupon:
                        coupon = payment.coupon 
                        coupon.count += 1
                        coupon.save()
                        
                    payment.status = result_status
                    payment.original_data = json.dumps(result)
                    payment.save()
                    return redirect('https://autgamecraft.ir/dashboard-event/?status=false')

            except Payment.DoesNotExist as e1:
                raise ValidationError('no payment with this order_id')
            except ConnectionError as e:
                self.verify(request)
        else:
            try:
#		print('here')
                # print(request.data)
                # print(request.POST)
                _payment = Payment.objects.get(pk=request.GET.get('clientrefid'))
                print(_payment)
                result = PayPingRequest().verify_payment(_payment.payment_id)
                print(result['status'])
                
                result_body = result['data']
                if result['status'] != 200:
                    if _payment.coupon:
                        _payment.coupon.count +=1
                        _payment.coupon.save()
                    _payment.status = 1
                    _payment.original_data = json.dumps(result['data'])
                    return redirect('https://autgamecraft.ir/dashboard-event/?status=false')
		
                elif result['status'] == 200:
                    _payment.payment_id = result_body['refid']
                    _payment.card_number = result_body['card_number']
                    _payment.hashed_card_number = ""
                    _payment.payment_trackID = _payment.payment_id
                    services = EventService.objects.select_related('workshop').filter(payment=_payment)
                    for service in services:
                        service.payment_state = 'CM'
                        service.workshop.save()
                        service.save()
                    _payment.status = result['status']
                    _payment.original_data = json.dumps(result)
                    _payment.verify_trackID = _payment.payment_id
                    _payment.verified_date = datetime.now()
                    _payment.finished_date = datetime.now()
                    _payment.save()
                    
                    return redirect('https://autgamecraft.ir/dashboard-event/?status=true')
                # request_body = request.POST
                # if len(request_body.keys()) == 3:
                #     _payment = Payment.objects.get(pk=request_body['clientrefid'])
                #     if _payment.coupon:
                #         coupon = payment.coupon
                #         coupon.count += 1
                #         coupon.save()
                #     _payment.status = 1
                #     _payment.original_data = json.dumps(request_body)
                #     _payment.save()
                #     return redirect('https://autgamecraft.ir/dashboard-event/?status=false')
                
                # payment_id = request_body['refid']
                # code = request_body['code']
                # order_id = request_body['clientrefid']
                # payment = Payment.objects.get(pk=order_id)
                # payment.card_number = request_body['cardnumber']
                # payment.hashed_card_number = request_body['cardhashpan']
                # payment.payment_trackID = payment_id
                # payment.payment_id = payment_id
                # amount = int(payment.total_price)
                # result = PayPingRequest().verify_payment(
                #     amount,
                #     payment_id
                # )
                # result_status = result['status']
                # if result_status == PAYPING_STATUS_OK:
                #     services = EventService.objects.select_related('workshop').filter(payment=payment)
                #     for service in services:
                #         service.payment_state = 'CM'
                #         service.workshop.save()
                #         service.save()
                #     payment.status = result_status
                #     payment.original_data = json.dumps(result)
                #     payment.verify_trackID = payment_id
                #     payment.verified_date = datetime.now()
                #     payment.finished_date = datetime.now()
                #     payment.save()
                #     return redirect('https://autgamecraft.ir/dashboard-event/?status=true')
                # else:
                #     if payment.coupon:
                #         coupon = payment.coupon
                #         coupon.count += 1
                #         coupon.save()
                #     payment.status = result_status
                #     payment.original_data = json.dumps(result)
                #     payment.save()
                #     return redirect('https://autgamecraft.ir/dashboard-event/?status=false')

            except Payment.DoesNotExist as e1:
                raise ValidationError('no payment with this order_id')
            except ConnectionError as e:
                self.verify(request)

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


class CouponViewSet(ResponseGenericViewSet,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    mixins.ListModelMixin,
                    mixins.RetrieveModelMixin):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes_by_action = {
        'list': [IsAdminUser],
        'retrive': [IsAuthenticated],
        'destroy': [IsAdminUser],
        'update': [IsAdminUser],
    }
    lookup_field = 'name'

    def retrieve(self, request, *args, **kwargs):
        try:
            response_data = super(CouponViewSet, self).retrieve(
                request, *args, **kwargs)
            self.response_format["data"] = response_data.data
            self.response_format["status"] = 200
            if not response_data.data:
                self.response_format["message"] = EMPTY
            return Response(self.response_format)
        except Coupon.DoesNotExist as e:
            return self.set_response(
                message=COUPON_DOSE_NOT_EXIST,
                error="coupon doesn't exist",
                status=404,
                status_code=status.HTTP_404_NOT_FOUND
            )

    def list(self, request, *args, **kwargs):
        response_data = super(CouponViewSet, self).list(
            request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        self.response_format["status"] = 200
        if not response_data.data:
            self.response_format["message"] = EMPTY
        return Response(self.response_format)

    def update(self, request, *args, **kwargs):
        response_data = super(CouponViewSet, self).update(
            request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        self.response_format["status"] = 200

        return Response(self.response_format)

    def destroy(self, request, *args, **kwargs):
        response_data = super(CouponViewSet, self).destroy(
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
