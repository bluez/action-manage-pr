#!/bin/sh -l

set -e

if [[ -z $ACTION_TOKEN ]]; then
	echo "Set ACTION_TOKEN environment variable"
	exit 1
fi

TARGET_REPO=$1

echo "TARGET_REPO = $TARGET_REPO"

# Run script
/manage_pr.py -r $TARGET_REPO

