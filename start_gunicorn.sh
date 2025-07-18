#!/bin/bash

source /home/savage/Escritorio/homeService_API/venv/bin/activate

# Ejecutar gunicorn con 3 workers y bind 0.0.0.0:8000
exec gunicorn --workers 3 --bind 0.0.0.0:8000 backend_homeService.wsgi:application
