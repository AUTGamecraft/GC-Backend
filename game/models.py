from django.db import models
from tinymce.models import HTMLField
from django.core.validators import MaxValueValidator, MinValueValidator
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
    creators = models.ManyToManyField('user.SiteUser')
    

class Comment(models.Model):
    user = models.ForeignKey('user.SiteUser', on_delete=models.CASCADE, related_name='comments', null=False)
    game = models.ForeignKey('game.Game', on_delete=models.CASCADE, related_name='comments', null=False)
    text = models.CharField(max_length=512, blank=True, null=True)
    score = models.IntegerField(
        validators=[MaxValueValidator(5), MinValueValidator(1)], default=5
    )
    class Meta:
        unique_together = ('user', 'game',)
    