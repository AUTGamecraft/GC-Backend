from django.core.management.base import BaseCommand
import json
from tasks.tasks import send_simple_email_task
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from django.template.exceptions import TemplateDoesNotExist


class Command(BaseCommand):
    help = 'send email to all users !!!'

    def add_arguments(self, parser):
        parser.add_argument('body', type=str, help='html or txt file name')
        parser.add_argument('subject', type=str, help='subject of email')

    def handle(self, *args, **kwargs):
        body = kwargs['body']
        subject = kwargs['subject']
        data = None
        try:
            data = {
                'email': None,
                'body': render_to_string(body, None),
                'subject': subject
            }
        except TemplateDoesNotExist as e:
            self.stdout.write(self.style.ERROR("template doesn't exist"))
            exit()

        users = get_user_model().objects.filter(is_active=True, is_staff=False)
        for user in users:
            data['email'] = user.email
            send_simple_email_task.delay(data)
            self.stdout.write('sending to {} ......'.format(data['email']))
