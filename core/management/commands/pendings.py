from django.core.management.base import BaseCommand
from core.models import EventService
import json

class Command(BaseCommand):
    help = "saves users' email with pending workshop in their cart!!!"
    
    def add_arguments(self,parser):
        pass
    
    def handle(self ,*args, **kwargs):
        services = EventService.objects.select_related('user').filter(payment_state='PN',service_type='WS')
        emails = set()
        for service in services:
            emails.add(service.user.email)
        
        with open("emails.json" , 'w') as file:
            json.dump(list(emails),file)
            
        self.stdout.write(self.style.SUCCESS('emails saved'))