#!/bin/sh

#Run the nosetests 


#############
#ots.common
#############

nosetests ots.common/ots/common -e testdefinitionparser -e testrun_id -e test_package -e testrundata -e _check_input_defined -e testcase -e testsuite -e testset -e testpackagedata -e test_definition -e testdata -e testrun 

#############
#ots.server
#############

nosetests ots.server/ots/server/distributor/tests/test_* -e testrun -e test_remote 

nosetests ots.server/ots/server/testrun/tests/test_*

#############
#ots.worker
#############
nosetests ots.worker/ots/worker/tests/test_*

####################
#ots.report_plugin 
####################

nosetests ots.report_plugin/ots/report_plugin/tests/test_*