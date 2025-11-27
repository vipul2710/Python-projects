#!/usr/bin/env python3
# scripts/fill_metadata_only.py

"""
Populate metadata for existing articles without re-running summaries.

Usage:
  # dry run (safe)
  python scripts/fill_metadata_only.py --limit 5 --dry-run

  # update metadata for ALL articles
  python scripts/fill_metadata_only.py --limit 50

  # update ONLY ACM HCI gaming papers
  python scripts/fill_metadata_only.py --limit 50 --only-acm-hci-games
"""

import sys
import os

# --- IMPORTANT: add project root to sys.path ---
PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import argparse
import time

from src.summarize.summarizer import Summarizer
from src.normalize.db import Database


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--limit", type=int, default=0, help="Limit number of rows (0 = no limit)")
    p.add_argument("--dry-run", action="store_true", help="Print updates but do not write to DB")
    
    # FIXED: default = False
    p.add_argument(
        "--only-acm-hci-games",
        action="store_true",
        help="Process ONLY ACM HCI gaming papers (default: OFF)"
    )

    args = p.parse_args()

    print("Project root:", PROJECT_ROOT)
    print("Python executable:", sys.executable)
    print("sys.path[0]:", sys.path[0])

    s = Summarizer()
    db = Database()

    tbl = db.db["articles"]
    q = "doi IS NULL OR doi = '' OR authors IS NULL OR authors = '' OR year IS NULL OR year = ''"

    limit = None if args.limit == 0 else args.limit
    rows = list(tbl.rows_where(q + " ORDER BY published_at DESC", {}, limit=limit))

    print(f"Found {len(rows)} rows needing metadata")

    for r in rows:
        if args.only_acm_hci_games:
            if not s._is_acm_hci_game(r):
                print(f"Skipping (not ACM HCI gaming): {r.get('title')}")
                continue

        pk = r["id"]
        meta = s.extract_metadata(r.get("title") or "", r.get("content") or "")
        
        payload = {
            "authors": meta.get("authors"),
            "venue": meta.get("venue"),
            "doi": meta.get("doi"),
            "year": meta.get("year"),
            "keywords": meta.get("keywords"),
            "metadata_extracted": 1
        }

        print(f"Row {pk} => {payload}")

        if not args.dry_run:
            try:
                tbl.update(pk, payload)
                print("✔ Updated", pk)
            except Exception as e:
                print("✖ Update failed", pk, e)

        time.sleep(0.4)


if __name__ == "__main__":
    main()
