from django.template.loader import render_to_string
from django.conf import settings

from django.core.mail import EmailMultiAlternatives
from django.core.mail import get_connection

connection = get_connection(
    backend=settings.ALT_EMAIL_BACKEND,
    fail_silently=False,
    username=settings.ALT_EMAIL_HOST_USER,
    use_tls=True,
    password=settings.ALT_EMAIL_HOST_PASSWORD,
    port=settings.ALT_EMAIL_PORT,
    host=settings.ALT_EMAIL_HOST
)


def send_simple_email(data):
    message = data['body']
    msg = None
    if 'yahoo' in data['email']:
        msg = EmailMultiAlternatives(
            subject=data['subject'],
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[data['email'], ],
            connection=connection
        )
    else:
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
    msg = None
    if 'yahoo' in user['email']:
        msg = EmailMultiAlternatives(
            subject=email_subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user['email'], ],
            connection=connection
        )
    else:
        msg = EmailMultiAlternatives(
            subject=email_subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user['email'], ]
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
    msg = None
    if 'yahoo' in team_data['email']:
        msg = EmailMultiAlternatives(
            subject=email_subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[team_data['email'], ],
            connection=connection
        )
    else:
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
        'url': settings.BASE_URL + settings.REDIRECT_EMAIL_CHANGE_PASSWORD.format(user['uid'])
    }
    email_subject = 'Gamecraft Password Reset'
    html_message = render_to_string('change_password_email.html', context)
    plain_message = render_to_string('change_password_email.html', context)
    msg = None
    if 'yahoo' in user['email']:
        msg = EmailMultiAlternatives(
            subject=email_subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user['email'], ],
            connection=connection
        )
    else:
        msg = EmailMultiAlternatives(
            subject=email_subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user['email'], ],
        )
    msg.attach_alternative(html_message, 'text/html')
    msg.send()
    return {'success': True, 'email': user['email']}
