import os

# pylama:ignore=C0103
bind = '127.0.0.1:8000'

workers = int(os.environ.get('GUNICORN_PROCESSES', '3'))
threads = int(os.environ.get('GUNICORN_THREADS', '1'))
timeout = 120
worker_class = os.environ.get('GUNICORN_WORKER', 'sync')

forwarded_allow_ips = '*'
secure_scheme_headers = {'X-Forwarded-Proto': 'https'}
