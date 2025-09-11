from jinja2 import Environment, FileSystemLoader
from sqlite_utils import Database
from pathlib import Path

class Renderer:
    def __init__(self, db_path="data/cache/digest.db"):
        self.db = Database(db_path)
        self.env = Environment(loader=FileSystemLoader("template"))

    def fetch_articles(self, limit=10):
        return list(self.db["articles"].rows_where(
            "summary_brief IS NOT NULL",
            order_by="published_at DESC",
            limit=limit
        ))

    def render_html(self, output="digest.html", limit=10):
        articles = self.fetch_articles(limit=limit)
        template = self.env.get_template("digest.html")
        html_out = template.render(articles=articles)
        Path(output).write_text(html_out, encoding="utf-8")
        print(f"✅ HTML saved to {output}")

    def render_pdf(self, output="digest.pdf", limit=10):
        # Import WeasyPrint only if needed
        from weasyprint import HTML

        articles = self.fetch_articles(limit=limit)
        template = self.env.get_template("digest.html")
        html_out = template.render(articles=articles)
        HTML(string=html_out).write_pdf(output)
        print(f"✅ PDF saved to {output}")
