# Installation

## Ubuntu

### Base Installation
> This may be used for testing purposes, as it runs the interface
> @ http://127.0.0.1:8000

    sudo apt install python3-pip
    virtualenv -p python3 gdpr-app
    source gdpr-app/bin/activate
    pip install django django-axes django-jet PyPDF2 ReportLab svglib
    python manage.py makemigrations axes audit jet dashboard
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py populate
    python manage.py runserver

> NOW GO TO: `http://127.0.0.1:8000` with your browser

### Apache web server

    sudo apt install apache2 libapache2-mod-wsgi-py3

### Let's Encrypt SSL Certificate

#### Prerequisites
* Install the Apache web server as described in previous section
* Your machine needs a public IP address reachable at TCP port 80 (HTTP)
