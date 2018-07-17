# Installation

## Ubuntu (tested on version 18.04 LTS)

### Base Installation
This may be used for testing purposes, as it runs the interface
locally @ http://127.0.0.1:8000. Open a shell and insert the following instructions:

    sudo apt update
    sudo apt install git python3-pip virtualenv
    git clone https://github.com/pluribus-one/gdpr-registry-app
    virtualenv -p python3 python-venv
    source python-venv/bin/activate
    pip install django django-jet PyPDF2 ReportLab svglib
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
Let's Encrypt is a public Certificate Authority that provides free SSL certificates to any publicly available domain name.

#### Prerequisites
* Install the Apache web server as described in previous section
* Your machine needs a public IP address reachable at TCP port 80 (HTTP)
* Create a DNS entry for your domain **gdpr-registry.yourdomain.com** that resolves to the above-mentioned public IP address
    
    sudo add-apt-repository ppa:certbot/certbot
    sudo apt install python-certbot-apache
    sudo certbot --apache -d gdpr-registry.yourdomain.com
