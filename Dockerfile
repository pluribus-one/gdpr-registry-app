FROM ubuntu:impish

ENV DEBIAN_FRONTEND noninteractive


RUN apt update ; apt install -y  git python3-pip virtualenv sqlite3

WORKDIR /app

RUN set -x ; virtualenv -p python3 python-venv ; . python-venv/bin/activate

ADD . /app

COPY docker/entrypoint.sh /app
COPY docker/gdpr.sh /app

RUN  . python-venv/bin/activate ; pip install -r requirements.txt

ENTRYPOINT /app/entrypoint.sh
EXPOSE 8000
