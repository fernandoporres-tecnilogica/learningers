#!/bin/bash

rm db.sqlite3 
rm -rvf */migrations
spatialite essai.db "SELECT InitSpatialMetaData();"

#for app in catalog panel annotations wikis;
#do
#	./manage.py schemamigration --initial $app
#done
#bash ./cleanmigrations.sh
echo "yes


x
x
x
x
" | ./manage.py syncdb
./manage.py migrate
./manage.py runscript initial
#./manage.py rebuild_index
