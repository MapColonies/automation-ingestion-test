#!/bin/bash
source /source_code/venv/bin/activate
#pytest --show-capture=no /source_code/server_automation/tests/test_ingestion_discrete.py
#sleep 1m
#pytest --show-capture=no /source_code/server_automation/tests/test_failure_exists_product_manual_ingestion.py
#sleep 1m
#pytest --show-capture=no /source_code/server_automation/tests/test_failure_missing_files.py
##sleep 1m
#pytest --show-capture=no /source_code/server_automation/tests/test_failure_illegal_zoom_level_limit.py
#sleep 1m
#pytest --show-capture=no /source_code/server_automation/tests/test_invalid_imagery_data.py
#sleep 1m
#pytest --show-capture=no /source_code/server_automation/tests/test_parallel_ingestion_workers.py





#
pytest --show-capture=no /source_code/server_automation/tests/


#pytest --show-capture=no /source_code/server_automation/tests/test_different_zoom_levels.py

#test_ingestion_discrete.py
#echo "Please Choose running mode:\n* Sanity - press 's'\n* E2E - press 'e'\n* Full set - press 'f'"
#  read -p "Input Selection:" mode
#  if [ "$mode" = "s" ]; then
#        echo "Sanity"
#  elif [ "$mode" = "e" ]; then
#        echo "E2E"
#  elif [ "$mode" = "f" ]; then
#        echo "Full set"
#  fi
#pytest --show-capture=no /source_code/server_automation/tests/test_ingestion_discrete.py --slack_username="Dannys Run 1
#sleep 1m
#pytest --show-capture=no /source_code/server_automation/tests/test_failure_exists_product_manual_ingestion.py --slack_username="Dannys Run 2"
