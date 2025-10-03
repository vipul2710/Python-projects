# run_weekly_digest.py
from src.ingest.arxiv_ingest import ingest_arxiv
from src.summarize.summarizer import Summarizer
from src.render.renderer import Renderer
from sqlite_utils import Database

CATEGORY = "Arxiv_AI_Gaming"

def reset_category(category=CATEGORY):
    db = Database("data/cache/digest.db")
    deleted = db["articles"].delete_where("category = :cat", {"cat": category})
    print(f"🗑️ Deleted {deleted} old {category} papers.")

def run_pipeline():
    # 1. Reset
    reset_category(CATEGORY)

    # 2. Ingest
    ingest_arxiv(
        query='("video game" OR "game design" OR "player modeling" OR "human-computer interaction")',
        max_results=20,
        category=CATEGORY,
        days_back=30
    )

    # 3. Summarize (category-limited)
    Summarizer(provider="openai").run(limit=10, category=CATEGORY)

    # 4. Render PDF (category-limited)
    Renderer().render_pdf(limit=10, category=CATEGORY)
    print("📄 Weekly digest generated: output.pdf")

if __name__ == "__main__":
    run_pipeline()
