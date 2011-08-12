#!/bin/sh

# ***** BEGIN LICENCE BLOCK *****
# This file is part of OTS
#
# Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
#
# Contact: meego-qa@lists.meego.com
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

# These require database
EXCLUDE_PATHS="ots.plugin.monitor|ots.plugin.logger|ots.plugin.history"
# These require gmail
EXCLUDE_PATHS="$EXCLUDE_PATHS|ots.plugin.email/ots/plugin/email/tests/component/test_email_plugin.py"
# These require running OTS server
EXCLUDE_PATHS="$EXCLUDE_PATHS|ots.server/ots/server/xmlrpc/tests/component/test_xmlrpc.py"
# This directory may contain dependencies and their test
EXCLUDE_PATHS="$EXCLUDE_PATHS|eggs"

TEST_FILES=$(find . -type f \( -name "tests.py" -o -name "test_*.py" \) | grep -v -E "$EXCLUDE_PATHS")

# Run tests
nosetests $@ $TEST_FILES -e testrun_queue_name
