#!/bin/sh

cd ots.common
sudo python setup.py develop
cd -

cd ots.results
sudo python setup.py develop
cd -

cd ots.server
sudo python setup.py develop
cd -

cd ots.worker
sudo python setup.py develop
cd -