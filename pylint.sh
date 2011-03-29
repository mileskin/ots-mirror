#!/bin/bash

echo "################ PYLINT START ################"

export PYTHONPATH=$WORKSPACE/ots.common
export PYTHONPATH=$PYTHONPATH:$WORKSPACE/ots.plugin.email
export PYTHONPATH=$PYTHONPATH:$WORKSPACE/ots.plugin.logger
export PYTHONPATH=$PYTHONPATH:$WORKSPACE/ots.plugin.qareports
export PYTHONPATH=$PYTHONPATH:$WORKSPACE/ots.plugin.history
export PYTHONPATH=$PYTHONPATH:$WORKSPACE/ots.plugin.monitor
export PYTHONPATH=$PYTHONPATH:$WORKSPACE/ots.results
export PYTHONPATH=$PYTHONPATH:$WORKSPACE/ots.server
export PYTHONPATH=$PYTHONPATH:$WORKSPACE/ots.tools
export PYTHONPATH=$PYTHONPATH:$WORKSPACE/ots.worker
export PYTHONPATH=$PYTHONPATH:$WORKSPACE/ots.django

# specify Django settings module
export DJANGO_SETTINGS_MODULE=ots.django.settings


#
# pylint
#

pylint \
   --rcfile=./pylint.rc \
   --output-format=parseable \
   ots.common/ots \
   ots.django/ots \
   ots.plugin.email/ots \
   ots.plugin.history/ots \
   ots.plugin.logger/ots \
   ots.plugin.monitor/ots \
   ots.plugin.qareports/ots \
   ots.results/ots \
   ots.server/ots \
   ots.tools/ots \
   ots.worker/ots > pylint.txt

echo "################# PYLINT END #################"
