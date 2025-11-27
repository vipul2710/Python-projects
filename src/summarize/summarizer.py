# src/summarize/summarizer.py

import textwrap
from datetime import datetime
from src.normalize.db import Database
from src.summarize.model_router import ModelRouter


class Summarizer:
    """
    SIMPLE + STABLE summarizer:
    - NO metadata extraction (we already get perfect metadata from ingestion)
    - Only generates brief + extended summary
    - Saves to DB
    """

    def __init__(self, provider="openai"):
        self.db = Database()
        self.router = ModelRouter()
        self.provider = provider

        # Load prompt files
        with open("configs/prompts/brief.md", "r", encoding="utf-8") as f:
            self.brief_prompt = f.read()
        with open("configs/prompts/extended.md", "r", encoding="utf-8") as f:
            self.extended_prompt = f.read()

    # ---------------------------------------
    # SINGLE ARTICLE SUMMARIZATION
    # ---------------------------------------
    def summarize_article(self, row):
        title = row.get("title") or ""
        content = row.get("content") or ""
        snippet = textwrap.shorten(content, width=900, placeholder="...")

        # BRIEF
        brief_prompt = (
            f"{self.brief_prompt}\n\nTitle: {title}\n\nArticle excerpt:\n{snippet}"
        )
        brief = self.router.complete(
            brief_prompt,
            provider=self.provider,
            mode="brief",
            category=row.get("category", "General"),
        )

        # EXTENDED
        long_prompt = (
            f"{self.extended_prompt}\n\nTitle: {title}\n\nArticle excerpt:\n{snippet}"
        )
        extended = self.router.complete(
            long_prompt,
            provider=self.provider,
            mode="extended",
            category=row.get("category", "General"),
        )

        return {"summary_brief": brief, "summary_extended": extended}

    # ---------------------------------------
    # SAVE into DB
    # ---------------------------------------
    def save_summary(self, row_id, data):
        tbl = self.db.db["articles"]
        tbl.update(row_id, data)


    # ---------------------------------------
    # MAIN RUN
    # ---------------------------------------
    def run(self, limit=5):
        tbl = self.db.db["articles"]

        rows = list(
            tbl.rows_where(
                "summary_brief IS NULL OR summary_brief = '' LIMIT :lim",
                {"lim": limit},
            )
        )
        print(f"📝 Pending summaries: {len(rows)}")

        for row in rows:
            try:
                print(f"➡ Summarizing: {row['title']}")

                result = self.summarize_article(row)

                # PRIMARY KEY = hash
                self.save_summary(row["hash"], result)

                print(f"✅ Saved summary: {row['title']}")
            except Exception as e:
                print(f"❌ Failed: {row['title']} → {e}")
