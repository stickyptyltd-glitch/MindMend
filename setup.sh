#!/bin/bash

# Update package list
sudo apt-get update

# Install python3-venv
sudo apt-get install -y python3-venv

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
