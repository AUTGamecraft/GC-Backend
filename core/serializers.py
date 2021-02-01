from core.models import (
    Talk,
    Workshop,
    Presenter,
    EventService,
    Competition
    )
from rest_framework import serializers

from user.serializers import CustomUserSerializer





class PresenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Presenter
        fields = '__all__'

class EventServiceSerializer(serializers.ModelSerializer):

    def get_talk(self, obj):
        t:Talk=obj.talk
        if t is None:
            return None
        return {
            'id':t.id,
            'title':t.title,
            'cost':t.cost
        }
    talk = serializers.SerializerMethodField()

    def get_workshop(self, obj):
        w:Workshop=obj.workshop
        if w is None:
            return None
        return {
            'id':w.id,
            'title':w.title,
            'cost':w.cost
        }
    workshop = serializers.SerializerMethodField()


    user=CustomUserSerializer()

    def get_payment_state(self,obj):
        return obj.get_payment_state_display()
    payment_state=serializers.SerializerMethodField()

    def get_service_type(self,obj):
        return obj.get_service_type_display()
    service_type=serializers.SerializerMethodField()

    class Meta:
        model = EventService
        fields = ['id','user','workshop','payment_state','service_type','talk']

class TalksPageSerializer(serializers.ModelSerializer):

    def get_remain_capacity(self,obj):
        return obj.get_remain_capacity()

    remain_capacity=serializers.SerializerMethodField()
    presenter=PresenterSerializer(read_only=True)
    presenter_id=serializers.IntegerField(write_only=True)


    class Meta:
        model = Talk
        fields = ['capacity','date','content','title','remain_capacity',
                  'participant_count','presenter','pk','presenter_id','cost']
        extra_kwargs = {'pk': {'read_only': True},
                        'presenter_id':{'write_only':True},
                        'remain_capacity':{'read_only':True}}

    def create(self, validated_data):
        presenter_id=self.initial_data['presenter_id']
        try:
            p=Presenter.objects.get(id=presenter_id)
        except  Presenter.DoesNotExist:
            raise  serializers.ValidationError("no any presenter with this id")
        talk=Talk(**validated_data)
        talk.presenter=p
        talk.save()
        return talk

class WorkshopPageSerializer(serializers.ModelSerializer):
    def get_remain_capacity(self, obj):
        return obj.get_remain_capacity()

    remain_capacity = serializers.SerializerMethodField()
    presenter = PresenterSerializer(read_only=True)
    presenter_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Workshop
        fields = ['capacity', 'date', 'content', 'title', 'remain_capacity',
                  'participant_count', 'presenter', 'pk', 'presenter_id','cost']
        extra_kwargs = {'pk': {'read_only': True},
                        'presenter_id': {'write_only': True},
                        'remain_capacity': {'read_only': True}}

        def create(self, validated_data):
            presenter_id = self.initial_data['presenter_id']
            p = Presenter.objects.get(id=presenter_id)
            work_shop = Workshop(**validated_data)
            work_shop.presenter = p
            work_shop.save()
            return work_shop


class CompetitionPageSerializer(serializers.ModelSerializer):
    class Meta:
        Model = Competition
        extra_kwargs= {'pk': {'read_only': True}}