# syntax=docker/dockerfile:1
FROM python:3
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/

#RUN apt update && apt -y install firewalld
#RUN systemctl start firewalld && sudo systemctl enable firewalld && sudo systemctl status firewalld
#RUN firewall-cmd --add-port=389/tcp --permanent
#RUN firewall-cmd --add-port=636/tcp --permanent
#RUN firewall-cmd reload
