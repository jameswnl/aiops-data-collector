#!/bin/bash

source scl_source enable rh-python36
gunicorn wsgi --bind=0.0.0.0:8080 --access-logfile=- --config config.py
