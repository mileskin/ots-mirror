#!/bin/sh


ROOT=$(cd $(dirname "$0"); pwd) 
echo $ROOT 
export WORKER=$ROOT/ots.worker/ots/worker
export SERVER=$ROOT/ots.server/ots/server
export COMMON=$ROOT/ots.common/ots/common 
export RESULTS=$ROOT/ots.results/ots/results

PATH=$ROOT/ots.worker/ots/worker/tests/:$PATH
