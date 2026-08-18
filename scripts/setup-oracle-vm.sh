#!/bin/bash
# Run this once on an Oracle Cloud Always Free VM (Ubuntu, Mumbai region).
# Usage: curl -fsSL https://raw.githubusercontent.com/architv/odpt/main/scripts/setup-oracle-vm.sh | bash -s -- YOUR_BOT_TOKEN

set -euo pipefail

BOT_TOKEN="${1:-}"
CHAT_ID="${TELEGRAM_CHAT_ID:-996147432}"
APP_DIR="/opt/odpt"
REPO="https://github.com/architv/odpt.git"

if [[ -z "$BOT_TOKEN" ]]; then
  echo "Usage: $0 TELEGRAM_BOT_TOKEN"
  echo "  or:  TELEGRAM_CHAT_ID=123 $0 TELEGRAM_BOT_TOKEN"
  exit 1
fi

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Run as root: sudo bash $0 $BOT_TOKEN"
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq git python3 python3-venv python3-pip

rm -rf "$APP_DIR"
git clone "$REPO" "$APP_DIR"
cd "$APP_DIR"

python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m playwright install --with-deps chromium

cat > "$APP_DIR/.env" <<EOF
TELEGRAM_BOT_TOKEN=${BOT_TOKEN}
TELEGRAM_CHAT_ID=${CHAT_ID}
EOF
chmod 600 "$APP_DIR/.env"

cat > /etc/systemd/system/odpt.service <<EOF
[Unit]
Description=Odyssey PVR Nexus showtime check (oneshot)
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
WorkingDirectory=${APP_DIR}
EnvironmentFile=${APP_DIR}/.env
ExecStart=${APP_DIR}/.venv/bin/python ${APP_DIR}/check_shows.py
StandardOutput=append:${APP_DIR}/tracker.log
StandardError=append:${APP_DIR}/tracker.log
EOF

cat > /etc/systemd/system/odpt.timer <<EOF
[Unit]
Description=Run odpt every 10 minutes

[Timer]
OnBootSec=2min
OnUnitActiveSec=10min
Persistent=true

[Install]
WantedBy=timers.target
EOF

systemctl daemon-reload
systemctl enable --now odpt.timer
systemctl start odpt.service

echo ""
echo "odpt installed at ${APP_DIR}"
echo "Timer: every 10 minutes (quiet hours 2-8 AM IST handled in script)"
echo "Logs:  tail -f ${APP_DIR}/tracker.log"
echo "Status: systemctl status odpt.timer"
