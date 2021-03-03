from core.models import (
    Talk,
    Workshop,
    Presenter,
    EventService,
    Team,
    CompetitionMember,
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
            'talks', 'pk','profile'
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
                   'pk',  'cost', 'presenters', 'level','files']
        extra_kwargs = {'pk': {'read_only': True},
                        'remain_capacity': {'read_only': True}}


class WorkshopPageSerializer(serializers.ModelSerializer):
    def get_remain_capacity(self, obj):
        return obj.get_remain_capacity()
    remain_capacity = serializers.SerializerMethodField()

    def get_level(self, obj):
        return obj.get_level_display()
    level = serializers.SerializerMethodField(read_only=True)



    presenters = PresenterSerializer(many=True)

    class Meta:
        model = Workshop
        fields = ['capacity', 'start', 'end', 'content', 'title', 'remain_capacity',
                   'presenters', 'pk', 'cost', 'level','files']
        extra_kwargs = {'pk': {'read_only': True},
                        'remain_capacity': {'read_only': True}}


class CompetitionMemberSerializer(serializers.ModelSerializer):
    site_user_pk = serializers.ReadOnlyField(source='user.pk')
    profile = serializers.SerializerMethodField(read_only=True )
    email = serializers.ReadOnlyField(source='user.email' )
    first_name = serializers.ReadOnlyField(source='user.first_name' )
    last_name = serializers.ReadOnlyField(source='user.last_name' )
    

    def get_profile(self , member):
        try:
            photo_url = member.user.profile.url
            return photo_url
        except ValueError:
            return None

    class Meta:
        model = CompetitionMember
        fields = [
            'team','has_team','is_head','pk','site_user_pk','profile','email','first_name','last_name'
        ]
        extra_kwargs = {'pk': {'read_only': True}}
        
            


class TeamSerialzer(serializers.ModelSerializer):
    def get_state(self, obj):
        return obj.get_state_display()
    state = serializers.SerializerMethodField()
    emails = serializers.ListField(
        write_only=True, child=serializers.EmailField())
    members = CompetitionMemberSerializer(many=True)

    class Meta:
        model = Team
        fields = [
            'members', 'state', 'video', 'game', 'like', 'dislike', 'emails', 'name', 'pk'
        ]
        extra_kwargs = {'pk': {'read_only': True}}

    def create(self, validated_data):
        val = deepcopy(validated_data)
        val.pop('emails')
        team = Team.objects.create(**val)
        team.save()
        return team


class WorkshopCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workshop
        fields = [
            'title', 'date', 'cost'
        ]


class TalkCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Talk
        fields = [
            'title', 'date', 'cost'
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