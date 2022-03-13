FROM ubuntu:impish

ENV DEBIAN_FRONTEND noninteractive


RUN apt update ; apt install -y  git python3-pip virtualenv sqlite3 gettext

WORKDIR /app

RUN set -x ; virtualenv -p python3 python-venv ; . python-venv/bin/activate

ADD . /app

COPY docker/entrypoint.sh /app
COPY docker/gdpr.sh /app

RUN  . python-venv/bin/activate ; pip install -r requirements.txt

RUN . python-venv/bin/activate ; django-admin compilemessages

ENTRYPOINT /app/entrypoint.sh
EXPOSE 8000
