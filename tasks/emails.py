from django.template.loader import render_to_string
from django.conf import settings

from django.core.mail import EmailMultiAlternatives


def send_simple_email(data):
    message = data['body']
    msg = EmailMultiAlternatives(
        subject=data['subject'],
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[data['email'], ]
    )
    msg.attach_alternative(message, 'text/html')
    msg.send()
    return {
        'message': 'successfully sent to : {}'.format(data['email'])
    }


def send_email(user):
    context = {
        'first_name': user['first_name'],
        'url': settings.BASE_URL + settings.REDIRECT_EMAIL_ACTIVATION.format(user['uid'])
    }
    email_subject = 'Gamecraft Activation'
    html_message = render_to_string('activation_message.html', context)
    plain_message = render_to_string('activation_message.html', context)
    msg = EmailMultiAlternatives(
        subject=email_subject,
        body=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user['email'], ],
    )
    msg.attach_alternative(html_message, 'text/html')
    msg.send()
    return {'success': True, 'email': user['email']}


def send_team_request(team_data):
    context = {
        'url': settings.BASE_URL + settings.REDIRECT_TEAM_EMAIL_ACTIVATION.format(team_data['tid'], team_data['mid']),
        'head_name': team_data['head_name'],
        'first_name': team_data['first_name'],
        'team_name': team_data['team_name']
    }
    email_subject = 'Gamecraft Team Request'

    html_message = render_to_string('team_request_message.html', context)
    plain_message = render_to_string('team_request_message.html', context)

    msg = EmailMultiAlternatives(
        subject=email_subject,
        body=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[team_data['email'], ],
    )
    msg.attach_alternative(html_message, 'text/html')
    msg.send()
    return {'success': True, 'email': team_data['email']}


def change_pass_email(user):
    context = {
        'first_name': user['first_name'],
        'url': settings.BASE_URL + settings.REDIRECT_CHANGE_PASSWORD.format(user['uid'])
    }
    email_subject = 'Gamecraft Password Reset'
    html_message = render_to_string('change_password_email.html', context)
    plain_message = render_to_string('change_password_email.html', context)

    msg = EmailMultiAlternatives(
        subject=email_subject,
        body=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user['email'], ],
    )
    msg.attach_alternative(html_message, 'text/html')
    msg.send()
    return {'success': True, 'email': user['email']}
