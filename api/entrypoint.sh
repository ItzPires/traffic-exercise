#!/bin/sh

# Wait for PostgreSQL to be ready
while ! nc -z db 5432; do
  sleep 1
done

# Migrations
python manage.py makemigrations
python manage.py migrate

# Start the Django server
python manage.py runserver 0.0.0.0:8000
