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
class EventServiceSerialzer(serializers.ModelSerializer):

    class Meta:
        model = EventService
        fields = '__all__'

class TalksPageSerializer(serializers.ModelSerializer):

    def get_remain_capacity(self,obj):
        return obj.get_remain_capacity()

    remain_capacity=serializers.SerializerMethodField()

    presenter=PresenterSerializer()
    services= EventServiceSerialzer(many=True)

    class Meta:
        model = Talk
        fields = ['capacity','date','content','title','remain_capacity',
                  'participant_count','presenter','services','pk']
        extra_kwargs = {'pk': {'read_only': True}}

class WorkshopPageSerializer(serializers.ModelSerializer):
    presenter = PresenterSerializer()
    services = EventServiceSerialzer(many=True)

    class Meta:
        model = Workshop
        fields = ['capacity', 'date', 'content', 'title',
                  'participant_count', 'presenter', 'services', 'pk']
        extra_kwargs = {'pk': {'read_only': True}}










# # class GDUserSerializer(serializers.ModelSerializer):
# #     class Meta:
# #         model= GDUser
# #         fields=['user_name','phone_number','talks','workshops']

# #     user_name = serializers.SerializerMethodField('get_user_name')

# #     def get_user_name(self, obj):
# #         return obj.user.user_name
