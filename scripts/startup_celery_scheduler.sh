#! /bin/sh

# Celery scheduler startup script
export DJANGO_SETTINGS_MODULE=config.settings.base
celery -A mood_diary beat -l INFO
