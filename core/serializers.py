from core.models import (
    Talk,
    Workshop,
    Presenter,
    EventService,
    Team,
    CompetitionMember
)
from rest_framework import serializers

from user.serializers import CustomUserSerializer

from copy import deepcopy



class PresenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Presenter
        fields = [
            'first_name', 'last_name', 'email', 'descriptions', 'linked_in', 'workshops', 'talks', 'pk'
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
        fields = ['capacity', 'date', 'content', 'title', 'remain_capacity',
                  'participant_count', 'pk',  'cost', 'presenters', 'level']
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
        fields = ['capacity', 'date', 'content', 'title', 'remain_capacity',
                  'participant_count', 'presenters', 'pk', 'cost', 'level']
        extra_kwargs = {'pk': {'read_only': True},
                        'remain_capacity': {'read_only': True}}


class CompetitionMemberSerializer(serializers.ModelSerializer):
    site_user_pk = serializers.ReadOnlyField(source='user.pk')
    profile = serializers.SerializerMethodField(read_only=True )
    email = serializers.ReadOnlyField(source='user.email' )

    def get_profile(self , member):
        try:
            photo_url = member.user.profile.url
            return photo_url
        except ValueError:
            return None

    class Meta:
        model = CompetitionMember
        fields = [
            'team','user','has_team','is_head','pk','site_user_pk','profile','email'
        ]
        extra_kwargs = {'pk': {'read_only': True}}
        
            


class TeamSerialzer(serializers.ModelSerializer):
    def get_state(self, obj):
        return obj.get_state_display()
    state = serializers.SerializerMethodField()
    emails = serializers.ListField(
        write_only=True, child=serializers.EmailField())

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
    workshop = WorkshopCartSerializer(read_only=True)
    talk = TalkCartSerializer(read_only=True)

    class Meta:
        model = EventService
        fields = ['pk', 'user', 'workshop',
                  'payment_state', 'service_type', 'talk']
