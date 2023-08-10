FROM python:3.11 AS base

# Working directory
RUN mkdir -p /app
WORKDIR /app

# Copy relevant files and directories
COPY ./config/. ./
COPY ./mood_diary/. ./
COPY ./requirements/. ./
COPY ./scripts/. ./
COPY docker-compose.yml .
COPY manage.py .
COPY pyproject.toml .

# Ensure ownership and permissions (first linux user has usually id 1000)
RUN chown -R 1000:1000 /app && \
    chmod +x /app/scripts/startup_django.sh

FROM base AS staging

# Copy test/staging specific files
COPY .flake8 .
COPY nuke.sh .

# Install dependencies
RUN pip install -r requirements/test.txt

CMD ["scripts/startup_django.sh"]

FROM base AS prod

# Install dependencies
RUN pip install -r requirements/base.txt

CMD ["scripts/startup_django.sh"]
