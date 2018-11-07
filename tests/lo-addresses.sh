#!/bin/sh
set -eu

die () {
    echo "$1"
    exit 1
}

if [ $# -eq 0 ] || ([ "$1" != add ] && [ "$1" != del ]) ; then
    die "usage: sudo $0 add|del"
fi

for i in $(seq 1 16) ; do
    if [[ "$1" == "del" ]]; then
        echo "del $i";
        ifconfig lo0 -alias 127.0.1.$i;
    else
        echo "add $i";
        ifconfig lo0 alias 127.0.1.$i;
    fi
done
