# src/ingest/rss_loader.py

import feedparser
import yaml
from pathlib import Path
from typing import List, Dict


def load_sources(config_path: str = "configs/sources.yaml") -> Dict[str, List[str]]:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def fetch_feed(url: str, limit: int = 3):
    parsed = feedparser.parse(url)
    items = []

    for entry in parsed.entries[:limit]:
        items.append({
            "title": entry.get("title", "No title"),
            "link": entry.get("link"),
            "published": entry.get("published", "N/A"),
            "summary": entry.get("summary", ""),
        })
    return items


def fetch_all_feeds(sources: Dict[str, List[str]], limit: int = 2):
    all_items = {}

    for category, urls in sources.items():
        cat_items = []
        for url in urls:
            try:
                cat_items.extend(fetch_feed(url, limit=limit))
            except Exception as e:
                print(f"⚠️ Error fetching {url}: {e}")

        all_items[category] = cat_items

    return all_items
