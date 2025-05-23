#!/usr/bin/env bash
# build.sh - Render build script

set -o errexit  # exit on error

echo "Starting Render build process..."

# Update package lists
apt-get update

# Install system dependencies
apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    xvfb \
    software-properties-common

# Install Google Chrome
echo "Installing Google Chrome..."
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list
apt-get update
apt-get install -y google-chrome-stable

# Verify Chrome installation
google-chrome --version || echo "Chrome installation may have issues"

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Build completed successfully!"