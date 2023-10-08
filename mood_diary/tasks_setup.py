"""
This file configures Celery for the mood diary project, auto-discovering functions
annotated as tasks and registering periodic tasks.
"""

import os

from celery import Celery
from celery.schedules import crontab

app = Celery("mood_diary", broker=os.getenv("CELERY_BROKER_URL"))

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Register periodic tasks
celery_beat_schedule = {
    "Evaluation of time-based rules": {
        "task": "diaries.tasks.task_time_based_rules_init",
        "schedule": crontab(hour="6", minute="0"),
    },
}
app.conf.beat_schedule = celery_beat_schedule
