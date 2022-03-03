#!/bin/bash

cd /app ; . python-venv/bin/activate

do_populate(){
	echo "list.en.json" | python manage.py populate
	touch ./.stamps/populated
}

# https://github.com/pluribus-one/gdpr-registry-app#base-installation
do_install(){
	echo "## installing gdpr application"

	mkdir -p .stamps/

	python manage.py makemigrations axes audit jet dashboard
	python manage.py migrate

	# python manage.py collectstatic -> error
	
	# need stdin for this command
	# python manage.py createsuperuser
	# non interractive mode admin user creation
	python manage.py createsuperuser --username quinton --noinput --email quinton@cena.fr

	touch .stamps/installed
}

# interractive procedure to create admin user
do_create_admin(){
	python manage.py createsuperuser $*
}

do_reset() {
	echo "## resetting gdpr application"

	rm secret.txt
	rm db.sqlite3
	rm .stamps/*
	python manage.py migrate
	# python manage.py createsuperuser --username foobar --noinput --email foobar@example.com
	echo "list.en.json" | python manage.py populate
	
}

# https://github.com/pluribus-one/gdpr-registry-app#updates
do_upgrade(){
	echo "## running upgrade for gdpr application"

	git pull origin master
	python manage.py makemigrations axes audit jet dashboard
	python manage.py migrate
	do_populate
	#python manage.py collectstatic

}

do_backup(){
	echo "## making backup"
	mkdir -p /backup
	cp db.sqlite3 /backup
	echo ".dump" | sqlite3 db.sqlite3 > /backup/gdpr.sql
}

do_run() {
	echo "## running gdpr application"
	python manage.py runserver 0.0.0.0:8000
}

cmd=$1 ; shift
case $cmd in
   run)
	do_run $*
	;;
   backup)
	do_backup $*
	;;
   reset)
	do_reset $*
	;;
   upgrade)
	do_upgrade $*
	;;
   install)
	do_install $*
	;;
   upgrade)
	do_upgrade $*
	;;
  populate)
	do_populate $*
	;;
  create-admin)
	do_create_admin $*
	;;
esac

