#!/bin/bash

set -eu

ARCHIVE_URL=$(curl -sL https://api.github.com/repos/thombashi/sqlitebiter/releases/latest | jq -r '.assets[].browser_download_url' | \grep deb)
TEMP_DEB="$(mktemp)"

trap "\rm -f $TEMP_DEB" 0 1 2 3 15
curl -L ${ARCHIVE_URL} -o ${TEMP_DEB}
dpkg -i "${TEMP_DEB}"
