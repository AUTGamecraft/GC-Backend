from __future__ import absolute_import, unicode_literals
from celery import shared_task
from .emails import (
    send_email,
    send_team_request,
    send_simple_email,
    change_pass_email,
    send_reminder_email
)


@shared_task
def send_email_task(user_data):
    return send_email(user_data)


@shared_task
def send_team_requests_task(team_data):
    return send_team_request(team_data)


@shared_task
def send_simple_email_task(data):
    return send_simple_email(data)


@shared_task
def change_pass_email_task(user_data):
    return change_pass_email(user_data)

@shared_task
def reminder_email_task(service_data):
    return send_reminder_email(service_data)