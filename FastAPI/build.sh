#!/usr/bin/env bash
# Render-optimized build script (no sudo)

set -o errexit
set -o pipefail
set -o nounset

echo "🛠 Starting Render build process..."

# ======================
# System Dependencies
# ======================
echo "🔧 Installing system dependencies..."
apt-get update -y
apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    xvfb \
    software-properties-common \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1

# ======================
# Chrome Installation
# ======================
echo "🌐 Installing Google Chrome..."
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
apt-get update -y
apt-get install -y google-chrome-stable

# ======================
# Python Setup
# ======================
echo "🐍 Setting up Python environment..."
python -m pip install --upgrade pip
pip install poetry
poetry install --no-dev

echo "🎉 Build completed successfully!"