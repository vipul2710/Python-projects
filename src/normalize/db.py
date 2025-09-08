import sqlite_utils
from pathlib import Path
from typing import Dict, Any

DB_PATH = Path("data/cache/digest.db")

class Database:
    def __init__(self, db_path: Path = DB_PATH):
        self.db = sqlite_utils.Database(db_path)
        self._init_schema()

    def _init_schema(self):
        """Create articles table if it doesn't exist."""
        if "articles" not in self.db.table_names():
            self.db["articles"].create({
                "id": int,
                "url": str,
                "title": str,
                "published_at": str,
                "content": str,
                "hash": str,
                "category": str,
                "summary_brief": str,
                "summary_extended": str
            }, pk="id")

    def insert_article(self, article: Dict[str, Any]):
        """
        Insert article if not duplicate (by hash).
        """
        table = self.db["articles"]
        if table.exists():
            # check by hash
            existing = list(table.rows_where("hash = ?", [article["hash"]]))
            if existing:
                print(f"❌ Duplicate skipped: {article['title']}")
                return False
        table.insert(article)
        print(f"✅ Inserted: {article['title']}")
        return True

if __name__ == "__main__":
    db = Database()
    sample_article = {
        "url": "https://huggingface.co/blog/embeddinggemma",
        "title": "Welcome EmbeddingGemma, Google's new efficient embedding model",
        "published_at": "2025-09-06",
        "content": "This is sample cleaned text...",
        "hash": "abc12345",
        "category": "AI_ML_Analytics",
        "summary_brief": None,
        "summary_extended": None
    }
    db.insert_article(sample_article)
