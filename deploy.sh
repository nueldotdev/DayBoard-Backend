#!/bin/bash

# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Run the project with Gunicorn
gunicorn --workers 3 --threads 2 --bind 0.0.0.0:$PORT dayboard.wsgi:application