from .base import *  # noqa: F401 F403

TEST_USER_PASSWORD = "password1"

# python manage.py runserver 0.0.0.0:8000 and local machine's host name in ALLOWED_HOSTS
# to connect from phone via host-name:8000/...
ALLOWED_HOSTS = ["baby-yoda.local", "localhost"]

FROM_EMAIL = "test@test.de"
