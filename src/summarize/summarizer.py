# src/summarize/summarizer.py
from pathlib import Path
import textwrap
from src.normalize.db import Database
from src.summarize.model_router import ModelRouter  # <-- new import

PROMPT_DIR = Path("configs/prompts")

def load_prompt(name: str) -> str:
    p = PROMPT_DIR / name
    return p.read_text(encoding="utf-8")

class Summarizer:
    def __init__(self, provider: str = "mock"):
        self.db = Database()
        # preload prompts (editable files)
        self.brief_prompt = load_prompt("brief.md")
        self.extended_prompt = load_prompt("extended.md")
        # Model router instance to call LLM providers
        self.router = ModelRouter()
        self.provider = provider  # e.g., "mock", later "openai"

    def get_pending_articles(self, limit: int = 10):
        tbl = self.db.db["articles"]
        return list(tbl.rows_where("summary_brief IS NULL", order_by="published_at DESC", limit=limit))

    def summarize_article(self, row):
        # Build a compact context for the LLM (title + snippet)
        title = row.get("title") or ""
        content = row.get("content") or ""
        snippet = textwrap.shorten(content, width=800, placeholder="...")
        prompt_for_brief = f"{self.brief_prompt}\n\nTitle: {title}\n\nArticle excerpt:\n{snippet}"
        prompt_for_extended = f"{self.extended_prompt}\n\nTitle: {title}\n\nArticle excerpt:\n{snippet}"

        # --- Replace local mock with ModelRouter calls ---
        brief = self.router.complete(prompt_for_brief, provider=self.provider, mode="brief", category=row.get("category","General"))
        extended = self.router.complete(prompt_for_extended, provider=self.provider, mode="extended", category=row.get("category","General"))
        return brief, extended

    def run(self, limit: int = 10):
        pending = self.get_pending_articles(limit=limit)
        print(f"🔎 Found {len(pending)} articles to summarize.")
        for row in pending:
            brief, extended = self.summarize_article(row)
            pk = row["id"]
            self.db.db["articles"].update(pk, {
                "summary_brief": brief,
                "summary_extended": extended
            })
            print(f"✅ Summarized: {row.get('title')}")
