import arxiv
from datetime import datetime

def fetch_arxiv_papers(query="gaming", max_results=5, category="Arxiv_AI_Gaming"):
    """
    Fetch latest arXiv papers for a given query.
    Returns a list of dicts compatible with our DB schema.
    """
    client = arxiv.Client()  # new way
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending
    )

    results = []
    for result in client.results(search):  # use client.results instead of search.results()
        paper = {
            "url": result.entry_id,
            "title": result.title.strip(),
            "published_at": result.published.strftime("%Y-%m-%d %H:%M:%S"),
            "content": result.summary.strip(),
            "hash": None,  # will be filled by deduper later
            "category": category,
            "summary_brief": None,
            "summary_extended": None
        }
        results.append(paper)

    return results

from src.normalize.db import Database
from src.normalize.deduper import Deduper

def ingest_arxiv(query="gaming", max_results=5, category="Arxiv_AI_Gaming"):
    """
    Fetch arXiv papers and insert into DB with dedup.
    """
    db = Database()
    deduper = Deduper()

    papers = fetch_arxiv_papers(query=query, max_results=max_results, category=category)
    inserted = 0
    for paper in papers:
        # compute hash for dedup
        paper["hash"] = deduper.compute_hash(paper["content"])
        if deduper.is_duplicate(paper["hash"]):
            print(f"❌ Duplicate skipped: {paper['title']}")
            continue
        db.insert_article(paper)
        inserted += 1
        print(f"✅ Inserted: {paper['title']}")

    print(f"📚 Total inserted: {inserted}")

