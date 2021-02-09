from __future__ import absolute_import , unicode_literals
from celery import shared_task
from .emails import send_email
from celery.utils.log import get_task_logger




@shared_task
def send_email_task(user_data):
    try:
        return send_email(user_data)
    except Exception as e:
        print(str(e))
        return None

@shared_task
def send_team_requests_task(data):
    pass