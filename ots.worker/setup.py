# ***** BEGIN LICENCE BLOCK *****
# This file is part of OTS
#
# Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
#
# Contact: ___OSSO_CONTACT_NAME___ <___CONTACT_EMAIL___@nokia.com>
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

from setuptools import setup

setup(
    name = "ots.worker",
    author = "ext-teemu.a.vainio@nokia.com",
    version =  0.1,
    include_package_data = True,
    packages = ['ots',
                'ots.worker'],
    zip_safe = False,
    entry_points={"console_scripts": 
                  ["ots_worker = ots.worker.worker:main"]},
    data_files=[('/etc', ['ots.ini'])]
    )
