from sqlite_utils import Database
from pathlib import Path

DB_PATH = "data/cache/digest.db"

db = Database(DB_PATH)

columns = {
    "url": str,
    "title": str,
    "published_at": str,
    "content": str,
    "abstract": str,
    "authors": str,
    "venue": str,
    "doi": str,
    "year": str,
    "keywords": str,
    "hash": str,
    "category": str,
    "summary_brief": str,
    "summary_extended": str,
    "visual_path": str,
}

# Drop if exists
if "articles" in db.table_names():
    print("Dropping old articles table...")
    db["articles"].drop()

# Recreate table
print("Creating fresh articles table...")
db.create_table(
    "articles",
    columns=columns,
    pk="hash",
    strict=True
)

print("✔ DONE — fresh schema created.")
