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

#
# Run the unittests with nose
#
# usage: nose.sh <nose_parameter>
#

if [ $# -gt 0 ]; then
    echo "`basename $0` started with parameters: $@"
fi

#############
#ots.common
#############

nosetests ots.common/ots/common/framework/tests/test_* $@
nosetests ots.common/ots/common/dto/tests/test_* $@
nosetests ots.common/ots/common/amqp/tests/test_* -e testrun_queue_name $@

#############
#ots.server
#############

nosetests ots.server/ots/server/distributor/tests/test_* -e testrun -e test_remote $@

nosetests ots.server/ots/server/hub/tests/test_* -e testrun $@
nosetests ots.server/ots/server/xmlrpc/tests/test_* $@

#############
#ots.worker
#############
nosetests ots.worker/ots/worker/tests/test_* $@

###################
#ots.email_plugin
###################
nosetests ots.email_plugin/ots/email_plugin/tests/test_* $@

##############
#ots.results
##############
nosetests ots.results/ots/results/tests/test_* $@

