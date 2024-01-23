# Dockerfile for the Django application
FROM python:3.12.1 AS base

# Working directory
RUN mkdir -p /app
WORKDIR /app

# Create a new user 'user' and give it sudo privileges (running as root is considered a security risk)
RUN useradd -m user && echo "user:user" | chpasswd && adduser user sudo

# Switch to 'user'
USER user

COPY ./requirements/. ./requirements/

# Install dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements/base.txt

COPY . .

# Ensure ownership and permissions
RUN chown -R user:user /app && \
    chmod +x /app/scripts/startup_django.sh

CMD ["scripts/startup_django.sh"]

FROM base AS staging

# Switch to 'user'
USER user

# Install dependencies
RUN pip install -r requirements/test.txt

CMD ["scripts/startup_django.sh"]
