# re_summarize_recent.py
from src.normalize.db import Database
from src.summarize.summarizer import Summarizer
import sys

def reset_and_resummarize(n=5):
    db = Database()
    tbl = db.db["articles"]

    # Fetch latest n articles by published_at (adjust ordering if you prefer id)
    rows = list(tbl.rows_where("1=1 ORDER BY published_at DESC", limit=n))
    ids = [r["id"] for r in rows]

    if not ids:
        print("No articles found.")
        return

    print(f"Resetting summaries for article IDs: {ids}")
    for pid in ids:
        tbl.update(pid, {"summary_brief": None, "summary_extended": None})

    # Now run summarizer for those (limit=n)
    Summarizer().run(limit=n)

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    reset_and_resummarize(n)
