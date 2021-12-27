#!/bin/bash
source /source_code/venv/bin/activate
pytest --show-capture=no /source_code/server_automation/tests/test_ingestion_discrete.py
#echo "Please Choose running mode:\n* Sanity - press 's'\n* E2E - press 'e'\n* Full set - press 'f'"
#  read -p "Input Selection:" mode
#  if [ "$mode" = "s" ]; then
#        echo "Sanity"
#  elif [ "$mode" = "e" ]; then
#        echo "E2E"
#  elif [ "$mode" = "f" ]; then
#        echo "Full set"
#  fi