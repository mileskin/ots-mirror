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

# -*- coding: utf-8 -*-
"""Conductor internal settings file"""

# See also /etc/conductor.conf

DEBUG_LOG_FILE = "~/conductor.log"
HW_SUFFIX = '.bin'

TEST_DEFINITION_FILE_NAME = "tests.xml"

# Syslog file fetched from device
TESTRUN_LOG_FILE = "/var/log/testrun.log"

# Testrun log file cleaner
TESTRUN_LOG_CLEANER = "/usr/bin/clean-testrunlog.sh"

# Conductor working directory. Directory must exist.
# Tilde will be expanded for home dir of local user whose environment was taken 
# into use when Conductor was started. 
CONDUCTOR_WORKDIR = "~"

# Testrunner-lite's working directory. Directory must exist.
TESTRUNNER_WORKDIR = "~"

# Command for testrunner-lite:
# Last 3 options are: testfilter, httplogger, remotessh
CMD_TESTRUNNER = 'cd %s; ' + \
                 '/usr/bin/testrunner-lite -s -v -a -c ' + \
                 '-f %s ' + \
                 '-o %s ' + \
                 '%s ' + \
                 '%s ' + \
                 '%s '

TESTRUNNER_SSH_OPTION = "-t root@192.168.2.15"
TESTRUNNER_LOGGER_OPTION = '-L %s' #"[http://]host[:port][/path/]"
TESTRUNNER_FILTER_OPTION = '-l "%s"'

HTTP_LOGGER_PATH = "/logger/cita/%s/"  #testrun id

FLASHER_PATH = "/tmp/flasher"

# Command for HW_COMMAND must not contain single quotes (').
# Note: Backslash-escaping them doesn't work.
HW_COMMAND = "ssh root@192.168.2.15 '%s'"
HW_COMMAND_TO_COPY_FILE = "scp root@192.168.2.15:%s %s"
LOCAL_COMMAND_TO_COPY_FILE = "cp %s %s"  #for host-based testing

# Number of retries and sleep interval for SSH connections
SSH_CONNECTION_RETRIES = 3
SSH_RETRY_INTERVAL = 5

# Return codes for Testrunner-lite
TESTRUNNER_SUCCESFUL = 0
TESTRUNNER_INVALID_ARGS = 1
TESTRUNNER_SSH_FAILS = 2
TESTRUNNER_PARSING_FAILS = 3
TESTRUNNER_VALIDATION_FAILS = 4
TESTRUNNER_RESULT_FOLDER_FAILS = 5
TESTRUNNER_XML_READER_FAILS = 6
TESTRUNNER_RESULT_LOGGING_FAILS = 7
