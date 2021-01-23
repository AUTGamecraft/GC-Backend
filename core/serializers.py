from core.models import (
    Talk,
    Workshop,
    Presenter,
    EventService,
    Competition
    )
from rest_framework import serializers




class PresenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Presenter
        fields = '__all__'

class EventServiceSerializer(serializers.ModelSerializer):
    talk_title = serializers.ReadOnlyField(source='talk.title')
    workshop_title = serializers.ReadOnlyField(source='workshop.title')
    class Meta:
        model = EventService
        fields = '__all__'

class TalksPageSerializer(serializers.ModelSerializer):

    def get_remain_capacity(self,obj):
        return obj.get_remain_capacity()
    remain_capacity=serializers.SerializerMethodField()
    presenter=PresenterSerializer()

    class Meta:
        model = Talk
        fields = ['capacity','date','content','title','remain_capacity',
                  'participant_count','presenter','services','pk']
        extra_kwargs = {'pk': {'read_only': True}}

class WorkshopPageSerializer(serializers.ModelSerializer):
    def get_remain_capacity(self,obj):
        return obj.get_remain_capacity()
    remain_capacity=serializers.SerializerMethodField()
    presenter=PresenterSerializer()

    class Meta:
        model = Workshop
        fields = ['capacity', 'date', 'content', 'title',
                  'participant_count', 'presenter', 'services', 'pk']
        extra_kwargs = {'pk': {'read_only': True}}



class CompetitionPageSerializer(serializers.ModelSerializer):
    class Meta:
        Model = Competition
        extra_kwargs= {'pk': {'read_only': True}}