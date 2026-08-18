# odpt — Odyssey PVR Nexus Showtime Tracker

Polls [District.in](https://www.district.in) for **The Odyssey** showtimes at **PVR Nexus (Formerly Forum), Koramangala** on Aug 21–23, 2026, and sends Telegram alerts when new showtimes appear.

Repo: https://github.com/architv/odpt

## Why not GitHub Actions or your laptop?

| Option | Problem |
|--------|---------|
| **GitHub Actions** | District.in blocks datacenter IPs (403) — doesn't work |
| **Your laptop** | Script stops when Mac sleeps/shuts down — unreliable |

**Recommended: Oracle Cloud free VM (Mumbai)** — always on, $0/month, Indian IP that District.in accepts.

→ **[Oracle Cloud setup guide](docs/oracle-cloud.md)** (15 min one-time setup)

## Behaviour

- Checks **Aug 21, 22, 23 2026**
- **Quiet hours:** skips 2:00–8:00 AM IST
- **No duplicate alerts** for the same showtime
- HTML-formatted Telegram messages

## Quick deploy (Oracle Cloud VM)

```bash
ssh ubuntu@YOUR_VM_IP
curl -fsSL https://raw.githubusercontent.com/architv/odpt/main/scripts/setup-oracle-vm.sh | sudo bash -s -- YOUR_BOT_TOKEN
```

## Manual run (local testing)

```bash
git clone https://github.com/architv/odpt.git && cd odpt
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export TELEGRAM_BOT_TOKEN="..." TELEGRAM_CHAT_ID="996147432"
python check_shows.py
```

## Files

- `check_shows.py` — checker + Telegram notifier
- `scripts/setup-oracle-vm.sh` — one-shot VM installer
- `docs/oracle-cloud.md` — full cloud setup guide
- `.github/workflows/check.yml` — kept for reference (blocked by District.in)
