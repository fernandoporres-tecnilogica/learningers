#!/bin/bash

rm /home/rnguyen/db.sqlite3 
rm -rvf */migrations
spatialite /home/rnguyen/db.sqlite3 "SELECT InitSpatialMetaData();"
bash ./cleanmigrations.sh
echo "yes


x
x
x
x
" | ./manage.py syncdb
./manage.py migrate
./manage.py runscript initial
#./manage.py rebuild_index
