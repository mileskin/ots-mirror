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
# Run the unit tests with nose
#
# usage: nose.sh <nose_parameter>
#

if [ $# -gt 0 ]; then
    echo "`basename $0` started with parameters: $@"
fi

# Define tests
SERVER_TESTS="ots.server/ots/server/allocator/tests/test_*.py ots.server/ots/server/distributor/tests/test_*.py ots.server/ots/server/xmlrpc/tests/test_*.py ots.server/ots/server/hub/tests/test_*.py"

WORKER_TESTS="ots.worker/ots/worker/tests/test_*.py ots.worker/ots/worker/conductor/tests/test_*.py"

COMMON_TESTS="ots.common/ots/common/framework/tests/test_*.py ots.common/ots/common/amqp/tests/test_*.py ots.common/ots/common/routing/tests/test_*.py ots.common/ots/common/dto/tests/test_*.py"

RESULT_TESTS="ots.results/ots/results/tests/test_*.py"

EMAIL_PLUGIN_TESTS="ots.plugin.email/ots/plugin/email/tests/test_*.py"

QA_REPORTS_PLUGIN_TESTS="ots.plugin.qareports/ots/plugin/qareports/tests/test_*.py"

# Run tests
nosetests \
  $SERVER_TESTS \
  $WORKER_TESTS \
  $COMMON_TESTS \
  $RESULT_TESTS \
  $EMAIL_PLUGIN_TESTS \
  $QA_REPORTS_PLUGIN_TESTS \
  -e testrun_queue_name \
  $@
