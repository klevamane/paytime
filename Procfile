release: python manage.py migrate
web: gunicorn paytime.wsgi --log-file - --log-level debug
