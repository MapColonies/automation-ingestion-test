#!/bin/bash

docker run \
--net=host \
-e PYTEST_RUNNING_MODE=ingest_only \
-e CONF_FILE="/opt/configuration.json" \
-v /tmp/my_config:/opt/ \
automation-ingestion-test:latest