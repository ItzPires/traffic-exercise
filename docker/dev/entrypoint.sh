#!/bin/sh

# Wait for PostgreSQL to be ready
while ! nc -z db 5432; do
  sleep 1
done

# Always run migrations
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Upload default data
python init.py

# Start the Django server
python manage.py runserver 0.0.0.0:8000
