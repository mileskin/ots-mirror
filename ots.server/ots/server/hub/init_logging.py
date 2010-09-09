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

#FIXME

import logging
import datetime

def _generate_log_id_string(request_id, testrun_id):
    """
    Generates the log file name
    """
    request_id = "testrun_%s_request_%s_"% (testrun_id, request_id)
    request_id += str(datetime.datetime.now()).\
        replace(' ','_').replace(':','_').replace('.','_')
    return request_id


def init_logging(request_id, testrun_id):
    """
    initializes the logger
    """
    log_id_string = _generate_log_id_string(request_id, testrun_id)
    log = logging.getLogger()
    return log
