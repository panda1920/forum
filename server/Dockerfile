# This file creates dockerized backend for this app
FROM python:3.7-slim

# remove entrypoint defined in parent
ENTRYPOINT []
CMD [ "gunicorn", "server.app:app" ]

COPY . /app
WORKDIR /app

# install dependencies
RUN pip install pipenv
RUN pipenv install --system --ignore-pipfile --deploy
