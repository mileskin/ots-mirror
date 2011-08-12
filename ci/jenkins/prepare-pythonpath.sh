#!/bin/sh
# Adds OTS code and django_xmlrpc in PYTHONPATH
EGGS_DIR=$WORKSPACE/eggs
rm -rf $EGGS_DIR
mkdir -p $EGGS_DIR
export PYTHONPATH=$EGGS_DIR
PACKAGES="ots.common ots.results ots.server ots.worker ots.tools ots.django ots.plugin.email ots.plugin.logger ots.plugin.qareports ots.plugin.monitor ots.plugin.history ots.plugin.conductor.richcore"
for egg_root in $PACKAGES; do
  (cd $WORKSPACE/$egg_root && python setup.py develop --install-dir=$EGGS_DIR)
done
export DJANGO_SETTINGS_MODULE=ots.django.settings
# Expect to find preloaded django_xmlrpc-0.1.tar.gz in users home directory
tar xzf ~/django_xmlrpc-0.1.tar.gz -C $EGGS_DIR
