#!/bin/bash

cd /app ; 

[ ! -f .stamps/installed ]   && /app/gdpr.sh install
[ ! -f ./.stamps/populated ] && /app/gdpr.sh populate

/app/gdpr.sh run
