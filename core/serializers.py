from rest_framework import serializers


class TalkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Talk

        fields =[
            'title',
            'content',
            'capacity',
            'participant_count'
        ]

