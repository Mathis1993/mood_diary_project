#! /bin/bash

# Expected to be run from the root of the repository

# Load the .env file
source .env

# Ensure the main branch is checked out
git checkout main

# Fetch the latest changes from the remote repository
git fetch

# Check for changes
if [ -n "$(git diff origin/main)" ]; then
  # If there are changes, pull the changes (resetting any local changes before pulling)
  git reset --hard origin/main
  git pull

  # Choose correct compose file
  rm docker-compose.yml
  cp ./infra/production/docker-compose.yml .
  cp ./infra/production/traefik_dynamic_conf.yml .

  # Ensure networks exist
  docker network create --driver bridge overlay || true
  docker network create --driver bridge web || true

  # Execute the Docker Compose commands
  docker login -u "$REGISTRY_USER" -p "$REGISTRY_TOKEN" "$REGISTRY_NAME"
  docker compose pull && docker compose up -d
  docker compose exec django python manage.py migrate
fi
