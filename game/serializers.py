from rest_framework import serializers
from django.db import transaction
from game.models import Game, Comment
from user.models import SiteUser, Team
from user.serializers import UserSerializerMinimal
from django.core.validators import MaxValueValidator, MinValueValidator
from user.serializers import TeamSerialzer
from rest_framework.exceptions import ValidationError

class CommentSerializer(serializers.ModelSerializer):
    game = serializers.PrimaryKeyRelatedField(
        queryset=Game.objects.filter(is_verified=True), required=True, write_only=False
    )
    user = serializers.PrimaryKeyRelatedField(
        queryset=SiteUser.objects.all(), required=True
    )
    score = serializers.IntegerField(
        required=True,
        write_only=False,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )

    def to_representation(self, obj):
        self.fields["user"] = UserSerializerMinimal()

        return super(CommentSerializer, self).to_representation(obj)

    class Meta:
        model = Comment
        fields = (
            "text",
            "score",
            "game",
            "user",
            "timestamp",
        )
        extra_kwargs = {
            "text": {
                "required": True,
                "write_only": False,
            },
            "score": {
                "required": True,
                "write_only": False,
            },
        }

    def validate(self, attrs):
        return super().validate(attrs)

    def create(self, validated_data):
        comment = Comment.objects.create(**validated_data)

        return comment

class GameSerializer(serializers.ModelSerializer):
    
    team = serializers.PrimaryKeyRelatedField(write_only=True, required=True, queryset=Team.objects.all())
    
    # title = serializers.CharField(read_only=True)
    game_id = serializers.CharField(read_only=True, source="pk")
    
    comments = CommentSerializer(read_only=True, many=True)

    def to_representation(self, obj):
        self.fields["team"] = TeamSerialzer()

        return super(GameSerializer, self).to_representation(obj)

    class Meta:
        model = Game
        fields = (
            "title",
            "poster",
            "description",
            "game_link",
            "team",
            "is_verified",
            "timestamp",
            "game_id",
            "comments",
        )
        extra_kwargs = {
            "title": {
                "required": True,
                "write_only": False,
            },
            "poster": {
                "required": True,
                "write_only": False,
            },
            "description": {
                "required": True,
                "write_only": False,
            },
            "game_link": {
                "required": True,
                "write_only": False,
            },
            "is_verified": {"read_only": True},
        }

    def validate(self, attrs):
        return super().validate(attrs)

    def create(self, validated_data):
        
        team_head = validated_data["team"].members.filter(team_role="HE")
        user_wants_to_create_game = self.context['request'].user
        print(user_wants_to_create_game)
        print(team_head)
        if user_wants_to_create_game not in team_head:
            raise ValidationError({"message": "User should be head of team"})
        
        if validated_data['team'].state != 'AC':
            raise ValidationError({"message": "Team is not activated yet"})
            
            
        with transaction.atomic():
                
            game = Game.objects.create(**validated_data)
            # game.save()

            return game

