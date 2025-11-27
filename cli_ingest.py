# cli_ingest.py
import hashlib
from src.ingest.rss_loader import load_sources, fetch_all_feeds
from src.normalize.text_cleaner import clean_article
from src.normalize.deduper import Deduper
from src.normalize.db import Database

def compute_hash(doi: str, title: str) -> str:
    seed = (doi or "") + "|" + (title or "")
    return hashlib.sha256(seed.lower().encode("utf-8")).hexdigest()

def run_ingestion(limit=10):
    print("🚀 Running ingestion...")

    sources = load_sources()
    raw_results = fetch_all_feeds(sources, limit=limit)

    deduper = Deduper()
    db = Database()

    for category, items in raw_results.items():
        for item in items:
            url = item["link"]
            cleaned = clean_article(url)

            title = cleaned.get("title") or item.get("title")
            doi = cleaned.get("doi")
            content = cleaned.get("content") or item.get("summary") or ""

            if not title or not content:
                continue

            # stable hash
            h = compute_hash(doi, title)

            if deduper.is_duplicate(h):
                print(f"❌ Duplicate skipped: {title}")
                continue

            article = {
                "url": url,
                "title": title,
                "published_at": item.get("published"),
                "content": content,
                "abstract": cleaned.get("abstract"),
                "authors": cleaned.get("authors"),
                "venue": cleaned.get("venue"),
                "doi": doi,
                "year": cleaned.get("year"),
                "keywords": cleaned.get("keywords"),
                "hash": h,
                "category": category,
                "summary_brief": None,
                "summary_extended": None,
                "visual_path": None,
            }

            db.insert_article(article)
            print(f"✅ Inserted: {title}")

if __name__ == "__main__":
    run_ingestion()
