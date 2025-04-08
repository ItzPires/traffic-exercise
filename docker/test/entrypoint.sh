#!/bin/sh

# Wait for PostgreSQL to be ready
while ! nc -z db 5432; do
  sleep 1
done

# Always run migrations
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Run tests
python manage.py test
