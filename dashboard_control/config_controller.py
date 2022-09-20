import os


def func_to_execute(func_name=None):
    if func_name is not None:
        tests_names = {
            'sharizi tiff': 'shaziri_tiff_overseer',
            'different_zoom_levels': 'test_different_zoom_levels.test_zoom_level()',
            'failure_exist_product_manual_ingestion':
                'test_failure_exists_product_manual_ingestion.test_exists_product_manual_ingestion()',
            'failure_illegal_zoom_level_limit': 'test_failure_illegal_zoom_level_limit.test_illegal_zoom()',
            'test_failure_missing_files': 'test_failure_missing_files.test_missing_files()',
            'ingestion_discrete': 'test_ingestion_discrete.test_manual_discrete_ingest()',
            'invalid_imagery_data': 'test_invalid_imagery_data.test_invalid_data()',
            'manual_geopackage_ingestion': 'test_manual_geopackage_ingestion.test_manual_ingestion_geopackage()',
            'parallel_ingestion_workers': 'test_parallel_ingestion_workers.test_parallel_ingestion()',
            'priority_change': 'test_priority_change.test_priority_change()',
            'watch_ingestion_discrete': 'test_watch_ingestion_discrete.test_watch_discrete_ingest()',
        }
        return exec(tests_names[func_name])
    return None


list_test_name = [
    'sharizi tiff',
    'different_zoom_levels',
    'failure_exist_product_manual_ingestion',
    'failure_illegal_zoom_level_limit',
    'test_failure_missing_files',
    'ingestion_discrete',
    'invalid_imagery_data',
    'manual_geopackage_ingestion',
    'parallel_ingestion_workers',
    'priority_change',
    'watch_ingestion_discrete']

test_conf = {'PYTHONUNBUFFERED': 1,
             'CONF_FILE': "/home/shayperp/Desktop/auto-int/automation-ingestion-test/server_automation/configuration"
                          "/configuration.json",
             }

os.environ["PYTHONUNBUFFERED"] = test_conf['PYTHONUNBUFFERED']
os.environ["CONF_FILE"] = test_conf['CONF_FILE']
