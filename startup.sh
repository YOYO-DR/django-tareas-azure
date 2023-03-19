#para ejecutar en el azure en el despliegue
python manage.py migrate
gunicorn  config.wsgi