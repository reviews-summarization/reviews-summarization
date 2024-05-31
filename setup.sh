#!/bin/bash

GIT_ROOT=$(git rev-parse --show-toplevel)
if [ $? -ne 0 ]; then
    exit 1
fi

CURRENT_DIR=$(pwd)

if [ "$GIT_ROOT" != "$CURRENT_DIR" ]; then
    echo "This script must be run from the root of the Git repository."
    exit 1
fi

/usr/bin/python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e ".[dev]"
pre-commit install

