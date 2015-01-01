#!/bin/bash

rm /home/rnguyen/db.sqlite3 
echo "yes


x
x
x
x
" | ./manage.py syncdb
./manage.py migrate
./manage.py runscript initial
./manage.py rebuild_index
