#! /bin/bash

docker compose exec django python manage.py shell_plus -c "from mood_diary.seed_database import seed_database_production; seed_database_production()"
