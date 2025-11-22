#!/bin/bash
# File: scripts/setup_system.sh

echo "Installing system dependencies..."

sudo apt update
sudo apt install -y \
    python3.12 \
    python3.12-venv \
    python3-pip \
    git \
    sqlite3 \
    build-essential \
    libssl-dev \
    libffi-dev \
    curl

# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

echo "✅ System dependencies installed"