#!/bin/bash

echo "Migration"
python manage.py migrate
echo "Server start"
python manage.py runserver 0.0.0.0:8080
