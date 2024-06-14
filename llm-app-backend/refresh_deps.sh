#!/bin/bash
set -e
pip install --upgrade pip-tools
pip install --upgrade pip
pip-compile --upgrade
pip-sync
