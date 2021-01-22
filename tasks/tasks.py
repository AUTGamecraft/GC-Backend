from __future__ import absolute_import , unicode_literals
from celery import shared_task
from .emails import send_email
from celery.utils.log import get_task_logger


logger = get_task_logger(__name__)


@shared_task
def send_email_task(user_data):
    # try:
    logger.info(f"sent review email to {user_data['user_name']}")
    return send_email(user_data)
    # except:
    #     logger.error('something wrong !!!')
    #     return None