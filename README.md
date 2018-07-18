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

### Pre-configured virtual machine
For your convenience, we have built a preconfigured virtual applicance with the GDPR registry app, based on Ubuntu 18.04.
You may just import the OVA file into your VirtualBox and run the appliance. Then connect to the IP address assigned to the machine (it uses DHCP by default). You may need to put the related network interface into bridge mode OR NAT mode (in this case, you need to setup a NAT rule).

In fact, we simply

* downloaded Ubuntu 18.04
* created a VirtualBox virtual machine
* followed the installation steps as described in the following (with self-signed certificate generation).

Please note that such virtual appliance is not ready for production, especially if you plan to host your appliance with a public IP address. You may need to:

* harden the server configuration (e.g., with strong HTTPS chiphers) 
* install a let's encrypt certificate for your domain
* properly setup a firewall to enable only HTTP/HTTPS traffic

### Ubuntu (tested version: server x64, 18.04 LTS)
https://www.ubuntu.com/download/server/thank-you?version=18.04&architecture=amd64

### Base Installation
The base installation can be used for testing purposes, as it runs the interface
locally @ http://127.0.0.1:8000. Open a shell and insert the following instructions (let's assume we created a **gdpr** user and we open a shell in its home: **/home/gdpr**):

    sudo apt update
    sudo apt install git python3-pip virtualenv
    git clone https://github.com/pluribus-one/gdpr-registry-app
    virtualenv -p python3 python-venv
    source python-venv/bin/activate
    pip install django django-jet PyPDF2 ReportLab svglib django-appconf django-ipware
    cd gdpr-registry-app
    python manage.py makemigrations axes audit jet dashboard
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py populate
    python manage.py collectstatic
    python manage.py runserver

Now go to: `http://127.0.0.1:8000/admin` with your browser. To log in use the (superuser) credentials previously created while executing `python manage.py createsuperuser`.

### Apache web server
In order to make your gdpr registry app available to other machines, you may use the Apache web server. Open a shell inside */home/gdpr* and digit:

    sudo apt install apache2 libapache2-mod-wsgi-py3
    sudo chown -R www-data:gdpr gdpr-registry-app
    sudo a2enmod ssl headers rewrite

#### SSL Certificate
In order to protect your data in transit you need to setup a HTTPS certificate. You may choose to either 
* (a) generate a self-signed certificate OR 
* (b) install a certificate signed by a trusted certificate authority (**suggested option**).

##### (a) Self-signed
You may use a self-signed certificate if your app is running on a private network. In this case, however, your browser will probably raise an alert (and you may need to add an exception), because the certificate has not been signed by a trusted certificate authority. 

To create a self-signed certificate and update the apache configuration, open a shell and run the following code (inside the */home/gdpr/gdpr-registry-app* folder)
    
    sudo openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -keyout /etc/ssl/private/apache-selfsigned.key -out /etc/ssl/certs/apache-selfsigned.crt
    sudo cp sample.apache.https.conf sample.apache.http.conf /etc/apache2/sites-available/
    sudo a2ensite sample.apache.https sample.apache.http
    sudo a2dissite 000-default
    sudo service apache2 restart

##### (b) Let's Encrypt
Let's Encrypt is a public Certificate Authority that provides free HTTPS certificates for any publicly available domain name.

###### Prerequisites
* Install the Apache web server as described in previous section
* Your machine needs a public IP address reachable at TCP port 80 (HTTP)
* Create a DNS entry for your domain **gdpr-registry.yourdomain.com** that resolves to the above-mentioned public IP address

Open a shell and insert the following commands:

    sudo add-apt-repository ppa:certbot/certbot
    sudo apt install python-certbot-apache
    sudo certbot --apache -d gdpr-registry.yourdomain.com

> To harden your server configuration you may consider to run

    sudo cp sample.apache.security.conf /etc/apache2/conf-available/
    sudo a2enconf sample.apache.security


## Issues
Please report all issues in the appropriate [section of this repository](https://github.com/pluribus-one/gdpr-registry-app/issues)
