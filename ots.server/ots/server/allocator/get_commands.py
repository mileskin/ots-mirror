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

"""
A module for generating conductor commands based on testrun options
"""
from ots.server.allocator.default_distribution_models \
    import single_task_distribution, perpackage_distribution


def get_commands(distribution_model,
                 image_url,
                 rootstrap,
                 test_list,
                 testrun_id,
                 storage_address,
                 test_filter,
                 timeout,
                 flasher="",
                 custom_distribution_model=None,
                 use_libssh2=False,
                 resume=False,
                 extended_options=None):
    """Returns a list of conductor commands based on the options"""
    options = dict()
    options['image_url'] = image_url
    options['testrun_id'] = testrun_id
    options['storage_address'] = storage_address
    options['testfilter'] = test_filter
    options['flasherurl'] = flasher
    options['timeout'] = str(timeout)
    options['rootstrap'] = rootstrap
    options['use_libssh2'] = use_libssh2
    options['resume'] = resume

    if extended_options:
        options['flasher_options'] = extended_options.get("flasher_options", None)

    cmds = []

    # Try custom distribution model first
    if custom_distribution_model:
        return custom_distribution_model(test_list, options)

    # Or use defaults
    if distribution_model == "perpackage":
        cmds = perpackage_distribution(test_list,
                                       options)
    else: # Default to single task distribution if nothing else matches
        cmds = single_task_distribution(test_list,
                                        options)
    return cmds
