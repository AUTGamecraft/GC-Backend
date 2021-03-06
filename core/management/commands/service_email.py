from django.core.management.base import BaseCommand
from core.models import EventService ,Workshop , Talk
import json
import os 
class Command(BaseCommand):
    help = "saves users' email to the registered service json file in email_service folder"
    
    def add_arguments(self,parser):
        pass
    
    def handle(self ,*args, **kwargs):

        workshops = Workshop.objects.all()
        for workshop in workshops:
            services = EventService.objects.filter(
                workshop=workshop ,
                payment_state='CM' ,
                service_type='WS',
            ).select_related('user')
            emails = [
                {
                    'email':service.user.email,
                    'full_name':service.user.first_name
                }
                for service in services
            ]
            with open('service_email/workshop/{}.json'.format(workshop.title),'w') as file:
                json.dump(emails , file , ensure_ascii=False)
                
            
        talks = Talk.objects.all()
        for talk in talks:
            services = EventService.objects.filter(
                talk=talk ,
                payment_state='CM' ,
                service_type='TK',
            ).select_related('user')
            emails = [
                {
                    'email':service.user.email,
                    'full_name':service.user.first_name
                }
                for service in services
            ]
            with open('service_email/talk/{}.json'.format(talk.title),'w') as file:
                json.dump(emails , file , ensure_ascii=False)
        
            
        self.stdout.write(self.style.SUCCESS('emails saved'))
