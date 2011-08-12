#!/bin/bash
# Remove logs, set PYTHONPATH and run the tests
rm -f /var/log/ots/*
$WORKSPACE/ci/jenkins/prepare-pythonpath.sh
$WORKSPACE/nose.sh --with-xunit --xunit-file=$WORKSPACE/nosetests.xml

