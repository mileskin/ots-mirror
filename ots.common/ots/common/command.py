#!/usr/bin/env python
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

"""A Class for executing shell commands with timeout."""

import os
import time
import signal
import subprocess
import threading
import shlex

from ots.common.helpers import get_logger_adapter

from ots.common.dto.ots_exception import OTSException


class SoftTimeoutException(OTSException):
    """Exception that is raised when soft timeout occurs."""
    errno = 6001


class HardTimeoutException(OTSException):
    """Exception that is raised when hard timeout occurs."""
    errno = 6001


class FailedAfterRetries(OTSException):
    """Exception that is raised if command fails after retries."""
    pass


class CommandFailed(OTSException):
    """Exception that is if command return value is not what is expected."""
    errno = 6002


class Command(object):
    """Encapsulates a command line command with timeout functionality."""
    def __init__(self, command, soft_timeout=0, hard_timeout=0, wrapper=""):
        """
        Command is the execution command as a string.
        soft_timeout is timeout after which normal kill signal is sent.
        hard_timeout is timeout after kill -9 is sent.
        wrapper is a string with %s where the command will go
        """
        self.log = get_logger_adapter(__name__)
        self.command = command
        if wrapper:
            self.command = wrapper % command
        self.soft_timeout = float(soft_timeout)
        self.hard_timeout = float(hard_timeout)
        self.return_value = None
        self.stdout = ""
        self.stderr = ""
        self.execution_time = - 1
        self.pid = - 1
        self.soft_timeout_occured = False
        self.hard_timeout_occured = False
        self.process = None
        self.start_time = None
        self.expected_returnvalue = 0
        self.soft_timer = None
        self.hard_timer = None

    def __str__(self):
        return ("Command %s, pid: %d, return_value: %s, stdout: %s, " + \
            "stderr: %s, execution time: %s") % \
            (str(self.command), self.pid, str(self.return_value), self.stdout,
             self.stderr, str(self.execution_time))

    def execute_with_retries(self,
                             retries=1,
                             expected_returnvalue=0,
                             sleep_between_retries=0):
        """
        Tries to execute the command several times. This only works with
        non-background commands.
        expected_returnvalue is used to check if execution was successful.
        sleep_between_retries is sleep time in seconds

        Throws an exception if failed after all retries.
        returns number of tries before successful execution

        Note: Timeouts mean timeout for one execution try. The command is
        executed again after timeout occurs until number of retries is met.
        """
        retries = int(retries)
        expected_returnvalue = int(expected_returnvalue)
        sleep_between_retries = int(sleep_between_retries)
        self.log.debug("expected_returnvalue %d" % expected_returnvalue)
        self.log.debug("retries %d" % retries)
        tries = 1
        while tries <= retries:
            try:
                self.execute_in_shell(expected_returnvalue)
                return tries

            except (SoftTimeoutException, HardTimeoutException, CommandFailed):
                self.log.debug("command %s attempt %d failed" % \
                                   (self.command, tries))

            tries = tries + 1
            time.sleep(sleep_between_retries)
        raise FailedAfterRetries

    def execute(self, expected_returnvalue=0):
        """
        Executes the command without shell and wait that command returns.
        Throws an exception if timeout occurs.
        """
        self._execute_and_wait(expected_returnvalue, shell=False)

    def execute_in_shell(self, expected_returnvalue=0):
        """
        Executes the command in a new shell and wait that command returns.
        Throws an exception if timeout occurs.
        """
        self._execute_and_wait(expected_returnvalue, shell=True)

    def _execute_and_wait(self, expected_returnvalue=0, shell=True):
        """
        Executes the command and wait that command returns.
        Throws an exception if timeout occurs.
        """
        self.start_time = time.time()
        self.expected_returnvalue = int(expected_returnvalue)

        self._start_timers()

        command_string = self.command
        if not shell:
            command_string = shlex.split(self.command)
            self.log.debug("Command arguments: %s" % command_string)

        self.process = subprocess.Popen(command_string,
                                        shell=shell,
                                        stderr=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                        stdin=subprocess.PIPE,
                                        preexec_fn=os.setpgrp)

        self.pid = self.process.pid
        # Wait
        self._communicate()

    def execute_without_redirection(self, expected_returnvalue=0):
        """
        Executes the command and returns its return value. stdout and stderr
        are not piped so they cannot be accessed from the command object.
        Throws an exception if timeout occurs.
        """
        self.start_time = time.time()
        self.expected_returnvalue = int(expected_returnvalue)

        self._start_timers()

        self.process = subprocess.Popen(self.command,
                                        shell=True,
                                        preexec_fn=os.setpgrp)

        self.pid = self.process.pid

        self._communicate()

    def execute_background(self, expected_returnvalue=0):
        """
        Executes the command in the background. Call wait() to get results from
        it.
        Throws an exception if timeout occurs.
        """
        self.start_time = time.time()
        self.expected_returnvalue = int(expected_returnvalue)

        self._start_timers()

        self.process = subprocess.Popen(self.command,
                                        stderr=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                        shell=True,
                                        preexec_fn=os.setpgrp)
        self.pid = self.process.pid

    def _start_timers(self):
        """
        Starts timers if self.soft_timeout of self.hard_timeout is defined.
        """
        if self.soft_timeout:
            self.soft_timer = threading.Timer(self.soft_timeout,
                                              self._kill_softly)
            self.soft_timer.start()

        if self.hard_timeout:
            self.hard_timer = threading.Timer(self.hard_timeout,
                                              self._kill_brutally)
            self.hard_timer.start()

    def _communicate(self):
        """
        Waits for process to end and reads values from it.
        Stops timers if any.
        Checks if return value was successful or not
        """
        self.log.debug("calling process.communicate() %s" % self.command)
        try:
            self.stdout, self.stderr = self.process.communicate()
        except (KeyboardInterrupt, SystemExit):
            self.log.info("Aborting...")
            self._stop_timers()
            os.killpg(self.pid, signal.SIGTERM)
            raise

        self.log.debug("process.communicate() returned %s" % self.command)
        self._stop_timers()
        self.return_value = self.process.returncode
        self.execution_time = time.time() - self.start_time

        if self.hard_timeout_occured:
            raise HardTimeoutException

        if self.soft_timeout_occured:
            raise SoftTimeoutException

        if self.return_value != self.expected_returnvalue:
            raise CommandFailed

    def wait(self):
        """
        Waits until process ends. This makes sense only if background is True
        """
        self.log.debug("Waiting for process %d to end..." % self.pid)
        self._communicate()
        self.log.debug("Process %d ended..." % self.pid)

    def already_executed(self):
        """Returns true if command has been executed."""
        return self.execution_time != - 1

    def send_signal(self, sig_num):
        """Send a signal to command process"""
        os.killpg(self.pid, sig_num)
        self.log.debug("Sent signal %d to %d" % (sig_num, self.pid))

    def _kill_softly(self):
        """A Callback function to terminate process softly"""

        os.killpg(self.pid, signal.SIGTERM)
        self.log.debug("Soft timeout. Killing...")
        self.soft_timeout_occured = True

    def _kill_brutally(self):
        """A Callback function to terminate process brutally"""

        os.killpg(self.pid, signal.SIGKILL)

        self.log.debug("Hard timeout. Killing...")
        self.hard_timeout_occured = True

    def _stop_timers(self):
        """Stops timers if they exist"""

        if self.hard_timeout:  # Stop timer if it exists
            self.hard_timer.cancel()
            self.hard_timer.join()

        if self.soft_timeout:  # Stop timer if it exists
            self.soft_timer.cancel()
            self.soft_timer.join()
