# FROM rhscl/python-36-rhel7
FROM python:3

COPY . /app
WORKDIR /app

RUN pip install pipenv

RUN pipenv install --system --deploy

# CMD ["python", "start.py"]
