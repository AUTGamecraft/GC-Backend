from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import json
import os 
class Command(BaseCommand):
    help = "saves users' information to a json file named users.json"
    
    def add_arguments(self,parser):
        pass
    
    def handle(self ,*args, **kwargs):

        data = [
            {
                'full_name':user.full_name,
                'email':user.email,
                'phone_number': user.phone_number
            }
            for user in get_user_model().objects.filter(is_active=True, is_staff=False)
        ]
        with open('users.json','w') as file:
            json.dump(data , file , ensure_ascii=False)
         