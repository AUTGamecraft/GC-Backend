from core.models import (
    Assistant,
    Talk,
    Workshop,
    Presenter,
    EventService,
    Coupon
)
from rest_framework import serializers

from user.serializers import CustomUserSerializer

from copy import deepcopy


class PresenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Presenter
        fields = [
            'first_name', 'last_name', 'email',
            'descriptions', 'linked_in', 'workshops',
            'talks', 'pk', 'profile'
        ]
        extra_kwargs = {'pk': {'read_only': True}}


class AssistantsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assistant
        fields = [
            'pk', 'first_name',
            'last_name', 'linked_in',
            'profile', 'role'
        ]
        extra_kwargs = {'pk': {'read_only': True}}


class TalksPageSerializer(serializers.ModelSerializer):

    def get_remain_capacity(self, obj):
        return obj.get_remain_capacity()

    remain_capacity = serializers.SerializerMethodField()
    presenters = PresenterSerializer(many=True)

    def get_level(self, obj):
        return obj.get_level_display()

    level = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Talk
        fields = ['capacity', 'start', 'end', 'content', 'title', 'remain_capacity',
                  'pk', 'cost', 'presenters', 'level', 'files', 'is_registration_active', 'presentation_link']
        extra_kwargs = {'pk': {'read_only': True},
                        'remain_capacity': {'read_only': True}, 'presentation_link': {'read_only': True}, }


class WorkshopPageSerializer(serializers.ModelSerializer):
    def get_remain_capacity(self, obj):
        return obj.get_remain_capacity()

    remain_capacity = serializers.SerializerMethodField()

    def get_level(self, obj):
        return obj.get_level_display()

    level = serializers.SerializerMethodField(read_only=True)

    presenters = PresenterSerializer(many=True)
    assistants = AssistantsSerializer(many=True)

    class Meta:
        model = Workshop
        fields = ['capacity', 'start', 'end', 'content', 'title', 'remain_capacity',
                  'presenters', 'assistants', 'pk', 'cost', 'level', 'files', 'is_registration_active']
        extra_kwargs = {'pk': {'read_only': True},
                        'remain_capacity': {'read_only': True}}


class WorkshopCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workshop
        fields = [
            'title', 'date', 'cost', 'is_registration_active'
        ]


class TalkCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Talk
        fields = [
            'title', 'date', 'cost', 'is_registration_active'
        ]


class EventServiceSerializer(serializers.ModelSerializer):

    def get_payment_state(self, obj):
        return obj.get_payment_state_display()

    payment_state = serializers.SerializerMethodField()

    def get_service_type(self, obj):
        return obj.get_service_type_display()

    service_type = serializers.SerializerMethodField()
    workshop = WorkshopPageSerializer(read_only=True)
    talk = TalksPageSerializer(read_only=True)

    class Meta:
        model = EventService
        fields = ['pk', 'user', 'workshop',
                  'payment_state', 'service_type', 'talk']


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'
