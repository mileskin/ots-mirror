#!/bin/bash
# Set PYTHONPATH and run the tests
$WORKSPACE/ci/jenkins/prepare-pythonpath.sh
python ots.django/ots/django/manage.py test --settings=settings logger history

