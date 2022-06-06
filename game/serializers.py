from rest_framework import serializers
from django.db import transaction
from game.models import Game, Comment
from user.models import SiteUser
from user.serializers import UserSerializerMinimal
from django.core.validators import MaxValueValidator, MinValueValidator


class GameSerializer(serializers.ModelSerializer):
    creator = serializers.PrimaryKeyRelatedField(
        queryset=SiteUser.objects.all(), required=True
    )
    other_creators = serializers.PrimaryKeyRelatedField(
        queryset=SiteUser.objects.all(), many=True, required=False
    )
    # title = serializers.CharField(read_only=True)
    game_id = serializers.CharField(read_only=True, source="pk")

    def to_representation(self, obj):
        self.fields["creator"] = UserSerializerMinimal()
        self.fields["other_creators"] = UserSerializerMinimal(many=True)

        return super(GameSerializer, self).to_representation(obj)

    class Meta:
        model = Game
        fields = (
            "title",
            "poster",
            "description",
            "game_link",
            "creator",
            "other_creators",
            "is_verified",
            "timestamp",
            "game_id",
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
        with transaction.atomic():
            other_creators = validated_data.pop("other_creators", [])
            print(other_creators)
            game = Game.objects.create(**validated_data)
            # game.save()

            for creator in other_creators:
                # print(creator)
                game.other_creators.add(creator)
            game.save()

            return game


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
