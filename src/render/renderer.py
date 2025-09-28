from jinja2 import Environment, FileSystemLoader
from sqlite_utils import Database
from pathlib import Path
from datetime import date

class Renderer:
    def __init__(self, db_path="data/cache/digest.db"):
        self.db = Database(db_path)
        self.env = Environment(loader=FileSystemLoader("templates"))

    def fetch_articles(self, limit=10, category=None):
        where_clause = "summary_brief IS NOT NULL"
        params = {}
        if category:
            where_clause += " AND category = :cat"
            params["cat"] = category

        return list(self.db["articles"].rows_where(
            where_clause + " ORDER BY published_at DESC",
            params,
            limit=limit
        ))

    def render_html(self, output="digest.html", limit=10, category=None):
        articles = self.fetch_articles(limit=limit, category=category)
        template = self.env.get_template("digest.html")
        html_out = template.render(articles=articles, now=date.today().isoformat())
        Path(output).write_text(html_out, encoding="utf-8")
        print(f"✅ HTML saved to {output}")

    def render_pdf(self, output="digest.pdf", limit=10, category=None):
        from weasyprint import HTML
        articles = self.fetch_articles(limit=limit, category=category)
        template = self.env.get_template("digest.html")
        html_out = template.render(articles=articles, now=date.today().isoformat())
        HTML(string=html_out).write_pdf(output)
        print(f"✅ PDF saved to {output}")

    def render_md(self, output="digest.md", limit=10, category=None):
        """
        Render digest as a Markdown file.
        """
        articles = self.fetch_articles(limit=limit, category=category)
        lines = [f"# Agentic AI Digest\n", f"**Date:** {date.today().isoformat()}\n"]

        current_cat = None
        for row in articles:
            if row["category"] != current_cat:
                current_cat = row["category"]
                lines.append(f"\n## {current_cat}\n")

            lines.append(f"### {row['title']}\n")
            lines.append(f"**Brief:** {row['summary_brief']}\n\n")
            lines.append(f"{row['summary_extended']}\n\n")
            lines.append(f"[Source]({row['url']})\n")

        Path(output).write_text("\n".join(lines), encoding="utf-8")
        print(f"✅ Markdown saved to {output}")

        



