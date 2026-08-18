#!/bin/bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PLIST_NAME="com.archit.odyssey-pvr-tracker"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_NAME}.plist"
VENV_PYTHON="$PROJECT_DIR/.venv/bin/python"
SCRIPT="$PROJECT_DIR/check_shows.py"
ENV_FILE="$PROJECT_DIR/.env"

if [[ ! -x "$VENV_PYTHON" ]]; then
  echo "Creating virtualenv..."
  python3 -m venv "$PROJECT_DIR/.venv"
  "$PROJECT_DIR/.venv/bin/pip" install -r "$PROJECT_DIR/requirements.txt"
  "$PROJECT_DIR/.venv/bin/python" -m playwright install chromium
fi

if [[ ! -f "$ENV_FILE" ]]; then
  cat > "$ENV_FILE" <<'EOF'
TELEGRAM_BOT_TOKEN=your-token-here
TELEGRAM_CHAT_ID=996147432
EOF
  echo "Created $ENV_FILE — add your TELEGRAM_BOT_TOKEN before running."
fi

mkdir -p "$HOME/Library/LaunchAgents"

cat > "$PLIST_PATH" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${PLIST_NAME}</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>-lc</string>
    <string>set -a; source "${ENV_FILE}"; set +a; exec "${VENV_PYTHON}" "${SCRIPT}"</string>
  </array>
  <key>StartInterval</key>
  <integer>600</integer>
  <key>RunAtLoad</key>
  <true/>
  <key>StandardOutPath</key>
  <string>${PROJECT_DIR}/tracker.log</string>
  <key>StandardErrorPath</key>
  <string>${PROJECT_DIR}/tracker.log</string>
</dict>
</plist>
PLIST

launchctl bootout "gui/$(id -u)/${PLIST_NAME}" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST_PATH"
launchctl enable "gui/$(id -u)/${PLIST_NAME}"
launchctl kickstart -k "gui/$(id -u)/${PLIST_NAME}"

echo "Installed local scheduler: runs every 10 minutes"
echo "Logs: $PROJECT_DIR/tracker.log"
echo "Stop with: launchctl bootout gui/$(id -u)/${PLIST_NAME}"
