release: python manage.py makemigrations
release: python manage.py migrate
release: python manage.py test
web: gunicorn musicroomweb.wsgi --log-file -