#!/bin/sh
#export FILE_LOGS=1 # remove to avoid logging to file - will print only to console
source /source_code/venv/bin/activate

pytest pytest server_automation/tests/test_ingestion_discrete.py
