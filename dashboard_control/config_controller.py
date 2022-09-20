

def different_zoom_levels():
    return "test_different_zoom_levels.test_zoom_level()"


def failure_exist_product_manual_ingestion():
    return " test_failure_exists_product_manual_ingestion.test_exists_product_manual_ingestion()"


def test_failure_illegal_zoom_level_limit():
    return "test_failure_illegal_zoom_level_limit.test_illegal_zoom()"


def test_failure_missing_files():
    return "test_failure_missing_files.test_missing_files()"


def ingestion_discrete():
    return "test_ingestion_discrete.test_manual_discrete_ingest()"


def invalid_imagery_data():
    return "test_invalid_imagery_data.test_invalid_data()"


def manual_geopackage_ingestion():
    return "test_manual_geopackage_ingestion.test_manual_ingestion_geopackage()"


def parallel_ingestion_workers():
    return "test_parallel_ingestion_workers.test_parallel_ingestion()"


def priority_change():
    return "test_priority_change.test_priority_change()"


def watch_ingestion_discrete():
    return "test_watch_ingestion_discrete.test_watch_discrete_ingest()"


tests_names = {
    'sharizi tiff': 'shaziri_tiff_overseer',
    'different_zoom_levels': different_zoom_levels(),
    'failure_exist_product_manual_ingestion': failure_exist_product_manual_ingestion(),
    'failure_illegal_zoom_level_limit': test_failure_illegal_zoom_level_limit(),
    'test_failure_missing_files': test_failure_missing_files(),
    'ingestion_discrete': ingestion_discrete(),
    'invalid_imagery_data': invalid_imagery_data(),
    'manual_geopackage_ingestion': manual_geopackage_ingestion(),
    'parallel_ingestion_workers': parallel_ingestion_workers(),
    'priority_change': priority_change(),
    'watch_ingestion_discrete': watch_ingestion_discrete(),
}


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
    'watch_ingestion_discrete'
]

test_conf = {'PYTHONUNBUFFERED': 1,
             'CONF_FILE': "/home/shayperp/Desktop/auto-int/automation-ingestion-test/server_automation/configuration"
                          "/configuration.json",
             }
