# FROM python:3
FROM base/archlinux
ENV PYTHONUNBUFFERED 1
ENV DWCFILES_SETTINGS /code/instance/settings.cfg
RUN pacman -Syu --noconfirm &&
    pacman -S python python-pip ffmpeg --noconfirm
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt

