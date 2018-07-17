# GDPR Registry Web App
Welcome to the official repository of the GDPR Registry Web App, developed by Pluribus One. This app is part of a comprehensive effort by Pluribus One to help organizations to achieve General Data Protection Regulation (GDPR) compliance. More information can be found on the official website [https://gdpr.pluribus-one.it](https://gdpr.pluribus-one.it/en).

## Goals
To manage the whole GDPR process, you need a central point where information about GDPR procedures are stored and can be updated on a regular basis by dedicated personnel, including your Data Protection Officer. 

This central place is of fundamental importance to keep track of your current compliance status, identify issues and mitigate them. And this is exactly the role of the so-called Registry of Data Processing Activities, described in the GDPR Article 30. It can also demonstrate that GDPR is a continuous process that has become an integral part of your business. 

This is a key step towards an enhanced security posture.

The Pluribus One GDPR Registry app allows you to keep track of all data processing activities according to a hierarchical structure and the various GDPR stages highlighted in our [website](https://gdpr.pluribus-one.it/en/data_audit).

**Key Features**
* **Open Source**: You may freely use and modify it according to our licence.
* **Sound framework and suggestion mechanisms**: We implemented the Registry App exploiting to our expertise in the field of cybersecurity, and a thorough study of GDPR (which nowadays, it is essentially a cybersecurity problem) to build a comprehensive framework. As you fill in the registry, the app can suggest you how to proceed. We have inserted some useful suggestions that come from our GDPR framework and expertise.
* **Report Generation**: You can generate, anytime, an updated, high-quality PDF report with all your data registry. This is a very useful feature especially if you organization is under investigation by GDPR supervisory authorities.
* **Multi-language**: Full translation support thanks to the Django framework. Currently, the interface is available in English and Italian language.
* **GDPR technology and services**: If you need, Pluribus One offers advanced [technology](https://gdpr.pluribus-one.it/en/technology) and [services](https://gdpr.pluribus-one.it/en/services) around GDPR, to help your organization to achieve GDPR compliance.

## Installation
The app can be installed in virtually any modern operating system. It is implemented in [Python](https://www.python.org), using the [Django Framework](https://www.djangoproject.com). In the following, we provide installation instructions for all tested platforms.

### Ubuntu (tested version: 18.04 LTS)

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
In order to make your gdpr registry app available to other machines, you may use the Apache web server.

    sudo apt install apache2 libapache2-mod-wsgi-py3

### Let's Encrypt SSL Certificate
In order to protect your data in transit you need to setup a HTTPS certificate. Let's Encrypt is a public Certificate Authority that provides free HTTPS certificates for any publicly available domain name.

#### Prerequisites
* Install the Apache web server as described in previous section
* Your machine needs a public IP address reachable at TCP port 80 (HTTP)
* Create a DNS entry for your domain **gdpr-registry.yourdomain.com** that resolves to the above-mentioned public IP address
    
    sudo add-apt-repository ppa:certbot/certbot
    sudo apt install python-certbot-apache
    sudo certbot --apache -d gdpr-registry.yourdomain.com
