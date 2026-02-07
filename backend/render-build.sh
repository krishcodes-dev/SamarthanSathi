#!/usr/bin/env bash
# Exit on error
set -o errexit

# Upgrade pip to ensure we get the latest wheels
pip install --upgrade pip

# Install dependencies
# Using --prefer-binary to avoid compiling from source when wheels are available but slightly older
pip install -r requirements.txt --prefer-binary

# Download SpaCy model
python -m spacy download en_core_web_md
