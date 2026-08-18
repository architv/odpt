# Odyssey PVR Nexus Showtime Tracker

Polls [District.in](https://www.district.in) every 10 minutes for **The Odyssey** showtimes at **PVR Nexus (Formerly Forum), Koramangala** on Aug 21–23, 2026, and sends Telegram alerts for new showtimes.

## Behaviour

- Checks dates: **21, 22, 23 August 2026**
- **Quiet hours:** no checks between 2:00–8:00 AM IST
- **No duplicate alerts:** each showtime is notified once, ever
- **Readable Telegram messages** with HTML formatting

## Local setup

```bash
pip install -r requirements.txt
export TELEGRAM_BOT_TOKEN="your-bot-token"
export TELEGRAM_CHAT_ID="996147432"
python check_shows.py
```

To test outside quiet hours or force a run:

```bash
BYPASS_QUIET_HOURS=1 python check_shows.py
```

## GitHub Actions deployment

1. Push this repo as a **public** repository (required for free scheduled workflows).
2. Add secrets under **Settings → Secrets and variables → Actions**:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID` = `996147432`
3. The workflow runs every 10 minutes automatically.
4. Trigger manually via **Actions → Check Odyssey Showtimes → Run workflow**.

## Files

- `check_shows.py` — main checker script
- `.github/workflows/check.yml` — scheduled runner
- `last_state.json` — cached alerted show IDs (gitignored locally; persisted via Actions cache in CI)
