#!/bin/bash


python manage.py makemigrations "$1"

python manage.py migrate core