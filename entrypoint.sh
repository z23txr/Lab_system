#!/bin/bash
set -e

echo "Waiting for database..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.5
done
echo "Database is up!"

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn storefront.wsgi:application --bind 0.0.0.0:8000 --workers 3