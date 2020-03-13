# This file creates dockerized backend for this app
FROM python:3.7-slim

COPY . /app
WORKDIR /app

# remove entrypoint defined in parent
ENTRYPOINT []
CMD [ "flask", "run", "--host=0.0.0.0" ]

RUN pip install pipenv
RUN pipenv install --system --ignore-pipfile --deploy