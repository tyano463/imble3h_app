#!/bin/bash

TRUE=1
FALSE=0

ARGC=$#
ARGV=$1
RET=
CDEV=/dev/ttyUSB0

function usage() {
    cat << EOF
usage:
    sudo ./writeable.sh [hex file name]
EOF
}
function writeable() {
    if [ `id -u` == 0 ] ; then
        RET=$TRUE
    else
        RET=$FALSE
    fi
}

function argcheck() {
    # echo "ARGC:$ARGC ARGV:$ARGV"
    if [ $ARGC -lt 1 ] ; then
        RET=$FALSE
    else
        if [ -e "$ARGV" ] ; then
            RET=$TRUE
        else
            RET=$FALSE
        fi
    fi
}

function check() {
    #echo "RET:$RET"
    if [ "$RET" != "$TRUE" ] ; then
        usage
        exit
    fi
}

function comcheck() {
    echo -ne "***?" | sudo tee ${CDEV}
    cat ${CDEV}
}

writeable ; check
#echo "ok1"
argcheck ; check
#echo "ok2"

comcheck ; check


