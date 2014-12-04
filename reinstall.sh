#!/bin/bash

rm /home/rnguyen/db.sqlite3 
rm -rvf */migrations
spatialite /home/rnguyen/db.sqlite3 "SELECT InitSpatialMetaData();"

for app in catalog ;
do
	./manage.py schemamigration --initial $app
done
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
