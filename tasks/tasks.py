from __future__ import absolute_import , unicode_literals

from celery import shared_task


@task(name="send_email_task")
def add(x,y):
    return x+y