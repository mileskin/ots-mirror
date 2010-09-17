#!/bin/sh

#Sets Environment Variables for navigation convenience

ROOT=$(cd $(dirname "$0"); pwd) 

export WORKER=$ROOT/ots.worker/ots/worker
export SERVER=$ROOT/ots.server/ots/server
export COMMON=$ROOT/ots.common/ots/common 
export RESULTS=$ROOT/ots.results/ots/results
export OTS=$ROOT

PATH=$ROOT/ots.worker/ots/worker/tests/:$PATH