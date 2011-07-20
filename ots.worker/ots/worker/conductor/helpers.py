# -*- coding: utf-8 -*-
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

"""General helper methods, classes etc."""

import os
import shlex
import logging
import ConfigParser


def parse_config(config_file, section, current_config=None):
    """
    Parses config section from a file. Returns a dictionary.
    Values in current_config dictionary are updated from
    config_file if current_config is not None

    @type config_file: C{str}
    @param config_file: Absolute path of configuration file

    @type section: C{str}
    @param config_file: Section of configuration file

    @type current_config: C{dict}
    @param current_config: Base configuration dictionary

    @rtype: C{dict}
    @return: Configuration dictionary
    """

    config = ConfigParser.ConfigParser()
    config.read(config_file)
    config_options = dict()
    for key, value in config.items(section):
        if current_config:
            config_options.update(_update_config_items(current_config, \
                                                       key, value))
        else:
            config_options[key] = value
    return config_options


def parse_list(config_value):
    """
    Parse comma-separated list of values from given string.
    Remove possible quotes surrounding any value. Return values as list.

    @type config_value: C{str}
    @param config_value: Configuration parameter value

    @rtype: C{list}
    @return: List presentation of configuration parameter value
    """

    splitter = shlex.shlex(config_value, posix=True)
    splitter.whitespace += ','
    splitter.whitespace_split = True
    return list(splitter)


def _update_config_items(config_dict, key, value):
    """
    Updates configuration dictionary values

    @type config_dict: C{str}
    @param config_dict: Dictionary that will be updated

    @type key: C{str}
    @param key: Dictionary key

    @type value: C{list}
    @param value: Value that will be added to configuration

    @rtype: C{dict}
    @return: Configuration dictionary

    """
    if key in config_dict and type(config_dict[key]) is type(list()):
        config_dict[key] = config_dict[key] + parse_list(value)
    else:
        config_dict[key] = value

    return config_dict


def get_logger_adapter(logger_name):
    """
    Returns the logger adapter for logging with 'userDefinedId' parameter,
    which is the same as OTS worker number, device id and HAT control USB
    port number.
    """
    device_n = os.getenv("OTS_WORKER_NUMBER")
    return logging.LoggerAdapter(logging.getLogger(logger_name),
                                 {'userDefinedId': device_n})
