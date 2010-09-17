#!/bin/sh

#Creates developer eggs for all the eggs with 'ots' namespace

for egg_root in ots.*
do
    cd "$egg_root"
    sudo python setup.py develop   
    cd - 
done