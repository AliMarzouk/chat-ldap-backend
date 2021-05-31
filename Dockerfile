# syntax=docker/dockerfile:1
FROM python:3
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/code \
    DJANGO_SETTINGS_MODULE=myChannelTuto.settings \
    PORT=8000 \
    WEB_CONCURRENCY=3

EXPOSE 8000
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/

# Install operating system dependencies.
RUN apt-get update -y && \
    apt-get install -y apt-transport-https rsync gettext libgettextpo-dev && \
    curl -sL https://deb.nodesource.com/setup_8.x | bash - && \
    apt-get install -y nodejs &&\
    rm -rf /var/lib/apt/lists/*

RUN pip install "gunicorn>=19.8,<19.9"

CMD gunicorn myChannelTuto.asgi:application

#RUN apt update && apt -y install firewalld
#RUN systemctl start firewalld && sudo systemctl enable firewalld && sudo systemctl status firewalld
#RUN firewall-cmd --add-port=389/tcp --permanent
#RUN firewall-cmd --add-port=636/tcp --permanent
#RUN firewall-cmd reload
