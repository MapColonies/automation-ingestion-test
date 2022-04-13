#!/bin/bash
source /source_code/venv/bin/activate

# shellcheck disable=SC2236
if [[ ! -z "${PYTEST_RUNNING_MODE}" ]]; then
  echo -ne "Test chosen running mode is: [${PYTEST_RUNNING_MODE}]\n"

  case $PYTEST_RUNNING_MODE in

  parallel)
    echo -ne " ***** Will Run End - To - End test ***** \n"
    pytest --show-capture=no /source_code/server_automation/tests/test_parallel_ingestion_workers.py
    ;;

  \
    full)
    echo -ne " ***** Will Run full set of tests: e2e, failures, functional tests ***** \n"
    pytest --show-capture=no /source_code/server_automation/tests/
    ;;

  failures)
    echo -ne "Will Run failures tests\n"
    pytest --show-capture=no /source_code/server_automation/tests/test_failure_exists_product_manual_ingestion.py
    sleep 1m
    pytest --show-capture=no /source_code/server_automation/tests/test_failure_missing_files.py
    sleep 1m
    pytest --show-capture=no /source_code/server_automation/tests/test_failure_illegal_zoom_level_limit.py
    sleep 1m
    pytest --show-capture=no /source_code/server_automation/tests/test_invalid_imagery_data.py
    ;;

  zoom_levels)
    echo -ne " ***** Will Run functional tests *****\n"
    pytest --show-capture=no /source_code/server_automation/tests/test_different_zoom_levels.py
    ;;

  fail_exist_product)
    echo -ne " ***** Will Run functional tests *****\n"
    pytest --show-capture=no /source_code/server_automation/tests/test_failure_exists_product_manual_ingestion.py
    ;;

  fail_missing_file)
    echo -ne " ***** Will Run functional tests *****\n"
    pytest --show-capture=no /source_code/server_automation/tests/test_failure_missing_files.py
    ;;

  fail_illegal_zoom)
    echo -ne " ***** Will Run functional tests *****\n"
    pytest --show-capture=no /source_code/server_automation/tests/test_failure_illegal_zoom_level_limit.py --alluredir=/opt/my_results
    ;;

  fail_invalid_imagery_data)
    echo -ne " ***** Will Run functional tests *****\n"
    pytest --show-capture=no /source_code/server_automation/tests/test_invalid_imagery_data.py
    ;;

  ingest_only)
    echo -ne " ***** Will Run only ingestion *****\n"
    pytest --show-capture=no /source_code/server_automation/tests/test_ingestion_discrete.py --alluredir=/opt/my_results
    ;;

  docker_test)
    echo -ne "Start docker test suite \n"

    pytest --show-capture=no /source_code/server_automation/tests/test_invalid_imagery_data.py
    sleep 1m

    pytest --show-capture=no /source_code/server_automation/tests/test_ingestion_discrete.py
    sleep 1m

    pytest --show-capture=no /source_code/server_automation/tests/test_invalid_imagery_data.py
    sleep 1m

    pytest --show-capture=no /source_code/server_automation/tests/test_failure_illegal_zoom_level_limit.py


    pytest --show-capture=no /source_code/server_automation/tests/test_manual_geopackage_ingestion.py
    ;;


  geopackage_ingest)
    echo -ne " ***** Will Run only ingestion *****\n"
    pytest --show-capture=no /source_code/server_automation/tests/test_manual_geopackage_ingestion.py
    ;;
    #  geopack_ingestion)
    #    echo -ne " ***** Will Run only ingestion *****\n"
    #    pytest --show-capture=no /source_code/server_automation/tests/new_ingestion_ToDo.py
    #    ;;

  working)
    echo -ne " ***** Will Run only ingestion *****\n"
    pytest --show-capture=no /source_code/server_automation/tests/test_ingestion_discrete.py
    sleep 1m
    pytest --show-capture=no /source_code/server_automation/tests/test_failure_exists_product_manual_ingestion.py
    sleep 1m
    pytest --show-capture=no /source_code/server_automation/tests/test_failure_missing_files.py
    sleep 1m
    pytest --show-capture=no /source_code/server_automation/tests/test_failure_illegal_zoom_level_limit.py
    sleep 1m
    pytest --show-capture=no /source_code/server_automation/tests/test_invalid_imagery_data.py
    sleep 1m
    pytest --show-capture=no /source_code/server_automation/tests/test_parallel_ingestion_workers.py
    ;;

  \
    *)
    echo -ne " ----- unknown tests mode params: [PYTEST_RUNNING_MODE=$PYTEST_RUNNING_MODE] ----- \n"
    ;;
  esac

else
  echo "no variable provided for PYTEST_RUNNING_MODE"
fi

#pytest --show-capture=no /source_code/server_automation/tests/new_ingestion_ToDo.py
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
#pytest --show-capture=no /source_code/server_automation/tests/

#pytest --show-capture=no /source_code/server_automation/tests/test_different_zoom_levels.py

#new_ingestion_ToDo.py
#echo "Please Choose running mode:\n* Sanity - press 's'\n* E2E - press 'e'\n* Full set - press 'f'"
#  read -p "Input Selection:" mode
#  if [ "$mode" = "s" ]; then
#        echo "Sanity"
#  elif [ "$mode" = "e" ]; then
#        echo "E2E"
#  elif [ "$mode" = "f" ]; then
#        echo "Full set"
#  fi
#pytest --show-capture=no /source_code/server_automation/tests/new_ingestion_ToDo.py --slack_username="Dannys Run 1
#sleep 1m
#pytest --show-capture=no /source_code/server_automation/tests/test_failure_exists_product_manual_ingestion.py --slack_username="Dannys Run 2"
