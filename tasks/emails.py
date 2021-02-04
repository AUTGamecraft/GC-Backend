from django.template import Context
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

def send_email(user):
    context = {
        'first_name':user['first_name'],
        'uid':urlsafe_base64_encode(force_bytes(user['pk']))
    }

    email_subject = 'Activation'
    email_body = render_to_string('email_message.txt' , context)
    email = EmailMessage(
        email_subject,
        email_body,
        settings.DEFAULT_FROM_EMAIL,
        [user['email'],],
    )
    email.send(fail_silently=False)
    print(user)
    return {'status':True}