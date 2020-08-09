#!/usr/bin/env bash

pyver=$(python -c "from __future__ import print_function; import sys; print('{}{}'.format(*sys.version_info[0:2]))")
echo $pyver

echo $CI
echo $TRAVIS

if [ "$TOXENV" != "build" ] ; then
    tox
fi
