import arxiv
from datetime import datetime, timedelta, timezone
import hashlib
from src.normalize.db import Database
from src.normalize.deduper import Deduper

# ---------------- STRICT / OPTIONAL / NEGATIVE ----------------
STRICT_POSITIVES = [
    "video game", "video games",
    "game design", "game development",
    "player experience", "player modeling",
    "playtesting", "serious games",
    "educational games", "interactive storytelling"
]

OPTIONAL_POSITIVES = [
    "gameplay", "gamified", "game mechanics",
    "procedural content generation", "pcg",
    "human-computer interaction", "hci"
]

HARD_NEGATIVES = [
    # RL / simulation noise
    "reinforcement learning", "rl", "chip-8", "arcade environment", "atari",

    # Economics / math
    "game theory", "endgame", "financial", "auction", "pricing", "bundle", "bundling",

    # Robotics / traffic / vehicles
    "robot", "robotics", "drone",
    "traffic", "vehicle", "car-following", "truck", "axle",

    # Medical / law / other noise
    "medical", "disease", "surgery", "biomechanics",
    "law", "legal", "economics", "market", "policy", "regulation"
]

# ---------------- RELEVANCE CHECK ----------------
def is_relevant(paper: dict, debug: bool = False) -> bool:
    title = paper['title'].lower()
    abstract = paper['content'].lower()
    text = f"{title} {abstract}"

    # 1. Block negatives (immediate reject)
    for bad in HARD_NEGATIVES:
        if bad in text:
            if debug:
                print(f"⏭️ Skip (negative: {bad}): {paper['title']}")
            return False

    # 2. Strict positives (one is enough)
    for kw in STRICT_POSITIVES:
        if kw in text:
            if debug:
                print(f"✅ KEEP (strict match: {kw}): {paper['title']}")
            return True

    # 3. Optional positives (need at least 2 matches)
    optional_matches = [opt for opt in OPTIONAL_POSITIVES if opt in text]
    if len(optional_matches) >= 2:
        if debug:
            print(f"✅ KEEP (optional combo: {optional_matches}): {paper['title']}")
        return True

    # 4. Otherwise skip
    if debug:
        print(f"⏭️ Skip (no strong match): {paper['title']}")
    return False


# ---------------- FETCH ----------------
def fetch_arxiv_papers(
    query='"video game" OR "game design" OR "player modeling" OR "human-computer interaction" OR "gameplay"',
    max_results=20,
    category="Arxiv_AI_Gaming_Filtered",
    days_back=30
):
    """
    Fetch latest arXiv papers for a given query and time window.
    Filters results manually by published date.
    Returns a list of dicts compatible with our DB schema.
    """
    today = datetime.now(timezone.utc)
    cutoff = today - timedelta(days=days_back)

    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=max_results * 2,  # fetch more, filter later
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending,
    )

    results = []
    for result in client.results(search):
        if result.published < cutoff:
            continue

        paper = {
            "url": result.entry_id,
            "title": (result.title or "").strip(),
            "published_at": result.published.strftime("%Y-%m-%d %H:%M:%S"),
            "content": (result.summary or "").strip(),
            "hash": None,
            "category": category,
            "summary_brief": None,
            "summary_extended": None,
        }
        results.append(paper)

        if len(results) >= max_results:
            break

    return results


# ---------------- INGEST ----------------
def ingest_arxiv(
    query='"video game" OR "game design" OR "player modeling" OR "human-computer interaction" OR "gameplay"',
    max_results=20,
    category="Arxiv_AI_Gaming_Filtered",
    days_back=30
):
    """
    Fetch arXiv papers and insert into DB with dedup + relevance filter.
    """
    db = Database()
    deduper = Deduper()

    papers = fetch_arxiv_papers(query=query, max_results=max_results, category=category, days_back=days_back)
    inserted = 0
    for paper in papers:
        if not is_relevant(paper, debug=True):
            continue

        dedup_text = paper["title"] + " " + paper["content"] + " " + paper["url"]
        paper["hash"] = hashlib.sha256(dedup_text.encode("utf-8")).hexdigest()

        if deduper.is_duplicate(paper["hash"]):
            print(f"❌ Duplicate skipped: {paper['title']}")
            continue

        db.insert_article(paper)
        inserted += 1
        print(f"✅ Inserted: {paper['title']}")

    print(f"📚 Total inserted: {inserted}")
