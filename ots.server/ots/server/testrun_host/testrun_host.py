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
Constructs a testrun and hosts it. Takes care of testrun setup, test
execution etc.
"""

import logging
import datetime


from ots.common.testrun import Testrun

from ots.server.email_backend import email_backend
from ots.common.results.xmlhandler import XmlHandler
from ots.common.results.resultjudge import ResultJudge
from ots.server.conductorengine.conductorengine import ConductorEngine
from ots.server.input.default import Default
from ots.server.input.resultsplugin import InputResultsPlugin


# Extension point mechanism
try:
    from ots_extensions import extension_points
except ImportError: # If no extension points found, use the empty default
    from ots.server.testrun_host import \
        example_extension_points as extension_points

try:    
    from ots_extensions import ots_config
except ImportError: # If no custom config found, use the default
    from ots.server.testrun_host import default_ots_config as ots_config



class TestrunHost(object):
    """
    Constructs a testrun and hosts it. Takes care of testrun setup, test
    execution etc.
    """
    
    def __init__(self):
        self.testrun = None
        self.log = logging.getLogger(__name__)
        self.emailbackend = None
        self.input_plugin = None
        self.testrun_id = None
        self.test_engines = []
        self.post_process_plugins = []
        self.result_plugins = []

    def init_testrun(self,
                     build_id,
                     testrun_id,
                     sw_product,
                     options,
                     email_list,
                     test_packages,
                     image_url=None,
                     rootstrap_url=None):
        """Initializes a new testrun. Returns testrun ID"""
        
        self.testrun_id = testrun_id

        self.testrun = Testrun()
        self.testrun.set_testrun_id(testrun_id)
        self.testrun.set_request_id(build_id)
        self.testrun.set_sw_product(sw_product)
        self.testrun.set_options(self._load_default_options(sw_product))
        self.testrun.set_options(options)
        self.testrun.set_email_list(email_list)        
        self.testrun.set_image_url(image_url)


        self.input_plugin = extension_points.get_inputplugin(self.testrun)

        if not self.input_plugin: # Use default if extension point returned None
            self.input_plugin = Default()

        self._publish_log_link()
        target_packages = self._get_target_packages(build_id)
        self.testrun.set_target_packages(target_packages)
        self._validate_testpackages(test_packages)
        self.testrun.set_testpackages(test_packages)
        self._validate_image_url()
        self.testrun.set_image_name(image_url.split("/")[-1])
        self._init_assetplugin()
        return self.testrun.get_testrun_id()
        

    def register_ta_plugins(self):
        """Registers ta plugins to testrun"""
        config = ots_config.results_storage_config
        distribution_models = \
            extension_points.get_custom_distribution_models(self.testrun)
        self._validate_distribution_model(custom_models = distribution_models)
        eng = ConductorEngine(config,
                              custom_distribution_models = distribution_models)
        self._register_test_engine(eng)
        
    def register_results_plugins(self):
        """Registers results plugins to testrun"""

        if not ots_config.debug_mode:
            input_result_plugin = InputResultsPlugin(self.input_plugin)
            self._register_result_plugin(input_result_plugin)

        xml_handler = XmlHandler(self.testrun,
                                     ots_config.xml_file_name_pattern)
        result_judge = \
            ResultJudge(self.testrun,
                        ots_config.insignificant_tests_matter)


        if self.testrun.email_enabled():
            if ots_config.debug_mode:
                self.emailbackend = \
                    email_backend.EmailBackend(self.testrun,
                                               ots_config.link_urls,
                                               ots_config.email_settings,
                                               mailer="LOG_ONLY")
            else:
                self.emailbackend = \
                    email_backend.EmailBackend(self.testrun,
                                               ots_config.link_urls,
                                               ots_config.email_settings)

            xml_handler.register_backend(self.emailbackend)

        # Get custom result backends
        for backend in extension_points.get_resultbackends(self.testrun):
            xml_handler.register_backend(backend)

        xml_handler.register_backend(result_judge)
        self._register_result_plugin(xml_handler)

        # Get custom resultfilehandlers
        for plugin in extension_points.get_resultfilehandlers(self.testrun):
            self._register_result_plugin(plugin)


    def run(self):
        """Runs the testrun"""
        extension_points.update_testrun_in_db(self.testrun,
                                              self.testrun.get_testrun_id())
        self._execute_ta_engines()
        self._post_process()
        self._save_results()
        

    def publish_result_links(self):
        """Create links to results"""
        # TODO: implement generic publishing plugin stuff and move
        # this and email plugin there.

        self._generate_result_links()
        self.log.info("Publishing result links")

        try:
            if not ots_config.debug_mode:
                for text, url in self.testrun.get_result_links():
                    self.input_plugin.store_url(url, text)

        except:
            self.log.error("Publishing result url failed. "\
                           "Traceback follows:", exc_info = True)

        try:
            if self.testrun.email_enabled() and self.emailbackend:
                self.emailbackend.send_mail()
        except:
            self.log.error("Sending result email failed. Traceback follows:", 
                           exc_info = True)
    
    def testrun_result(self):
        """Returns the final result of the testrun"""
        if not self.testrun: 
            raise Exception("Testrun not defined")

        return self.testrun.get_result()


    def cleanup(self):
        """The final cleanup. Removes temporary stuff."""

        if self.testrun and self.testrun.get_testrun_id():
            extension_points.update_testrun_in_db(self.testrun,
                                                  self.testrun.get_testrun_id())

    #
    # Private methods
    #

    def _execute_ta_engines(self):
        """Execute all registered ta_engines"""


        for engine in self.test_engines:
            self.log.debug("Starting test execution with engine %s" \
                               % engine.name())
            engine.execute(self.testrun)
            self.log.debug("Finished test execution with engine %s" \
                               % engine.name())

        self.log.info("Test execution ready")
        self.testrun.endtime = datetime.datetime.now()

        
    def _post_process(self):
        """
        Executes post processing plugins for the testrun. The idea
        is that this will be executed after the testrun but before
        result handling.
        """
        self.log.info("starting post processing")
        for plugin in self.post_process_plugins:
            try:
                plugin.process(self.testrun)
                self.log.debug("Executed post processing plugin %s" \
                                   % plugin.name())
            except:
                self.log.exception("Post processing plugin %s failed" \
                                       % plugin.name())
        self.log.info("finished post processing")


    def _load_default_options(self, sw_product):
        """Load default options from ots_config"""
        try:
            return ots_config.default_options[sw_product]
        except (KeyError, ValueError):
            raise Exception("Unknown sw_product %s" % sw_product)


    def _publish_log_link(self):
        """Publishes link to testrun log with input_plugin"""

        text = "Log for testrun %s" \
            % str(self.testrun.get_testrun_id())
        url = ots_config.link_urls['logURL']\
            % str(self.testrun.get_testrun_id())

        self.log.info("Publishing testrun log link")
        try:
            if not ots_config.debug_mode:
                self.input_plugin.store_url(url, text)

        except:
            self.log.error("Publishing testrun log link failed. "\
                           "Traceback follows:", exc_info = True)


    def _generate_result_links(self):
        """Generate links to result pages"""

        # link to results on primary server
        text = ots_config.link_text['resultURL1'] \
            % (str(self.testrun.get_testrun_id()),
               str(self.testrun.get_result()))
        link = ots_config.link_urls['resultURL1']\
            % extension_points.get_testrun_link(self.testrun_id)
        self.testrun.add_result_link(text, link)

        # link to results on secondary server
        if "resultURL2" in ots_config.link_urls.keys():
            text = ots_config.link_text['resultURL2'] \
                % str(self.testrun.get_testrun_id())
            link = ots_config.link_urls['resultURL2'] \
                % extension_points.get_testrun_link(self.testrun_id)
            self.testrun.add_result_link(text, link)



    def _init_assetplugin(self):
        """Sets up post processing plugins"""
        
        for plugin in extension_points.get_postprocessplugins(self.testrun):
            self._register_post_process_plugin(plugin)


    def _register_result_plugin(self, plugin):
        """Register new results plugin into testrun"""
        self.result_plugins.append(plugin)
        self.log.debug("Registered new ResultsPlugin: %s" % plugin.name())


    def _register_test_engine(self, engine):
        """
        Register new test engine plugin to be used for the testrun

        @type engine: L{<TAEngine>}
        @param engine: TAEngine plugin implementing 
                       ots.common.interfaces.taengine.TAEngine

        """
        self.test_engines.append(engine)
        self.log.debug("Registered new TestEngine: %s" % engine.name())


        
    def _register_post_process_plugin(self, plugin):
        """Register post processing plugin to testrun
        
        @type plugin: L{<PostProcessPlugin>}
        @param plugin: Plugin implementing 
                       ots.common.interfaces.postprocessplugin
        
        """
        self.post_process_plugins.append(plugin)
        self.log.debug("Registered post processing plugin %s" % plugin.name())


 
    def _store_resultfile(self, result_object):
        """Stores a result object with all registered resultsPlugins"""
        for plugin in self.result_plugins:
            try:
                plugin.add_result_object(result_object)
                self.log.debug("Stored result_object %s with resultsPlugin %s" \
                                   % (result_object.name(), plugin.name()))
            except:
                self.log.exception(\
                    "Failed to store result_object %s with resultsPlugin %s" \
                        % (result_object.name(), plugin.name()))
   
   
    def _save_results(self):
        """Calls saveResults in all registered result_plugins"""

        error_messages = []
        self.log.info("Starting result file processing")
        for result in self.testrun.get_result_objects():
            self._store_resultfile(result)


        for plugin in self.result_plugins:
            try:
                errors = plugin.save_results(self.testrun)
                if errors:
                    error_messages.extend(errors)
                self.log.debug("Saved results with resultsPlugin %s" \
                                   % plugin.name())
            except:
                self.log.exception("Failed to save results with plugin %s" %\
                                       plugin.name())

        self.log.info("Result file processing done")
        return error_messages



    def _validate_testpackages(self, test_packages):
        """
        checks that given testpackages match our naming definitions

        Raises ValueError if invalid packages given

        @type test_packages: D{List} consiting of D{string}
        @param test_packages: List of test package names

        """
        invalid_packages = []
        for package in test_packages:
            if not (package.endswith("-tests")\
            or package.endswith("-test")\
            or package.endswith("-benchmark")):
                invalid_packages.append(package)

        if invalid_packages:
            error_msg = "Invalid testpackage(s): %s" % invalid_packages
            self.testrun.set_state("FINISHED", error_msg)
            self.testrun.set_error_info(error_msg)
            self.testrun.set_result("ERROR")
            raise ValueError(error_msg)



    def _validate_image_url(self):
        """
        checks that image url is given if image is required.

        Raises ValueError if any errors found.
        """

        if not (self.testrun.get_rootstrap_url() \
                    or self.testrun.get_image_url()):

            error_msg = "No image url or rootstrap url defined."
            self.testrun.set_state("FINISHED", error_msg)
            self.testrun.set_error_info(error_msg)
            self.testrun.set_result("ERROR")
            raise ValueError(error_msg)

        if not self.testrun.get_image_url() and \
                self.testrun.get_host_testpackages():

            error_msg = "Image url missing. Executing host based tests "+\
                        "requires image url."
            self.testrun.set_state("FINISHED", error_msg)
            self.testrun.set_error_info(error_msg)
            self.testrun.set_result("ERROR")
            raise ValueError(error_msg)

    def _validate_distribution_model(self, custom_models = []):
        """
        Checks the validitity of given distribution model.

        Raises ValueError if invalid distribution model was given.

        @type distribution_model: D{string}
        @param distribution_model: Name of distribution model to be used. 
                    Currently supported values are 'default' and 'perpackage'.
        """

        valid_values = ['default', 'perpackage']
        for model in custom_models:
            valid_values.append(model[0])
        model = self.testrun.get_option('distribution_model')

        if model not in valid_values:
            error_msg = "Invalid distribution model: %s" % model
            self.testrun.set_state("FINISHED", error_msg)
            self.testrun.set_error_info(error_msg)
            self.testrun.set_result("ERROR")
            raise ValueError(error_msg)

        if model == 'perpackage' and len(self.testrun.get_testpackages()) == 0:
            error_msg = "Test packages must be defined for specified "\
                        +"distribution model '%s'" % model
            self.testrun.set_state("FINISHED", error_msg)
            self.testrun.set_error_info(error_msg)
            self.testrun.set_result("ERROR")
            raise ValueError(error_msg)


    def _get_target_packages(self, build_id):
        """Gets target packages with input_plugin"""
        try:
            target_packages = self.input_plugin.get_changed_packages(build_id)
        except:
            self.log.error("Getting target packages failed. "\
                           "Traceback follows:", exc_info = True)
            target_packages = []

        return target_packages
