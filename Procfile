web: gunicorn casino.wsgi --timeout 120 --workers 3 --threads 4 --timeout=120 --preload
release: python manage.py collectstatic --noinput
