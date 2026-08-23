#!/usr/bin/env bash
# Run this script on the RHEL box (as root or with sudo) to install
# and enable the k9-dow-pod systemd service.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_FILE="$SCRIPT_DIR/k9-dow-pod.service"
TARGET="/etc/systemd/system/k9-dow-pod.service"

echo "Installing k9-dow-pod.service ..."
cp "$SERVICE_FILE" "$TARGET"
chmod 644 "$TARGET"

systemctl daemon-reload
systemctl enable k9-dow-pod.service
systemctl start  k9-dow-pod.service

echo ""
systemctl status k9-dow-pod.service --no-pager
echo ""
echo "Done. k9-dow-pod will now auto-start on every boot."
