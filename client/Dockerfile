# Creates an image of web server that serves the frontend of this app
FROM nginx:latest

COPY ./build /usr/share/nginx/html
COPY ./web/nginx.conf /etc/nginx/nginx.conf
WORKDIR /usr/share/nginx/html