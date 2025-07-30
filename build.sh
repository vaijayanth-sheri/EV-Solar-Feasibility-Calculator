#!/usr/bin/env bash
# exit on error
set -o errexit

# Install the system dependencies for WeasyPrint
apt-get update
apt-get install -y libpango-1.0-0 libharfbuzz0 libpangoft2-1.0-0
