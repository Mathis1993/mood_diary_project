# Load the .env file
source .env

# Navigate to the repository directory
cd "$REPO_DIR" || exit

# Ensure the main branch is checked out
git checkout main

# Fetch the latest changes from the remote repository
git fetch

# Check for changes
if [ -n "$(git diff origin/main)" ]; then
  # If there are changes, pull the changes
  git pull

  # Choose correct compose file
  rm docker-compose.yml
  cp ./infra/production/docker-compose.yml .

  # Execute the Docker Compose commands
  docker login -u "$REGISTRY_USER" -p "$REGISTRY_TOKEN" "$REGISTRY_NAME"
  docker compose pull && docker compose up -d
  docker compose exec django python manage.py migrate
fi
