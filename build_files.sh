#!/bin/bash
echo "Building Vercel project..."
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
