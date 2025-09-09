# src/summarize/summarizer.py
from pathlib import Path
import textwrap
from src.normalize.db import Database

PROMPT_DIR = Path("configs/prompts")

def load_prompt(name: str) -> str:
    p = PROMPT_DIR / name
    return p.read_text(encoding="utf-8")

def mock_generate(text: str, mode: str, category: str) -> str:
    """
    Very small deterministic mock summarizer for testing.
    - mode == 'brief' -> return 2 short bullets.
    - mode == 'extended' -> return 'Why it matters' + 2 recommendations.
    """
    # take first 120 chars as a seed
    seed = textwrap.shorten(text, width=120, placeholder="...")
    if mode == "brief":
        # naive bullet creation from seed
        bullets = [
            f"• {seed.split('.')[0].strip()}",
            f"• Monitor developments in {category.replace('_',' ')}."
        ]
        return "\n".join(bullets)
    else:
        why = f"Why it matters: This affects {category.replace('_',' ')} and related workflows."
        recs = [
            "- Run a small POC to measure impact.",
            "- Track metrics weekly and reassess."
        ]
        return f"{why}\n\nRecommendations:\n" + "\n".join(recs)

class Summarizer:
    def __init__(self):
        self.db = Database()
        # preload prompts (editable files)
        self.brief_prompt = load_prompt("brief.md")
        self.extended_prompt = load_prompt("extended.md")

    def get_pending_articles(self, limit: int = 10):
        tbl = self.db.db["articles"]
        # rows_where gives dict-like rows
        return list(tbl.rows_where("summary_brief IS NULL", order_by="published_at DESC", limit=limit))

    def summarize_article(self, row):
        # Build a compact context for the LLM (title + snippet)
        title = row.get("title") or ""
        content = row.get("content") or ""
        snippet = textwrap.shorten(content, width=800, placeholder="...")
        prompt_for_brief = f"{self.brief_prompt}\n\nTitle: {title}\n\nArticle excerpt:\n{snippet}"
        prompt_for_extended = f"{self.extended_prompt}\n\nTitle: {title}\n\nArticle excerpt:\n{snippet}"

        # In production, replace mock_generate with ModelRouter.complete(...)
        brief = mock_generate(snippet, mode="brief", category=row.get("category","General"))
        extended = mock_generate(snippet, mode="extended", category=row.get("category","General"))
        return brief, extended

    def run(self, limit: int = 10):
        pending = self.get_pending_articles(limit=limit)
        print(f"🔎 Found {len(pending)} articles to summarize.")
        for row in pending:
            brief, extended = self.summarize_article(row)
            # Update DB row by primary key id
            pk = row["id"]
            self.db.db["articles"].update(pk, {
                "summary_brief": brief,
                "summary_extended": extended
            })
            print(f"✅ Summarized: {row.get('title')}")
