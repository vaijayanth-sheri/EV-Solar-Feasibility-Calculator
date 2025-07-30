#!/usr/bin/env bash
# exit on error
set -o errexit

apt-get update
apt-get install -y libpango-1.0-0 libharfbuzz0 libpangoft2-1.0-0
