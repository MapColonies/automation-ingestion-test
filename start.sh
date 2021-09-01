#!/bin/bash
source /source_code/venv/bin/activate
pytest --show-capture=no /source_code/server_automation/tests/test_ingestion_discrete.py
