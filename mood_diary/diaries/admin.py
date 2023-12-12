"""
This file is used to register models to the djagno admin.
By doing this, admin users can manage the models via the django admin sites.
"""

from diaries.models import Activity, ActivityCategory
from django.contrib import admin

admin.site.register(ActivityCategory)
admin.site.register(Activity)
