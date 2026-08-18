#!/usr/bin/env python3
"""Check District.in for The Odyssey showtimes at PVR Nexus Koramangala."""

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo

from curl_cffi import requests

IST = ZoneInfo("Asia/Kolkata")
STATE_FILE = Path("last_state.json")

MOVIE_SLUG = "the-odyssey-movie-tickets-in-bengaluru-MV187151"
FORMAT_ID = "y7eznlxn5y"
CINEMA_ID = 1022297
CINEMA_NAME = "PVR Nexus (Formerly Forum), Koramangala"
TARGET_DATES = ["2026-08-21", "2026-08-22", "2026-08-23"]

DISTRICT_BASE = (
    "https://www.district.in/movies/"
    f"{MOVIE_SLUG}?frmtid={FORMAT_ID}&fromdate={{date}}"
)
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
REQUEST_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-IN,en;q=0.9",
    "Referer": "https://www.district.in/movies/bengaluru-movie-tickets",
}

QUIET_START = time(2, 0)
QUIET_END = time(8, 0)


@dataclass(frozen=True)
class Show:
    date: str
    sid: str
    show_time: str
    audi: str
    avail: int

    @property
    def key(self) -> str:
        return f"{self.date}|{self.sid}|{self.show_time}"

    def display_time(self) -> str:
        dt = datetime.fromisoformat(self.show_time).replace(tzinfo=ZoneInfo("UTC"))
        return dt.astimezone(IST).strftime("%I:%M %p").lstrip("0")

    def display_date(self) -> str:
        dt = datetime.fromisoformat(self.date)
        return dt.strftime("%A, %d %b %Y")


def is_quiet_hours(now: datetime | None = None) -> bool:
    now = now or datetime.now(IST)
    current = now.time()
    return QUIET_START <= current < QUIET_END


def load_state() -> set[str]:
    if not STATE_FILE.exists():
        return set()
    try:
        data = json.loads(STATE_FILE.read_text())
        return set(data.get("alerted_shows", []))
    except (json.JSONDecodeError, OSError):
        return set()


def save_state(alerted: set[str]) -> None:
    STATE_FILE.write_text(json.dumps({"alerted_shows": sorted(alerted)}, indent=2))


def fetch_sessions(date: str) -> list[Show]:
    url = DISTRICT_BASE.format(date=date)
    response = requests.get(
        url,
        headers=REQUEST_HEADERS,
        timeout=30,
        impersonate="chrome120",
    )
    response.raise_for_status()

    match = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
        response.text,
        re.DOTALL,
    )
    if not match:
        return []

    data = json.loads(match.group(1))
    server_state = data.get("props", {}).get("pageProps", {}).get("data", {}).get(
        "serverState", {}
    )
    session_key = f"{FORMAT_ID}{date}"
    movie_sessions = server_state.get("movieSessions", {}).get(session_key, {})
    arranged = movie_sessions.get("arrangedSessions", [])

    shows: list[Show] = []
    for item in arranged:
        cinema = item.get("data", {})
        if cinema.get("id") != CINEMA_ID:
            continue
        for session in item.get("sessions", []):
            avail = session.get("avail", 0)
            if avail <= 0:
                continue
            shows.append(
                Show(
                    date=date,
                    sid=str(session.get("sid", "")),
                    show_time=session.get("showTime", ""),
                    audi=session.get("audi", "Unknown"),
                    avail=avail,
                )
            )
    return shows


def format_message(shows: list[Show]) -> str:
    by_date: dict[str, list[Show]] = {}
    for show in sorted(shows, key=lambda s: (s.date, s.show_time)):
        by_date.setdefault(show.date, []).append(show)

    lines = [
        "🎬 <b>The Odyssey</b>",
        f"📍 {CINEMA_NAME}",
        "",
    ]

    for date in sorted(by_date):
        day_shows = by_date[date]
        lines.append(f"<b>{day_shows[0].display_date()}</b>")
        for show in day_shows:
            lines.append(
                f"  🕐 {show.display_time()}  ·  {show.audi}  ·  {show.avail} seats"
            )
        lines.append("")

    book_date = min(by_date)
    book_url = DISTRICT_BASE.format(date=book_date)
    lines.append(f'<a href="{book_url}">Book on District →</a>')
    return "\n".join(lines)


def send_telegram(message: str) -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise RuntimeError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set")

    response = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": False,
        },
        timeout=30,
    )
    response.raise_for_status()
    body = response.json()
    if not body.get("ok"):
        raise RuntimeError(f"Telegram API error: {body}")


def main() -> int:
    bypass_quiet = os.environ.get("BYPASS_QUIET_HOURS") == "1"
    if not bypass_quiet and is_quiet_hours():
        print("Quiet hours (2:00–8:00 AM IST), skipping.")
        return 0

    alerted = load_state()
    all_shows: list[Show] = []

    for date in TARGET_DATES:
        try:
            shows = fetch_sessions(date)
            all_shows.extend(shows)
            print(f"{date}: found {len(shows)} show(s) at target cinema")
        except requests.RequestException as exc:
            print(f"{date}: fetch failed — {exc}", file=sys.stderr)

    new_shows = [show for show in all_shows if show.key not in alerted]
    if not new_shows:
        print("No new shows to alert.")
        return 0

    message = format_message(new_shows)
    send_telegram(message)

    for show in new_shows:
        alerted.add(show.key)
    save_state(alerted)

    print(f"Alerted for {len(new_shows)} new show(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
