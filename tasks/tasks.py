from __future__ import absolute_import , unicode_literals
from celery import shared_task
from .emails import (
    send_email,
    send_team_request
    )
from celery.utils.log import get_task_logger




@shared_task
def send_email_task(user_data):
    return send_email(user_data)

@shared_task
def send_team_requests_task(team_data):
    return send_team_request(team_data)
    