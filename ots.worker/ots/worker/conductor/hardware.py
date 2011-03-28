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

"""Hardware test target"""

from ots.worker.conductor.testtarget import TestTarget
from ots.worker.conductor.conductor_config import HW_COMMAND
from ots.worker.conductor.conductor_config import HW_COMMAND_TO_COPY_FILE
from ots.worker.conductor.conductor_config import FLASHER_PATH
from ots.worker.conductor.conductorerror import ConductorError

try:
    import customflasher as flasher_module
except ImportError:
    # This is just example class of flasher implementation 
    import defaultflasher as flasher_module


import os
import urllib
import hashlib
import re

class Hardware(TestTarget):
    """
    This class implements methods and commands needed in setting up and to 
    communicate with hardware used as test target.

    The default implementation has support for hardware using Debian packaging.
    """

    def __str__(self):
        return "Hardware"

    def prepare(self):
        """
        Get flasher script and Download flasher and image(s) and flash them
        to hardware. Sets testrun.image_path and testrun.content_image_path
        """

        if self.testrun.dontflash:
            self.log.warning("Skipping image downloading and flashing!")
            return

        self._fetch_flasher()
        self._fetch_release() 
        self._fetch_content_image()
        self._flash()

    def cleanup(self):
        """Remove flash image files."""
        self.log.debug("Removing flash image files.")
        for path in (self.testrun.image_path, self.testrun.content_image_path):
            self._delete_file(path)

    def get_commands_to_show_test_environment(self):
        """
        List of tuples with commands to get information about test environment.
        Commands are for system using Debian packaging.
        """
        plain_cmds = self.config['pre_test_info_commands_debian'] +\
                     self.config['pre_test_info_commands']
        commands = []
        for cmd in plain_cmds:
            commands.append(HW_COMMAND % cmd)
        return zip(commands, plain_cmds)

    def get_command_to_copy_file(self, src_path, dest_path):
        """Command used to copy file"""
        return HW_COMMAND_TO_COPY_FILE % (src_path, dest_path)

    def get_command_to_copy_testdef(self):
        """Command used to copy test definition"""
        cmd = HW_COMMAND_TO_COPY_FILE \
                % (self.testrun.testdef_src, self.testrun.testdef_target_dir)
        return cmd

    def get_command_to_copy_results(self):
        """Command used to copy test results"""
        cmd = HW_COMMAND_TO_COPY_FILE \
                % (self.testrun.results_src, self.testrun.results_target_dir)
        return cmd

    def get_command_to_find_test_packages(self):
        """Command to find Debian packages with file tests.xml from device."""
        return HW_COMMAND % "dpkg -S tests.xml"

    def parse_packages_with_file(self, lines):
        """
        Parse lines returned by "dpkg -S tests.xml" command for test packages.
        Returns list of test packages.
        """
        path_pattern = re.compile("/usr/share/"\
                "(\S+-test|\S+-tests|\S+-benchmark)/tests.xml$", re.MULTILINE)
        pkgs_with_file = re.findall(path_pattern, lines)
        return pkgs_with_file

    def get_command_to_list_installed_packages(self):
        """Command that lists all Debian packages installed in device."""
        return HW_COMMAND % "dpkg -l"

    def parse_installed_packages(self, lines):
        """
        Parse test packages from output lines returned by dpkg -l command. 
        Returns sorted list.
        """
        test_pkg_pattern = re.compile("ii\s\s"\
            "(?P<name>\S+-test|\S+-tests|\S+-benchmark)\s+"\
            "(?P<ver>\S+)\s+"\
            "(?P<desc>.*)$", re.MULTILINE)

        test_pkg_data = re.findall(test_pkg_pattern, lines)
        test_packages = [ name for (name, ver, desc) in test_pkg_data ]
        test_packages.sort()
        return test_packages

    # Private methods

    def _urlretrieve(self, url, path):
        """Calls urllib.urlretrieve() to fetch file from url to path given"""
        urllib.urlretrieve(url, path)


    def _fetch_flasher(self):
        """
        Fetch flasher from self.testrun.flasher_url if it's not None.
        Fetch flasher.md5 and check flasher's md5 digest against it.
        If anything fails, delete downloaded flasher. This forces flasher to use 
        the default flasher.
        """

        flasher_path = FLASHER_PATH
        self._delete_file(flasher_path)

        if self.testrun.flasher_url:
            path = self._fetch_file(self.testrun.flasher_url, 
                                    path=flasher_path, min_size=10000)
            if not path:
                self._delete_file(flasher_path)
                return

            if self._add_execute_privileges(flasher_path):
                self.log.warning("Failed to set +x for %s. Deleting it."\
                                 % flasher_path)
                self._delete_file(flasher_path)
                return

            #Now we have flasher file that should be used.
            #Try downloading flasher.md5 file. 
            #If it succeeds, check md5 digest. If check fails, delete flasher.

            md5_url = "%s.md5" % self.testrun.flasher_url
            md5_path = self._fetch_file(md5_url, exact_size=16)

            if md5_path:
                valid = self._md5_valid(flasher_path, md5_path)
                self._delete_file(md5_path)
                if not valid:
                    self._delete_file(flasher_path)


    def _fetch_file(self, url, path=None, min_size=None, exact_size=None):
        """
        Fetch file from url. Save file to given path or to temporary file.
        If file already exists, it is first deleted.
        Return path to file. Return None if download or size check failed.
        """

        def download_error(url, path):
            """Report failure to log and delete file"""
            self.log.warning("Error downloading file %s" % url)
            self._delete_file(path)

        if not path:
            path = os.path.join(self.config['tmp_path'], os.path.basename(url))

        self._delete_file(path)

        self.log.debug("Fetching file from %s" % url)

        try:
            self._urlretrieve(url, path)
        except:
            download_error(url, path)
            return None

        #TODO instead of size check, check d/l errors from urllib
        if exact_size:
            if os.path.getsize(path) != exact_size:
                download_error(url, path)
                return None
        if min_size:
            size = os.path.getsize(path)
            if size < min_size: 
                self.log.debug("File size too small. "\
                               "(size: %s min_size: %s)" % (size, min_size))
                download_error(url, path)
                return None

        self.log.debug("Received file: %s" % path)

        return path


    def _md5_valid(self, path, md5_path):
        """
        Check MD5 digest for file in path. Calculate MD5 digest for the file 
        and compare to the digest stored in file defined by md5_path.
        Return True if there's a match. Otherwise return False.
        """

        content = self._read_file(path)
        calculated_digest = self._md5_digest(content)
        downloaded_digest = self._read_file(md5_path)

        if calculated_digest == downloaded_digest:
            self.log.debug("Flasher MD5 digest checked ok.")
            return True
        else:
            self.log.warning("Mismatch in flasher's MD5 digest. "\
                             "Calculated: %s Downloaded: %s"\
                             % (calculated_digest, downloaded_digest))
            return False


    def _read_file(self, path):
        """Return the content of the file in given path."""
        thefile = open(path, "r")
        content = thefile.read()
        thefile.close()
        return content

    def _md5_digest(self, content):
        """Read the file in given path and return its MD5 digest."""
        md5hash = hashlib.md5()
        md5hash.update(content)
        return md5hash.digest()

    def _delete_file(self, path):
        """Delete file. Do not raise exception if deleting fails."""
        if path:
            try:
                os.unlink(path)
            except OSError:
                return
            self.log.debug("Deleted file %s" % path)

    def _add_execute_privileges(self, path):
        """Add execute rights to file in given path. Return 0 for success."""
        return os.system("chmod a+x %s" % path) #we are root, we have rights.


    def _fetch_release(self):
        """Fetch image file from URL if specified and if path not already set"""

        if not self.testrun.image_path and self.testrun.image_url:
            self.testrun.image_path = \
                    self._fetch_file(self.testrun.image_url, min_size=10000)
            if not self.testrun.image_path:
                self._raise_download_error(self.testrun.image_url)


    def _fetch_content_image(self):
        """
        Fetch content_image from URL if specified and if path not already set
        """

        if not self.testrun.content_image_path and \
               self.testrun.content_image_url:
            self.testrun.content_image_path = \
                    self._fetch_file(self.testrun.content_image_url, \
                                     min_size=5000)
            if not self.testrun.content_image_path:
                self._raise_download_error(self.testrun.content_image_url)


    def _raise_download_error(self, url):
        """Raise ConductorError about error in downloading required file."""
        filename = os.path.basename(url)
        raise ConductorError("Could not download file %s" % filename, "103")


    def _flash(self):
        """Flash images to the device using the flasher_module"""

        flasher_path = None
        if os.path.isfile(FLASHER_PATH):
            flasher_path = FLASHER_PATH

        try:
            flasher = flasher_module.SoftwareUpdater(flasher=\
                                                     flasher_path)

            self.log.debug("image: %s" % self.testrun.image_path)
            self.log.debug("content image: %s" % \
                           self.testrun.content_image_path)

            #Run flasher. Note: one of paths (image_path OR content_image_path)
            #may be None
            if self.testrun.bootmode:
                flasher.flash(image_path = self.testrun.image_path, \
                              content_image_path = self.testrun.content_image_path, \
                              boot_mode = self.testrun.bootmode)
            else:
                flasher.flash(image_path = self.testrun.image_path, \
                              content_image_path = self.testrun.content_image_path)

        except flasher_module.ConnectionTestFailed:
            raise ConductorError("Error in preparing hardware: "\
                                 "Connection test failed!", "2101")
        except flasher_module.FlashFailed:
            raise ConductorError("Error in preparing hardware: "\
                                 "Flashing the image failed!", "210")
        except flasher_module.InvalidImage:
            raise ConductorError("Error in preparing hardware: "\
                                 "Invalid flash image!", "211")
        except flasher_module.InvalidConfig:
            self.log.debug("Invalid flasher config! Traceback:", exc_info=True)
            raise ConductorError("Error in preparing hardware: "\
                                 "Invalid flasher config file!", "212")


class RPMHardware(Hardware):
    """
    This class implements support for devices that use RPM packaging. Everything
    else is inherited from default hardware class Hardware.
    """

    def get_commands_to_show_test_environment(self):
        """
        List of tuples with commands to get information about test environment.
        """
        plain_cmds = self.config['pre_test_info_commands_rpm'] +\
                     self.config['pre_test_info_commands']
        commands = []
        for cmd in plain_cmds:
            commands.append(HW_COMMAND % cmd)
        return zip(commands, plain_cmds)

    def get_command_to_find_test_packages(self):
        """Command that lists rpm test packages with tests.xml from device."""
        return HW_COMMAND % "find /usr/share/ -name tests.xml | xargs -r rpm -q --queryformat \"%{NAME}\n\" -f"

    def parse_packages_with_file(self, lines):
        """
        Parse lines returned by 'find /usr/share/ -name tests.xml | xargs 
        rpm -q --queryformat "%{NAME}\n" -f' command for test packages.
        Returns list of test packages.
        """
        test_pkg_pattern = re.compile(\
            "(?P<name>\S+-test|\S+-tests|\S+-benchmark)$", re.MULTILINE)
        pkgs_with_file = re.findall(test_pkg_pattern, lines)
        return pkgs_with_file

    def get_command_to_list_installed_packages(self):
        """Command that lists all rpm packages installed in device."""
        return HW_COMMAND % "rpm -qa --queryformat \"%{NAME}\n\""

    def parse_installed_packages(self, lines):
        """
        Parse test packages from output lines returned by 
        rpm -qa --queryformat '%{NAME}\n' command.  Returns sorted list.
        """
        test_pkg_pattern = re.compile(\
            "(?P<name>\S+-test|\S+-tests|\S+-benchmark)$", re.MULTILINE)

        test_pkg_data = re.findall(test_pkg_pattern, lines)
        test_packages = [ name for name in test_pkg_data ]
        test_packages.sort()
        return test_packages

