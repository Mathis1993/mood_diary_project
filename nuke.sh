# This script will nuke your local database and reseed it with fresh data (for better DX)
STEP_COUNTER=0

echo -e "\n$((STEP_COUNTER += 1))) 💣 💣 Nuking local DB 💣 💣"

echo -e "\n$((STEP_COUNTER += 1))) 🚀 🚀 Launching django reset_db 🚀 🚀"
python manage.py reset_db --noinput # https://django-extensions.readthedocs.io/en/latest/reset_db.html
echo -e "\n$((STEP_COUNTER += 1))) 💥 💥 django database was reset 💥 💥"

echo -e "\n$((STEP_COUNTER += 1))) 🚂 🚂 starting django migrations 🚂 🚂 "
python manage.py migrate --noinput

echo -e "\n$((STEP_COUNTER += 1))) 🌱 🌱 Seeding django database 🌱 🌱"
python manage.py shell -c "
from mood_diary.seed_database import seed_database;
seed_database();"

echo -e "\n$((STEP_COUNTER += 1))) 🛫 🛫 You are all set up 🛫 🛫"
