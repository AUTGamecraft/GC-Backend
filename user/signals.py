from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .models import Team 
from django.contrib.auth import get_user_model




@receiver(pre_delete , sender=Team)
def handle_team_delete(sender , instance,**kwargs):
    get_user_model().objects.filter(team=instance).update(team_role='NO')
  