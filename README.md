# Mood Diary Application
Author: Mathis Erichsen

This is my bachelor thesis' software development project.

## Description

The mood diary application is a digital version of the mood diary intervention as used in psychotherapy and psychological counseling with some advanced features.

It is developed for the Psychosoziale Beratungsstelle des Studentenwerks Osnabrück.

The application was developed following three main goals:
1. develop a digital application for the mood diary intervention available on a smartphone to ensure client compliance that additionally
2. makes mood diary entries accessible to counselors and
3. provides swift feedback about them to clients through automatic analyses.

There are three types of users:
1. admin users
   - can use the django admin interface to
     - create counselor users
     - maintain activities and activity categories
     - update client to counselor assignment
2. counselor users
    - can create client users
    - can set clients to inactive
    - can view their clients' mood diary entries released to them
3. client users
    - can create, read, update and delete mood diary entries
    - can release mood diary entries to their counselor
    - can receive automatic feedback about their mood diary entries
    - can enable and disable rules for automatic feedback
    - can receive in-app and push notifications about automatic feedback

## Technical Details
The application is based on the following technology stack:
1. Django
2. PostgreSQL
3. Celery (with Redis broker)
4. Docker
5. GitLab CI/CD
6. PWA Enhancement

## Get Up and Running
To locally run the application, please follow the steps outlined below.

### Prerequisites
- Docker and Docker Compose installed
- Python 3.11 or higher installed

### Initial Setup
1. Clone the repository
2. Create a virtual environment and activate it
```shell
python3 -m venv venv
source venv/bin/activate
```
3. Install the requirements
```shell
pip install -r requirements/local.txt
```
4. Copy the .env-sample file to .env
```shell
cp .env-sample .env
```
Note that in order to send emails (for example when creating a client user), the environment variables `SENDGRID_API_KEY` and `FROM_EMAIL` need to be set.
Push notifications only work when the application is served over HTTPS and also require further environment variables.

### Run the Services
1. Start the database and the Redis broker
```shell
docker-compose up -d
```

### Seed the Database
1. Run the nuke script (will renew and migrate the database schema, then seed it)
```shell
bash nuke.sh
```
This will create
- an admin user
  - email: `mathis@mood-diary.de`
  - password: `TEST_USER_PASSWORD` (defined in `config/settings/test.py`)
- a counselor user
  - email: `user0@example.com`
  - password: `TEST_USER_PASSWORD`
- a client user
  - email: `user1@example.com`
  - password: `TEST_USER_PASSWORD`

### Run the Application
1. Start the Django development server
```shell
python manage.py runserver
```

#### Mobile Device View
To view the application as it would appear on a mobile device, in Chrome, you can open the developer tools and toggle the device toolbar (second icon in the top-left corner).

## Tests
To execute tests, ensure you have test requirements installed.
With your virtual environment activated, run
```shell
pip install -r requirements/test.txt
```
Then, run the tests with
```shell
pytest
```
