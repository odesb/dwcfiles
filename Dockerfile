FROM python:3
ENV PYTHONUNBUFFERED 1
ENV DWCFILES_SETTINGS /code/instance/settings.cfg
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt

