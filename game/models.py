from django.db import models
from tinymce.models import HTMLField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from django.db.models.signals import pre_save
from django.dispatch import receiver
import os
# Create your models here.
main_dir = "game"

def get_game_path(instance, filename):
    return os.path.join(main_dir, filename)

class Game(models.Model):
    poster = models.ImageField(blank=True, null=True)
    title = models.CharField(max_length=512)
    description = HTMLField()
    game_link = models.CharField(max_length=512, blank=False, null=False)
    is_verified = models.BooleanField(default=False)
    team = models.OneToOneField('user.Team', on_delete=models.CASCADE, related_name='game', null=True)
    timestamp = models.DateTimeField(default=timezone.now, editable=False)

class Comment(models.Model):
    user = models.ForeignKey('user.SiteUser', on_delete=models.CASCADE, related_name='comments', null=False)
    game = models.ForeignKey('game.Game', on_delete=models.CASCADE, related_name='comments', null=False)
    text = models.CharField(max_length=512, blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now, editable=False)

class Like(models.Model):
    user = models.ForeignKey('user.SiteUser', on_delete=models.CASCADE, related_name='likes', null=False)
    game = models.ForeignKey('game.Game', on_delete=models.CASCADE, related_name='likes', null=False)
    is_deleted = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=timezone.now, editable=False)
    class Meta:
        # Each user can like a game just one time
        unique_together = ('user', 'game',)
    