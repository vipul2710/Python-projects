from jinja2 import Environment, FileSystemLoader
from sqlite_utils import Database
from pathlib import Path
from datetime import date
import os


class Renderer:
    def __init__(self, db_path="data/cache/digest.db"):
        self.db = Database(db_path)
        self.env = Environment(loader=FileSystemLoader("templates"))

    # -----------------------------
    # Fetch articles with summaries
    # -----------------------------
    def fetch_articles(self, limit=50, category=None):
        where_clause = "summary_brief IS NOT NULL AND summary_brief != ''"
        params = {}

        if category:
            where_clause += " AND category = :cat"
            params["cat"] = category

        rows = list(
            self.db["articles"].rows_where(
                where_clause + " ORDER BY published_at DESC",
                params,
                limit=limit,
            )
        )

        # Normalize visual_path to file:// URIs
        for r in rows:
            vp = r.get("visual_path")
            if vp:
                p = Path(vp).resolve()
                r["visual_path"] = p.as_uri()

        return rows

    # -----------------------------
    # Render HTML
    # -----------------------------
    def render_html(self, output="digest.html", limit=50, category=None):
        articles = self.fetch_articles(limit=limit, category=category)
        template = self.env.get_template("digest.html")

        html_out = template.render(
            articles=articles,
            now=date.today().isoformat(),
        )

        Path(output).write_text(html_out, encoding="utf-8")
        print(f"✅ HTML saved to {output}")

    # -----------------------------
    # Render PDF using WeasyPrint
    # -----------------------------
    def render_pdf(self, output="digest.pdf", limit=50, category=None):
        from weasyprint import HTML

        articles = self.fetch_articles(limit=limit, category=category)
        template = self.env.get_template("digest.html")

        html_out = template.render(
            articles=articles,
            now=date.today().isoformat(),
        )

        project_root = Path(__file__).resolve().parents[2]
        base_url = project_root.as_uri()
        print(f"BASE URL USED: {base_url}")

        HTML(string=html_out, base_url=base_url).write_pdf(output)
        print(f"✅ PDF saved to {output}")

    # -----------------------------
    # Render Markdown
    # -----------------------------
    def render_md(self, output="digest.md", limit=50, category=None):
        articles = self.fetch_articles(limit=limit, category=category)
        lines = [
            "# Agentic AI Digest\n",
            f"**Date:** {date.today().isoformat()}\n",
        ]

        current_cat = None
        for row in articles:
            if row["category"] != current_cat:
                current_cat = row["category"]
                lines.append(f"\n## {current_cat}\n")

            lines.append(f"### {row['title']}\n")

            if row.get("authors") or row.get("venue") or row.get("year"):
                lines.append(
                    f"*{row.get('authors','Unknown')} | "
                    f"{row.get('venue','Unknown')} | "
                    f"{row.get('year','Unknown')}*\n"
                )

            lines.append(f"**Brief:** {row['summary_brief']}\n\n")
            lines.append(f"{row['summary_extended']}\n\n")

            if row.get("visual_path"):
                lines.append(f"![diagram]({row['visual_path']})\n")

            if row.get("url"):
                lines.append(f"[Source]({row['url']})\n")

        Path(output).write_text("\n".join(lines), encoding="utf-8")
        print(f"✅ Markdown saved to {output}")

    # -----------------------------
    # Unified call
    # -----------------------------
    def render_digest(self, html=True, pdf=True, md=False, limit=50):
        if html:
            self.render_html(limit=limit)
        if pdf:
            self.render_pdf(limit=limit)
        if md:
            self.render_md(limit=limit)
        print("✨ Digest generation complete.")
