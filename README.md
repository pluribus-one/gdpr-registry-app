# Installation

## Ubuntu

### Base Installation
This may be used for testing purposes, as it runs the interface
locally @ http://127.0.0.1:8000

    sudo apt update
    sudo apt install git python3-pip
    git clone https://github.com/pluribus-one/gdpr-registry-app
    virtualenv -p python3 gdpr-app
    source gdpr-app/bin/activate
    pip install django django-axes django-jet PyPDF2 ReportLab svglib
    cd gdpr-registry-app
    python manage.py makemigrations axes audit jet dashboard
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py populate
    python manage.py runserver

Now go to: `http://127.0.0.1:8000` with your browser. To log in use the (superuser) credentials previously created while executing `python manage.py createsuperuser`.

### Apache web server

    sudo apt install apache2 libapache2-mod-wsgi-py3

### Let's Encrypt SSL Certificate

#### Prerequisites
* Install the Apache web server as described in previous section
* Your machine needs a public IP address reachable at TCP port 80 (HTTP)
