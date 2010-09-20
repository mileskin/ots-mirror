#!/bin/bash

#Creates developer eggs for all the eggs with 'ots' namespace

for egg_root in ots.*
do
    cd "$egg_root"
    sudo python setup.py develop   
    cd - 
done

#Build the dummy plugin egg for the unittest 

pushd ots.common/ots/common/framework/tests/test_plugin/ots.test_plugin/
sudo python setup.py bdist_egg
popd