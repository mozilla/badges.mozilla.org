#!/bin/bash
PORT=9002
MINSPARE=4
MAXSPARE=8
MAXCHILDREN=16
MAXREQUESTS=25

pushd `dirname $0` >/dev/null
BASE_DIR=`pwd`
PIDFILE=$BASE_DIR/fcgi.pid
. ./venv/bin/activate
if [ -f $PIDFILE ]; then
	cat $PIDFILE | xargs kill -9;
	rm $PIDFILE;
fi;
./manage.py runfcgi host=127.0.0.1 port=$PORT demonize=true \
	pidfile=$PIDFILE maxrequests=$MAXREQUESTS maxchildren=$MAXCHILDREN \
	maxspare=$MAXSPARE minspare=$MINSPARE \
	outlog=$BASE_DIR/fcgi.out errlog=$BASE_DIR/fcgi.err
PID=`cat $PIDFILE`
echo "Restarted as PID $PID"
popd >/dev/null

# This is handy with a .git/hooks/post-receive like:
#
# unset GIT_DIR
# cd ..
# git reset --hard
# git submodule sync
# git submodule update --init --recursive
# ./restart.sh
#
# And don't forget this in .git/config
#
#     [receive]
#         denyCurrentBranch = ignore
