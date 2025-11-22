#!/bin/bash
# File: scripts/setup_tailscale.sh

echo "Configuring Tailscale..."

# Start Tailscale (will prompt for login)
sudo tailscale up

# Get cert for HTTPS
sudo tailscale cert gaas

# Save tailnet domain for later
DOMAIN=$(tailscale status | grep "$(hostname)" | awk '{print $1}')
echo "export GAAS_DOMAIN=$DOMAIN" >> ~/.bashrc

echo "✅ Tailscale configured"
echo "Your site: https://$DOMAIN"