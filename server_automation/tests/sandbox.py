from capabilities import report

@report.utils.feature('Test reports')
def test_foo():
    boo()

@report.utils.step('Test step 1')
def boo():
    print('I am step 1')
    boo1()
    assert True


@report.utils.step('Test step 2')
def boo1():
    print('I am step 2')
    assert False

# from server_automation.functions import executors as e
#
#
#
# # e.init_ingestion_src_pvc()
# e.init_ingestion_src()
# e.update_shape_fs('/tmp/ingestion/2/Shapes/ShapeMetadata.shp')
# # e.init_ingestion_src()
#
