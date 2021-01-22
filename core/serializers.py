from core.models import (
    Talk,
    Workshop,
    Presenter,
    EventService
    )
from rest_framework import serializers




class PresenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Presenter
        fields = '__all__'

class TalksPageSerializer(serializers.ModelSerializer):
    presenters =serializers.ReadOnlyField(source='presenter_set')
    class Meta:
        model = Talk
        fields = ['capacity','date','content','title','participant_count']

class WorkshopPageSerializer(serializers.ModelSerializer):
    presenters =serializers.ReadOnlyField(source='presenter_set')
    class Meta:
        model = Workshop
        fields = ['capacity','date','content','title','participant_count']

class EventServiceSerialzer(serializers.ModelSerializer):
    talk = serializers.ReadOnlyField(source='talk.pk')
    workshop = serializers.ReadOnlyField(source = 'workshop.pk')
    class Meta:
        model = EventService
        fields = ['payment_state' , 'service']








# # class GDUserSerializer(serializers.ModelSerializer):
# #     class Meta:
# #         model= GDUser
# #         fields=['user_name','phone_number','talks','workshops']

# #     user_name = serializers.SerializerMethodField('get_user_name')

# #     def get_user_name(self, obj):
# #         return obj.user.user_name
