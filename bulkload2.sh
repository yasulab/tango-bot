#!/bin/sh
if [ $# -eq 0 ]
then
    echo "Usage: sh bulkload.sh CSV_FILE"
else
    PYTHONPATH=. python ../google_appengine/appcfg.py upload_data --config_file=./$@ --filename=./wl.csv --kind=Message --url=http://localhost:8080/remote_api ./
fi


