# -*- coding: utf-8 -*-


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
interface for executors than can be used with TestPackageDatas
process_testdata() method
"""

class GeneralExecutor(object):
    """
    interface for executors than can be used with TestPackageDatas
    process_testdata() method
    """
    
    def pre_process_testpackagedata(self, xml_version):
        '''pre_process testpackagedata object'''
        pass
    
    def pre_process_suite(self, suite):
        '''pre_process suite object'''
        pass
        
    def pre_process_set(self, test_set):
        '''pre_process set object'''
        pass        

    def post_process_suite(self):
        '''post_process suite object'''
        pass
    
    def post_process_set(self):
        '''post_process set object'''
        pass
        
    def post_process_testpackagedata(self):
        '''post_process testpackagedata object'''
        pass
        
    def pre_process_case(self, case):
        '''pre_process case object'''
        pass
        
    def post_process_case(self, case):
        '''post_process case object'''
        pass

    def process_presteps(self, presteps):
        '''process prestep object'''
        pass

    def process_get_additional_files(self, files):
        '''process additional files'''
        pass
        
    def process_poststeps(self, poststeps):
        '''process poststep object'''
        pass
