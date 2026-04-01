#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Load Rwanda data (optional - uncomment if needed)
# python manage.py load_rwanda_data

# Create sample data (optional - uncomment if needed)
# python manage.py create_sample_data

