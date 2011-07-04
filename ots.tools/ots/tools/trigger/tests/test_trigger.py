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

from ots.tools.trigger.ots_trigger import parse_commandline_arguments, _parameter_validator, _parse_configuration_file

class TestTrigger(unittest.TestCase):
    
    def test_parse_commandline_mandatory(self):
        """
        Test that mandatory parameters must be set
        """
        
        mandatory_args = ['-s', 'someurl.com',
                          '-b', 'build id',
                          '-i', 'http://imageurl.com',
                          '-p', 'example_sw_product',
                          '-e', 'foo@bar.com']
        
        invalid_args_1 = ['-s', 'someurl.com',
                          '-b', 'build id',
                          '-i', 'http://imageurl.com',
                          '-p', 'example_sw_product']
        
        invalid_args_2 = ['-s', 'someurl.com',
                          '-b', 'build id',
                          '-i', 'http://imageurl.com',
                          '-e', 'foo@bar.com']
        
        invalid_args_3 = ['-s', 'someurl.com',
                          '-b', 'build id',
                          '-p', 'example_sw_product',
                          '-e', 'foo@bar.com']
        
        invalid_args_4 = ['-s', 'someurl.com',
                          '-i', 'http://imageurl.com',
                          '-p', 'example_sw_product',
                          '-e', 'foo@bar.com']
        
        invalid_args_5 = ['-b', 'build id',
                          '-i', 'http://imageurl.com',
                          '-p', 'example_sw_product',
                          '-e', 'foo@bar.com']
        
        mandatory_parameters = parse_commandline_arguments(mandatory_args)
        invalid_parameters_1 = parse_commandline_arguments(invalid_args_1)
        invalid_parameters_2 = parse_commandline_arguments(invalid_args_2)
        invalid_parameters_3 = parse_commandline_arguments(invalid_args_3)
        invalid_parameters_4 = parse_commandline_arguments(invalid_args_4)
        invalid_parameters_5 = parse_commandline_arguments(invalid_args_5)
        
        self.assertFalse( mandatory_parameters == None)
        self.assertFalse( invalid_parameters_1 != None)
        self.assertFalse( invalid_parameters_2 != None)
        self.assertFalse( invalid_parameters_3 != None)
        self.assertFalse( invalid_parameters_4 != None)
        self.assertFalse( invalid_parameters_5 != None)
    
    def test_parse_commandline_chroot_paramters(self):
        """
        Test that all chroot parameters must be set
        """
        
        mandatory_args = ['-s', 'someurl.com',
                          '-b', 'build id',
                          '-i', 'http://imageurl.com',
                          '-p', 'example_sw_product',
                          '-e', 'foo@bar.com']
        chroot_args = ['-r', 'http://rootstrap.com',
                       '-C', 'test-package1-tests']
        
        invalid_args_1 = ['-r', 'http://rootstrap.com']
        invalid_args_2 = ['-C', 'test-package1-tests']
        
        chroot_args.extend(mandatory_args)
        invalid_args_1.extend(mandatory_args)
        invalid_args_2.extend(mandatory_args)
        
        mandatory_parameters = parse_commandline_arguments(chroot_args)
        invalid_parameters_1 = parse_commandline_arguments(invalid_args_1)
        invalid_parameters_2 = parse_commandline_arguments(invalid_args_2)
        
        self.assertFalse( mandatory_parameters == None)
        self.assertFalse( invalid_parameters_1 != None)
        self.assertFalse( invalid_parameters_2 != None)
    
    def test_parse_commandline_params_short(self):
        """
        Test that command line parameter names hasn't changed
        """
        
        # First cell is the cmd parameter name, second is the
        # parameter value and the third one is the assumed output
        parameters_list = [['-s', 'someurl.com', 'server'],
                           ['-b', 'build id', 'build_id'],
                           ['-i', 'http://imageurl.com', 'image'],
                           ['-p', 'example_sw_product', 'sw_product'],
                           ['-e', 'foo@bar.com', 'email'],
                           ['-r', 'http://rootstrap.com', 'rootstrap'],
                           ['-C', 'test-package1-tests', 'chroottest'],
                           ['-d', 'devicegroup:example', 'device'],
                           ['-t', 'testpackage1-tests', 'packages'],
                           ['-m', '1800', 'timeout'],
                           ['-f', 'notestcase', 'testfilter'],
                           ['-n', 'foo', 'input_plugin'],
                           ['-c', 'perpackage', 'distribution_model'],
                           ['-T', '/tmp/file1', 'hw_testplans'],
                           ['-T', '/tmp/file2', 'hw_testplans'],
                           ['-O', '/tmp/file3', 'host_testplans'],
                           ['-O', '/tmp/file4', 'host_testplans'],
                           ['-S', 'true', 'use_libssh2'],
                           ['-x', 'attribute1:value1', 'options']
                          ]
        
        cmd_list = []
        valid_dict = {}
        
        for param in parameters_list:
            cmd_list.extend(param[0:2])
            valid_dict[param[2]] = param[1]
        
        valid_dict['attribute1'] = 'value1'
                
        all_parameters = parse_commandline_arguments(cmd_list)
        
        for (name, value) in all_parameters.items():
            if name == "hw_testplans" or name == "host_testplans" or \
               name == "email":
                self.assertTrue(type(value) is list)
                continue
            
            if name == "timeout":
                self.assertTrue(int(valid_dict[name]) == value)
                continue
            
            if name == "use_libssh2":
                self.assertTrue(bool(valid_dict[name]) == value)
                continue    

            if valid_dict.has_key(name):
                self.assertTrue(valid_dict[name] == value)
            
    def test_parse_commandline_params_long(self):
        """
        Test that command line parameter names hasn't changed
        """
        
        # First cell is the cmd parameter name, second is the
        # parameter value and the third one is the assumed output
        parameters_list = [['--server', 'someurl.com', 'server'],
                           ['--build_id', 'build id', 'build_id'],
                           ['--image', 'http://imageurl.com', 'image'],
                           ['--sw_product', 'example_sw_product', 'sw_product'],
                           ['--email', 'foo@bar.com', 'email'],
                           ['--rootstrap', 'http://rootstrap.com', 'rootstrap'],
                           ['--chrootpackages', 'test-package1-tests', 'chroottest'],
                           ['--device', 'devicegroup:example', 'device'],
                           ['--testpackages', 'testpackage1-tests', 'packages'],
                           ['--timeout', '1800', 'timeout'],
                           ['--filter', 'notestcase', 'testfilter'],
                           ['--input_plugin', 'foo', 'input_plugin'],
                           ['--distribution', 'perpackage', 'distribution_model'],
                           ['--deviceplan', '/tmp/file1', 'hw_testplans'],
                           ['--deviceplan', '/tmp/file2', 'hw_testplans'],
                           ['--hostplan', '/tmp/file3', 'host_testplans'],
                           ['--hostplan', '/tmp/file4', 'host_testplans'],
                           ['--libssh2', 'true', 'use_libssh2'],
                           ['--options', 'attribute1:value1', 'options']
                          ]
        
        cmd_list = []
        valid_dict = {}
        
        for param in parameters_list:
            cmd_list.extend(param[0:2])
            valid_dict[param[2]] = param[1]
        
        valid_dict['attribute1'] = 'value1'
                
        all_parameters = parse_commandline_arguments(cmd_list)
        
        for (name, value) in all_parameters.items():
            if name == "hw_testplans" or name == "host_testplans" or \
               name == "email":
                self.assertTrue(type(value) is list)
                continue
            
            if name == "timeout":
                self.assertTrue(int(valid_dict[name]) == value)
                continue
            
            if name == "use_libssh2":
                self.assertTrue(bool(valid_dict[name]) == value)
                continue    

            if valid_dict.has_key(name):
                self.assertTrue(valid_dict[name] == value)
        
    def test_parameter_validator(self):
        
        cmd_options = { 'empty'         : '',
                        'zero'          : 0 ,
                        'none'          : None,
                        'options'       : 'param1:value1 param2:value2',
                        'email'         : 'foo@bar.com,name@domai.com',
                        'extra'         : 'value',
                        'configfile'    : None,
                        'configsection' : None}
        
        config_options = { 'email'  : ['new@system.com'],
                           'param3' : 'value3'}
        
        expected_dict = { 'param1' : 'value1',
                          'param2' : 'value2',
                          'param3' : 'value3',
                          'email'  : ['new@system.com','foo@bar.com', 'name@domai.com'],
                          'extra'  : 'value'}
        
        output_dict = _parameter_validator(config_options, cmd_options)
        
        self.assertEqual(output_dict, expected_dict)
        
    def test_parameter_validator_email_string(self):
        
        cmd_options = { 'email'         : 'foo@bar.com,name@domai.com',
                        'configfile'    : None,
                        'configsection' : None}
        
        config_options = { 'email'  : 'new@system.com' }
        
        expected_dict = { 'email'  : ['new@system.com','foo@bar.com', 'name@domai.com'] }
        
        output_dict = _parameter_validator(config_options, cmd_options)
        
        self.assertEqual(output_dict, expected_dict)
        
    def test_parameter_validator_email_config(self):
        
        cmd_options = { 'configfile'    : None,
                        'configsection' : None}
        
        config_options = { 'email'  : 'new@system.com' }
        
        expected_dict = { 'email'  : ['new@system.com'] }
        
        output_dict = _parameter_validator(config_options, cmd_options)
        
        self.assertEqual(output_dict, expected_dict)
        
        
    def test_parameter_validator_email_cmd(self):
        
        cmd_options = { 'email'         : 'foo@bar.com,name@domai.com',
                        'configfile'    : None,
                        'configsection' : None}
        
        config_options = {}
        
        expected_dict = { 'email'  : ['foo@bar.com', 'name@domai.com'] }
        
        output_dict = _parameter_validator(config_options, cmd_options)
        
        self.assertEqual(output_dict, expected_dict)
        
    
    def test_parse_configuration(self):
        
        example_path = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
        example_file = os.path.join(example_path, 'ots_trigger_example.conf')
        
        self.assertTrue(os.path.exists(example_file))
        
        expected_dict = { 'build_id': 'n900_acceptance', 
                          'sw_product': 'meego', 
                          'qa_hwproduct': 'n900', 
                          'rootstrap': '', 
                          'qa_testtype': 'Unknown', 
                          'testfilter': '', 
                          'image': 'http://someurl.com/image.tar.gz', 
                          'hosttest': ['testpackage-tests', 'testpackage2-tests'], 
                          'server': 'localhost:8080', 
                          'host_testplans': '', 
                          'chroottest': '', 
                          'distribution_model': 'perpackage', 
                          'timeout': '30', 
                          'device': 'devicegroup:n900', 
                          'hw_testplans': '', 
                          'use_libssh2': 'false', 
                          'packages': ['testpackage-tests', 'testpackage2-tests'], 
                          'email': ['foo@bar.com', 'test@domain.com'], 
                          'qa_target': 'Handset', 
                          'qa_release_version': '1.3'}
        
        config_params_without_section = _parse_configuration_file(example_file, None)
        
        self.assertEqual(config_params_without_section, expected_dict)
        
        config_params_with_section = _parse_configuration_file(example_file, 'example_section')
   
        expected_dict['qa_testtype'] ='example_device'
        expected_dict['image'] ='http://somethingelse.com/image.tar.gz'
        expected_dict['device'] ='devicegroup:netbook'
        
        self.assertEqual(config_params_with_section, expected_dict)        
        

if __name__ == "__main__":
    unittest.main()
