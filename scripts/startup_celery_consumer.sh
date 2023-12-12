#! /bin/sh

# Celery consumer startup script
export DJANGO_SETTINGS_MODULE=config.settings.base
celery -A mood_diary worker -l INFO
