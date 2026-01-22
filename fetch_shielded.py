#!/usr/bin/env python3
"""
Zcash Shielded Pool Fetcher
Fetches data from zcashexplorer.app and saves to JSON
Runs via GitHub Actions every 8 hours
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path

import requests

EXPLORER_URL = "https://mainnet.zcashexplorer.app/blockchain-info"
DATA_FILE = Path("shielded_data.json")
MAX_ENTRIES = 365  # Keep 1 year of data (3x per day = 1095, but we dedupe by date)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ZcashTracker/1.0)"
}


def fetch_shielded_pools() -> dict:
    """Fetch shielded pool balances from zcashexplorer.app"""
    resp = requests.get(EXPLORER_URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    html = resp.text

    pools = {}
    patterns = {
        "sprout": r"Sprout\s+Pool.*?<dd[^>]*>\s*([\d,]+\.?\d*)\s*ZEC",
        "sapling": r"Sapling\s+Pool.*?<dd[^>]*>\s*([\d,]+\.?\d*)\s*ZEC",
        "orchard": r"Orchard\s+Pool.*?<dd[^>]*>\s*([\d,]+\.?\d*)\s*ZEC",
    }

    for pool_name, pattern in patterns.items():
        match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
        if match:
            value_str = match.group(1).replace(",", "")
            pools[pool_name] = float(value_str)
        else:
            pools[pool_name] = 0.0

    return pools


def load_data() -> list:
    """Load existing data from JSON file"""
    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []


def save_data(data: list) -> None:
    """Save data to JSON file"""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def main():
    now = datetime.now(timezone.utc)
    today = now.strftime("%Y-%m-%d")
    timestamp = now.isoformat()

    print(f"[*] Fetching shielded pool data - {timestamp}")

    try:
        pools = fetch_shielded_pools()
        total = pools["sprout"] + pools["sapling"] + pools["orchard"]

        print(f"[+] Sprout:  {pools['sprout']:,.2f} ZEC")
        print(f"[+] Sapling: {pools['sapling']:,.2f} ZEC")
        print(f"[+] Orchard: {pools['orchard']:,.2f} ZEC")
        print(f"[+] TOTAL:   {total:,.2f} ZEC")

        if total == 0:
            print("[!] ERROR: Total is 0, skipping update")
            return

        # Load existing data
        data = load_data()

        # Create new entry
        entry = {
            "date": today,
            "timestamp": timestamp,
            "sprout": pools["sprout"],
            "sapling": pools["sapling"],
            "orchard": pools["orchard"],
            "total": total
        }

        # Update or append (keep latest per day)
        existing_idx = next((i for i, d in enumerate(data) if d["date"] == today), None)
        if existing_idx is not None:
            data[existing_idx] = entry
            print(f"[+] Updated existing entry for {today}")
        else:
            data.append(entry)
            print(f"[+] Added new entry for {today}")

        # Sort by date and keep only last MAX_ENTRIES
        data.sort(key=lambda x: x["date"])
        data = data[-MAX_ENTRIES:]

        # Save
        save_data(data)
        print(f"[+] Saved {len(data)} entries to {DATA_FILE}")

    except Exception as e:
        print(f"[!] ERROR: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
