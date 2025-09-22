# src/summarize/summarizer.py
from pathlib import Path
import textwrap
from src.normalize.db import Database
from src.summarize.model_router import ModelRouter  # <-- import model router

PROMPT_DIR = Path("configs/prompts")

def load_prompt(name: str) -> str:
    p = PROMPT_DIR / name
    return p.read_text(encoding="utf-8")

class Summarizer:
    def __init__(self, provider: str = "openai"):
        self.db = Database()
        # preload prompts (editable files)
        self.brief_prompt = load_prompt("brief.md")
        self.extended_prompt = load_prompt("extended.md")
        # Model router instance to call LLM providers
        self.router = ModelRouter()
        self.provider = provider  # e.g., "mock", "openai"

    def get_pending_articles(self, limit: int = 10, category: str = None):
        """
        Fetch pending articles that don't yet have summaries.
        If category is provided, filter by that category.
        """
        where_clause = "summary_brief IS NULL"
        params = {}

        if category:
            where_clause += " AND category = :cat"
            params["cat"] = category

        return list(self.db.db["articles"].rows_where(
            where_clause + " ORDER BY published_at DESC",
            params,
            limit=limit
        ))

    def summarize_article(self, row):
        """
        Generate brief + extended summaries for a given article row.
        """
        title = row.get("title") or ""
        content = row.get("content") or ""
        snippet = textwrap.shorten(content, width=800, placeholder="...")

        prompt_for_brief = f"{self.brief_prompt}\n\nTitle: {title}\n\nArticle excerpt:\n{snippet}"
        prompt_for_extended = f"{self.extended_prompt}\n\nTitle: {title}\n\nArticle excerpt:\n{snippet}"

        # Call via ModelRouter
        brief = self.router.complete(
            prompt_for_brief,
            provider=self.provider,
            mode="brief",
            category=row.get("category", "General")
        )
        extended = self.router.complete(
            prompt_for_extended,
            provider=self.provider,
            mode="extended",
            category=row.get("category", "General")
        )
        return brief, extended

    def run(self, limit: int = 10, category: str = None):
        """
        Summarize pending articles.
        Optionally filter by category.
        """
        pending = self.get_pending_articles(limit=limit, category=category)
        print(f"🔎 Found {len(pending)} articles to summarize.")
        for row in pending:
            brief, extended = self.summarize_article(row)
            pk = row["id"]
            self.db.db["articles"].update(pk, {
                "summary_brief": brief,
                "summary_extended": extended
            })
            print(f"✅ Summarized: {row.get('title')}")
