from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User


class TalkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Talk

        fields =[
            'title',
            'content',
            'capacity',
            'participant_count'
        ]

