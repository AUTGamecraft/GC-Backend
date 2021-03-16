from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .models import Team



@receiver(pre_delete , sender=Team)
def handle_team_delete(sender , instance,**kwargs):
    mems = instance.members
    for mem in mems:
        mem.team_role = 'NO'
        mem.save()
  