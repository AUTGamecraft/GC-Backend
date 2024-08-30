#!/bin/sh

set -e

sh /scripts/migrate.sh
gunicorn --env DJANGO_SETTINGS_MODULE=GD.settings.production GD.wsgi:application --bind 0.0.0.0:8000
# python manage.py runserver 0.0.0.0:8000

# python manage.py collectstatic --noinput

# python manage.py migrate

#uwsgi --socket :8000 --master --enable-threads --module app.wsgi
