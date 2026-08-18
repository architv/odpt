# Odyssey PVR Nexus Showtime Tracker

Polls [District.in](https://www.district.in) every 10 minutes for **The Odyssey** showtimes at **PVR Nexus (Formerly Forum), Koramangala** on Aug 21–23, 2026, and sends Telegram alerts for new showtimes.

## Behaviour

- Checks dates: **21, 22, 23 August 2026**
- **Quiet hours:** no checks between 2:00–8:00 AM IST
- **No duplicate alerts:** each showtime is notified once, ever
- **Readable Telegram messages** with HTML formatting

## Recommended: local Mac scheduler

District.in blocks cloud datacenter IPs (including GitHub Actions), so the reliable deployment is a **local scheduler on your Mac**. The script already handles quiet hours and deduplication.

```bash
cd ~/Projects/odyssey-pvr-tracker
chmod +x scripts/install-local-cron.sh
./scripts/install-local-cron.sh
```

This installs a LaunchAgent that runs every 10 minutes. Your Mac needs to be awake; plug it in or disable sleep while tracking.

Logs: `~/Projects/odyssey-pvr-tracker/tracker.log`

Stop the scheduler:

```bash
launchctl bootout gui/$(id -u)/com.archit.odyssey-pvr-tracker
```

## Manual run

```bash
cd ~/Projects/odyssey-pvr-tracker
source .venv/bin/activate
set -a; source .env; set +a
python check_shows.py
```

Force a run during quiet hours:

```bash
BYPASS_QUIET_HOURS=1 python check_shows.py
```

## GitHub Actions (optional, currently blocked)

A workflow is included at `.github/workflows/check.yml`, but District.in returns **403** from GitHub's datacenter IPs even with browser fallback. Secrets are configured on the repo if District changes this later.

Repo: https://github.com/architv/odyssey-pvr-tracker

## Files

- `check_shows.py` — main checker script
- `scripts/install-local-cron.sh` — installs macOS LaunchAgent
- `.github/workflows/check.yml` — optional cloud runner (blocked by District.in)
- `last_state.json` — alerted show IDs (gitignored locally)
