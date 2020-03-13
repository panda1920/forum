# This file creates dockerized backend for this app
FROM python:3.7

COPY . /app
WORKDIR /app

RUN apt-get update && apt-get install -y
RUN pip install -r requirements.txt

# remove entrypoint defined in parent
ENTRYPOINT []
CMD [ "flask", "run", "--host=0.0.0.0" ]