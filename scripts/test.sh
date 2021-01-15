#!/bin/bash
coverage run --omit='*/venv/*' manage.py 'test'

coverage html