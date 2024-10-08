from copy import deepcopy

from rest_framework import serializers

from django.contrib.auth import get_user_model

from core.models import SingletonCompetition, EventService
from .models import (
    PhoneValidator,
    SiteUser,
    Team
)

User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    user_name = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    phone_number = serializers.CharField(
        required=True, validators=[PhoneValidator()])
    password = serializers.CharField(min_length=8, write_only=True)

    class Meta:
        model = get_user_model()
        fields = ('team_role', 'team', 'email', 'user_name', 'password',
                  'first_name', 'phone_number', 'profile', 'is_staff', 'favorite_game_title')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class UserTeamSerializer(serializers.ModelSerializer):

    def get_profile(self, member):
        try:
            photo_url = member.user.profile.url
            return photo_url
        except ValueError:
            return None

    class Meta:
        model = User
        fields = [
            'team', 'team_role', 'pk', 'profile', 'email', 'first_name', 'user_name'
        ]
        extra_kwargs = {'pk': {'read_only': True}}


class TeamSerializer(serializers.ModelSerializer):
    def get_state(self, obj):
        return obj.get_state_display()

    def get_payment_state(self, obj):
        return obj.get_payment_state()

    state = serializers.SerializerMethodField()
    payment_state = serializers.SerializerMethodField()
    emails = serializers.ListField(write_only=True, child=serializers.EmailField())
    members = UserTeamSerializer(many=True)

    class Meta:
        model = Team
        fields = ['members', 'state', 'emails', 'name', 'pk', 'payment_state']
        extra_kwargs = {'pk': {'read_only': True}, 'payment_state': {'read_only': True}}

    def create(self, validated_data):
        val = deepcopy(validated_data)
        val.pop('emails')
        team = Team.objects.create(**val)
        team.save()
        return team


class UserSerializerMinimal(serializers.ModelSerializer):
    class Meta:
        model = SiteUser
        fields = ('first_name', 'about', 'email', 'profile')
