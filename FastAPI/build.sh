#!/usr/bin/env bash
# Render-optimized build script for FastAPI + Selenium

set -o errexit  # Exit immediately on error
set -o pipefail # Catch failures in pipes
set -o nounset  # Treat unset variables as errors

echo "🛠 Starting Render build process..."

# ======================
# System Dependencies
# ======================
echo "🔧 Installing system dependencies..."
sudo apt-get update -y
sudo apt-get install -y \
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
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt-get update -y
sudo apt-get install -y google-chrome-stable

# ======================
# Chrome Verification
# ======================
echo "✅ Verifying Chrome installation..."
if ! google-chrome --version; then
    echo "❌ Chrome verification failed!"
    exit 1
fi

# ======================
# Python Setup
# ======================
echo "🐍 Setting up Python environment..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "🎉 Build completed successfully!"