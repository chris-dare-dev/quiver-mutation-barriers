#!/bin/sh
# build_archive.sh -- pack the stored results into the release archive of data/README.md.
# Usage: sh src/bookkeeping/build_archive.sh STAGING     STAGING holds one directory, experiments/, with the result files
# only (not research/, whose experiments/ holds the scripts as well); the archive's members keep that prefix
# Writes dist/mutation-barriers-data-v1.tar.xz and its .sha256.  The archive stores no user or group names.
set -e
NAME=mutation-barriers-data-v1
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$ROOT/dist"
tar --sort=name --owner=0 --group=0 --numeric-owner --format=gnu -C "$1" -cf - experiments | xz -9 -T1 > "$ROOT/dist/$NAME.tar.xz"
(cd "$ROOT/dist" && sha256sum "$NAME.tar.xz" > "$NAME.tar.xz.sha256" && cat "$NAME.tar.xz.sha256")
