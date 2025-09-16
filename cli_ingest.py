from src.ingest.rss_loader import load_sources, fetch_all_feeds
from src.normalize.text_cleaner import clean_article
from src.normalize.deduper import Deduper
from src.normalize.db import Database
import hashlib

def compute_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def run_ingestion(limit=2):
    print("🚀 Running ingestion pipeline...")

    # Step 1: load sources
    sources = load_sources()

    # Step 2: fetch raw feed items
    raw_results = fetch_all_feeds(sources, limit=limit)

    # Step 3: init helpers
    deduper = Deduper()
    db = Database()

    # Step 4: process items
    for category, items in raw_results.items():
        print(f"\n📂 {category} ({len(items)} items)")
        for item in items:
            url = item["link"]
            cleaned = clean_article(url)

            if not cleaned["content"]:
                continue  # skip empty

            # Create article record
            article = {
                "url": url,
                "title": cleaned["title"] or item["title"],
                "published_at": item["published"],
                "content": cleaned["content"],
                "hash": compute_hash(cleaned["content"]),
                "category": category,
                "summary_brief": None,
                "summary_extended": None
            }

            # Dedup check (in-memory + DB)
            if deduper.is_duplicate(article["hash"]):
                print(f"❌ Duplicate skipped: {article['title']}")
                continue

            db.insert_article(article)

if __name__ == "__main__":
    run_ingestion()
