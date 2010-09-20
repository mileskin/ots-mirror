#!/bin/sh

# ***** BEGIN LICENCE BLOCK *****
# This file is part of OTS
#
# Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
#
# Contact: Mikko Makinen <mikko.al.makinen@nokia.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# version 2.1 as published by the Free Software Foundation.
#
# This library is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA
# 02110-1301 USA
# ***** END LICENCE BLOCK *****

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