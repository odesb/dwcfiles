FROM python:3-stretch
ENV PYTHONUNBUFFERED 1
ENV DWCFILES_SETTINGS /code/instance/settings.cfg
RUN apt-get update &&\
    apt-get install ffmpeg -y &&\
    mkdir /code
ADD ./requirements.txt /code
WORKDIR /code
RUN pip install -r requirements.txt


