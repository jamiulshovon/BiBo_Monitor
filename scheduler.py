"""
scheduler.py - Continuous scheduler daemon for 6 AM, 10 AM, and 2 PM (Bangladesh Time).

Run this in a terminal or background process:
    python scheduler.py
"""

import time
import math
from datetime import datetime, timedelta, timezone
from take_screenshot import take_screenshot, BD_TZ
import config

TARGET_TIMES = [
    (6, 0, "06AM"),    # 06:00 AM BST
    (10, 0, "10AM"),   # 10:00 AM BST
    (14, 0, "02PM"),   # 02:00 PM BST (14:00)
]

def get_next_run():
    """Computes the next target datetime and label in Bangladesh Standard Time."""
    now = datetime.now(BD_TZ)
    today = now.date()

    candidates = []
    for hour, minute, tag in TARGET_TIMES:
        dt = datetime(today.year, today.month, today.day, hour, minute, 0, tzinfo=BD_TZ)
        if dt > now:
            candidates.append((dt, tag))

    # If all target times for today have passed, get the first one tomorrow
    if not candidates:
        tomorrow = today + timedelta(days=1)
        first_hour, first_minute, first_tag = TARGET_TIMES[0]
        dt = datetime(tomorrow.year, tomorrow.month, tomorrow.day, first_hour, first_minute, 0, tzinfo=BD_TZ)
        candidates.append((dt, first_tag))

    candidates.sort(key=lambda x: x[0])
    return candidates[0]

def main():
    print("=" * 60)
    print("BiBoTracker Admin - Automated Daily Scheduler")
    print(f"Schedules (Bangladesh Time - BST): {', '.join([t[2] for t in TARGET_TIMES])}")
    print("=" * 60)

    while True:
        next_dt, tag = get_next_run()
        now = datetime.now(BD_TZ)
        seconds_to_wait = (next_dt - now).total_seconds()

        hours = int(seconds_to_wait // 3600)
        minutes = int((seconds_to_wait % 3600) // 60)
        seconds = int(seconds_to_wait % 60)

        next_str = next_dt.strftime("%Y-%m-%d %I:%M:%S %p %Z")
        print(f"\n[NEXT RUN] {next_str} ({tag})")
        print(f"[WAITING] Sleeping for {hours}h {minutes}m {seconds}s...")

        # Sleep in chunks of up to 60 seconds to stay responsive
        while seconds_to_wait > 0:
            sleep_chunk = min(seconds_to_wait, 60)
            time.sleep(sleep_chunk)
            now = datetime.now(BD_TZ)
            seconds_to_wait = (next_dt - now).total_seconds()

        print(f"\n>>> Triggering scheduled capture for {tag} <<<")
        try:
            take_screenshot(tag=tag)
        except Exception as e:
            print(f"[ERROR during scheduled capture] {e}")

        # Short pause to prevent re-triggering within the same minute
        time.sleep(5)

if __name__ == "__main__":
    main()
