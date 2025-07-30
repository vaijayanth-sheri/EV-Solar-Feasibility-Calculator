#!/usr/bin/env bash
# exit on error
set -o errexit

# --- System Dependencies for WeasyPrint ---
apt-get update
apt-get install -y libpango-1.0-0 libharfbuzz0 libpangoft2-1.0-0

# --- Python Dependencies ---
pip install --upgrade pip
pip install -r requirements.txt
