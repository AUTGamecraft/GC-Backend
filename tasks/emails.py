from django.template import Context
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings

from django.utils.encoding import force_bytes
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.utils.html import strip_tags


def send_email(user):
    context = {
        'first_name': user['first_name'],
        'url':settings.BASE_URL + settings.REDIRECT_EMAIL_ACTIVATION.format(user['uid']) 
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
    context = {
        'url':settings.BASE_URL + settings.REDIRECT_TEAM_EMAIL_ACTIVATION.format(team_data['tid'] , team_data['mid']),
        'head_name':team_data['head_name'],
        'first_name':team_data['first_name'],
        'team_name':team_data['team_name']
    }
    email_subject = 'Team Request'
    email_body = render_to_string('team_request_message.txt', context)

    html_message = render_to_string('team_request_message.html', context)
    plain_message = render_to_string('team_request_message.txt', context)

    msg = EmailMultiAlternatives(
        subject=email_subject,
        body=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[team_data['email'], ],
    )
    msg.attach_alternative(html_message, 'text/html')
    msg.content_subtype = 'html'
    msg.mixed_subtype = 'related'
    msg.send()
    return {'success': True}
