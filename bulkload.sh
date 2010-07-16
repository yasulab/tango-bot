#!/bin/sh
PYTHONPATH=. python ../google_appengine/appcfg.py upload_data --config_file=./100.csv     --filename=./test.csv     --kind=Message     --url=http://localhost:8080/remote_api ./
