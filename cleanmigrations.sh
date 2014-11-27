#!/bin/bash

for f in `ls */migrations/*.py`;
do
	sed -ibak 's/<Point object at [^>]\+>/fromstr("POINT(0 0)")/' $f
	sed -i '1s/^/from django.contrib.gis.geos import fromstr\n/' $f
done
