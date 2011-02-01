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

"""
example custom distribution model
"""

from ots.server.allocator.conductor_command import conductor_command

def example_model(test_list, options):
    """
    Implement your distribution model here. Examples can be found in
    ots.server.allocator.default_distribution_models
    """
    raise NotImplementedError("Example distribution model not implemented.")

def get_model(options):
    """This is the factory method.

    @type options: L{Options}
    @param options: The package name

    @rtype: C{callable}
    @return: A callable 

    """
    
    return example_model
