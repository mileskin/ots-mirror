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

import unittest
import os
import tempfile
import shutil
import subprocess

from ots.worker.conductor.conductor_plugins import ConductorPlugins
from ots.plugin.conductor.richcore.richcore_plugin import RichCorePlugin, DEFAULT_CONFIG_FILE
from ots.worker.conductor.tests.test_conductor import Options, _conductor_config_simple
from ots.worker.conductor.executor import TestRunData as TestRunData

##############################################################################
# Constants
##############################################################################

THIS_FILE = os.path.dirname(os.path.abspath(__file__))
TEST_PLUGIN_CONF = os.path.join(THIS_FILE, "testdata/test_ots_plugin_conductor_richcore.conf")
TEST_RESULT_DIR = os.path.join(tempfile.gettempdir(), "testrun123", "Hardware")

##############################################################################
# Globals
##############################################################################

g_Command = None

##############################################################################
# Stubs
##############################################################################

class Stub_Target(object):

    def get_command_to_enable_debug_repos(self):
        return ""

    def get_command_to_list_debug_packages(self):
        return ""

class Stub_Command(object):

    def __init__(self, command, return_value = None, stdout = ""):
        self.command = command
        self.return_value = return_value
        self.stdout = stdout

    def execute():
        pass
 
def _stub_execute_ssh_command(cmdstr):
    return g_Command

##############################################################################
# Helpers
##############################################################################

def _build_conductor_config():
    config = _conductor_config_simple()
    
    if not config.has_key('rich_core_dumps'):
        config['rich_core_dumps_folder'] = "/home/meego/core-dumps"

    return config

def _create_result_dirs():
    os.makedirs(os.path.join(TEST_RESULT_DIR, "pre")) 
    os.makedirs(os.path.join(TEST_RESULT_DIR, "post")) 
    os.makedirs(os.path.join(TEST_RESULT_DIR, "testdef", "results"))

##############################################################################
# Tests
##############################################################################

class test_richcore_plugin(unittest.TestCase):
    """unit tests for richcore_plugin"""

    def setUp(self):
        if os.path.exists(TEST_RESULT_DIR):
            shutil.rmtree(TEST_RESULT_DIR)

        _create_result_dirs()

    def tearDown(self):
        if os.path.exists(TEST_RESULT_DIR):
            shutil.rmtree(TEST_RESULT_DIR)

    def test_no_config_found(self):

        DEFAULT_CONFIG_FILE = os.path.join(THIS_FILE, "test.conf")
     
        plugin = RichCorePlugin(TestRunData(Options(), config = _build_conductor_config()))
        self.assertRaises(Exception, plugin.__init__)

    def test_before_testrun_disabled(self):

        DEFAULT_CONFIG_FILE = TEST_PLUGIN_CONF
        config = _build_conductor_config()
        del config['rich_core_dumps_folder']
        plugin = RichCorePlugin(TestRunData(Options(), config))

        plugin.set_target(Stub_Target())
        plugin.set_result_dir(TEST_RESULT_DIR)

        plugin.before_testrun()
        self.assertFalse(plugin.process_rich_core_dumps)

    def test_before_testrun_fetching_build_id_failed(self):

        DEFAULT_CONFIG_FILE = TEST_PLUGIN_CONF
        plugin = RichCorePlugin(TestRunData(Options(), config = _build_conductor_config()))

        plugin.set_target(Stub_Target())
        plugin.set_result_dir(TEST_RESULT_DIR)        

        global g_Command
        g_Command = Stub_Command("test", 1, "foo")
        plugin._execute_ssh_command = _stub_execute_ssh_command
        
        plugin.before_testrun()
        self.assertFalse(plugin.process_rich_core_dumps)

    def test_before_testrun_ok(self):

        DEFAULT_CONFIG_FILE = TEST_PLUGIN_CONF
        plugin = RichCorePlugin(TestRunData(Options(), config = _build_conductor_config()))

        plugin.set_target(Stub_Target())
        plugin.set_result_dir(TEST_RESULT_DIR)

        global g_Command
        g_Command = Stub_Command("test", 0, "build_id")
        plugin._execute_ssh_command = _stub_execute_ssh_command

        def _stub_subprocess_call(cmdstr, shell=True):
            pass

        subprocess.call = _stub_subprocess_call
        plugin.before_testrun()
        self.assertTrue(plugin.process_rich_core_dumps)

    def test_after_testrun_ok(self):

        DEFAULT_CONFIG_FILE = TEST_PLUGIN_CONF
        plugin = RichCorePlugin(TestRunData(Options(), config = _build_conductor_config()))

        plugin.set_target(Stub_Target())
        plugin.set_result_dir(TEST_RESULT_DIR)

        print plugin.result_dir
        print plugin.process_rich_core_dumps    
        global g_Command
        g_Command = Stub_Command("test", 0, "build_id")
        plugin._execute_ssh_command = _stub_execute_ssh_command

        def _stub_subprocess_call(cmdstr, shell=True):
            pass

        subprocess.call = _stub_subprocess_call

        path = os.path.join(TEST_RESULT_DIR, "testdef", "results", "test.rcore.lzo")
        try:
            temp = open(path, "w")
            temp.write("foo")
            temp.close()
        except IOError:
            return
    
        plugin.after_testrun()
        self.assertFalse(os.path.exists(path))
            
                
if __name__ == '__main__':
    unittest.main()
