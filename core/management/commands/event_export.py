from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import json
import os 
from core.models import Talk, Workshop, EventService, PAYMENT_STATES

class Command(BaseCommand):
    help = "saves event(or workshop) register record into event_export_*.json"
    
    def add_arguments(self,parser):
        # parser.add_argument('event_id', type=int, help='Indicates the event_id')
        parser.add_argument('is_talk', type=int, help='Indicates that this ID is for Talk or Workshop')

    
    def handle(self ,*args, **kwargs):
        is_talk =  kwargs['is_talk']
        # event_id =  kwargs['event_id']
        print("heh")
        
        events = None
        if is_talk:
            events = Talk.objects.all()
        else:
            events = Workshop.objects.all()
            
        register_records = None
        for event in events:
            if is_talk:
                register_records = EventService.objects.filter(talk=event, payment_state=PAYMENT_STATES[0][0])
            else:
                register_records = EventService.objects.filter(workshop=event, payment_state=PAYMENT_STATES[0][0])
                
            data = [
                {
                    'full_name':record.user.first_name,
                    'email':record.user.email,
                    'phone_number': record.user.phone_number
                }
                for record in register_records
            ]
            with open(f'event_export_{event.title}.json','w') as file:
                json.dump(data , file , ensure_ascii=False)
            
            
         