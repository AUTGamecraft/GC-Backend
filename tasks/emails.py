from django.template import Context
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.utils.html import strip_tags


def send_email(user):
    context = {
        'first_name': user['first_name'],
        'uid': urlsafe_base64_encode(force_bytes(user['pk'])),
        'base_url':settings.BASE_URL
    }

    email_subject = 'Activation'
    html_message = render_to_string('activation_message.html', context)
    plain_message = render_to_string('activation_message.txt', context)

    msg = EmailMultiAlternatives(
        subject=email_subject,
        body=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user['email'], ],
    )
    msg.attach_alternative(html_message, 'text/html')
    msg.content_subtype = 'html'
    msg.mixed_subtype = 'related'
    msg.send()
    return {'success': True}


def send_team_request(team_data):
    context = team_data
    context['tid'] = urlsafe_base64_encode(force_bytes(team_data['tid']))
    context['mid'] = urlsafe_base64_encode(force_bytes(team_data['mid']))
    email_subject = 'Team Request'
    email_body = render_to_string('team_request_message.txt', context)
    email = EmailMessage(
        email_subject,
        email_body,
        settings.DEFAULT_FROM_EMAIL,
        [context['email'], ],
    )
    email.send(fail_silently=False)
    return {'success': True}
