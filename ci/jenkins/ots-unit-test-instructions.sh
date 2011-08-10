#!/bin/sh
# Adds OTS code and django_xmlrpc in PYTHONPATH and runs the tests.
rm -f /var/log/ots/*
mkdir -p $WORKSPACE/eggs
export PYTHONPATH=$WORKSPACE/eggs
PACKAGES="ots.common ots.results ots.server ots.worker ots.tools ots.django ots.plugin.email ots.plugin.logger ots.plugin.qareports ots.plugin.monitor ots.plugin.history ots.plugin.conductor.richcore"
for egg_root in $PACKAGES; do
  (cd $WORKSPACE/$egg_root && python setup.py develop --install-dir=$WORKSPACE/eggs)
done
export DJANGO_SETTINGS_MODULE=ots.django.settings
rm -rf $WORKSPACE/eggs/django_xmlrpc
# Expect to find preloaded django_xmlrpc-0.1.tar.gz in users home directory
tar xzf ~/django_xmlrpc-0.1.tar.gz -C $WORKSPACE/eggs
$WORKSPACE/nose.sh --with-xunit --xunit-file=$WORKSPACE/nosetests.xml

