#!/bin/bash
#
# Run all system tests in parallel using nosetests-2.6.
#
# You need nosetests >= 1.1.2. Install it by running
# $ sudo easy_install "nose>=1.1.2"
#
# For best speed the number of processes should be equal to the number
# of devices available. It should not be higher, that causes timeouts.
#
# For detailed nosetests configuration see
# http://readthedocs.org/docs/nose/en/latest/plugins/multiprocess.html
#
# Run single test:  ... log_tests.py:TestCustomDistributionModels.test_load_invalid_distribution_model
# Run single suite: ... log_tests.py:TestErrorConditions
# Run all tests:    ... log_tests.py
#

nosetests-2.6 --nologcapture --processes=9 --process-timeout=3600 --process-restartworker log_tests.py &

