#!/bin/bash

# Exit on error
set -e

# Update package lists and install Node.js, npm, git
sudo apt-get update
sudo apt-get install -y nodejs npm git

# Clone the latest MindMend code (if directory exists, pull latest)
if [ -d "MindMend" ]; then
  cd MindMend
  git pull
else
  git clone https://github.com/stickyptyltd-glitch/MindMend.git
  cd MindMend
fi

# Install dependencies
npm install

# Start the app (background, logs to server.log)
nohup node server.js > server.log 2>&1 &
