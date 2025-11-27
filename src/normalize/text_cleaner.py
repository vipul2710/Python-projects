# src/normalize/text_cleaner.py

import time
import re
import requests
from urllib.parse import urlparse
import cloudscraper
from readability import Document
from lxml import html
  # pymupdf

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/121.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://dl.acm.org/",
}

SCRAPER = cloudscraper.create_scraper(
    browser={"browser": "chrome", "platform": "windows", "mobile": False}
)

# ---------------------------------------------------------
# DOI extraction
# ---------------------------------------------------------
def extract_doi_from_url(url: str) -> str:
    """
    Convert ACM URL → clean DOI (10.xxx/yyyy)
    """
    if not url:
        return None

    # Remove query params
    u = url.split("?")[0]

    # Accept both /doi/ and /doi/abs/
    if "/doi/" in u:
        doi = u.split("/doi/")[1]
        doi = doi.replace("abs/", "").strip("/")
        return doi

    return None

# ---------------------------------------------------------
# CROSSREF Metadata
# ---------------------------------------------------------
def fetch_crossref_metadata(doi: str) -> dict | None:
    if not doi:
        return None

    url = f"https://api.crossref.org/works/{doi}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return None
        data = r.json()["message"]

        authors = []
        if "author" in data:
            for a in data["author"]:
                name = f"{a.get('given','')} {a.get('family','')}".strip()
                if name:
                    authors.append(name)

        venue = None
        if "container-title" in data and data["container-title"]:
            venue = data["container-title"][0]

        year = None
        if "published-print" in data:
            y = data["published-print"]["date-parts"][0][0]
            year = str(y)

        keywords = None
        if "subject" in data:
            keywords = ", ".join(data["subject"])

        return {
            "title": data.get("title", [""])[0],
            "authors": "; ".join(authors) if authors else None,
            "venue": venue,
            "doi": doi,
            "year": year,
            "keywords": keywords,
            "abstract": None,
            "content": None,  # Will be filled manually
        }
    except Exception:
        return None

# ---------------------------------------------------------
# PDF METADATA Fallback
# ---------------------------------------------------------
def extract_pdf_metadata_from_doi(doi: str) -> dict | None:
    """
    Download ACM PDF and extract metadata using PyMuPDF.
    Returns authors, year, abstract, keywords (best effort)
    """
    if not doi:
        return None

    pdf_url = f"https://dl.acm.org/doi/pdf/{doi}"
    try:
        resp = requests.get(pdf_url, headers=HEADERS)
        if resp.status_code != 200:
            print("⚠ PDF download failed:", resp.status_code)
            return None

        tmp = f"/tmp/{doi.replace('/', '_')}.pdf"
        with open(tmp, "wb") as f:
            f.write(resp.content)

        doc = fitz.open(tmp)
        text = doc[0].get_text()

        # Extract authors
        authors = None
        for ln in text.split("\n")[:20]:
            if "," in ln and ln.count(" ") > 2:
                authors = ln.strip()
                break

        # Extract year
        year = None
        y = re.search(r"(19|20)\d{2}", text)
        if y:
            year = y.group(0)

        # Extract abstract
        abstract = None
        m = re.search(r"(?is)abstract[:\s]+(.*?)\n\n", text)
        if m:
            abstract = m.group(1).strip()

        # Extract keywords
        keywords = None
        k = re.search(r"(?is)keywords?[:\s]+(.*?)\n", text)
        if k:
            keywords = k.group(1).strip()

        return {
            "authors": authors,
            "venue": None,        # PDFs rarely contain venue
            "year": year,
            "abstract": abstract,
            "keywords": keywords,
        }

    except Exception as e:
        print("⚠ PDF extract failed:", e)
        return None

# ---------------------------------------------------------
# Readability fallback
# ---------------------------------------------------------
def readability_fallback(url: str) -> dict:
    try:
        resp = SCRAPER.get(url, headers=HEADERS)
        doc = Document(resp.text)
        html_tree = html.fromstring(doc.summary())
        content_text = html_tree.text_content().strip()

        return {
            "title": doc.short_title(),
            "authors": None,
            "venue": None,
            "doi": None,
            "year": None,
            "keywords": None,
            "abstract": None,
            "content": content_text,
        }

    except Exception as e:
        print("⚠ Readability failed:", e)
        return {
            "title": None,
            "authors": None,
            "venue": None,
            "doi": None,
            "year": None,
            "keywords": None,
            "abstract": None,
            "content": None,
        }

# ---------------------------------------------------------
# MASTER CLEANER
# ---------------------------------------------------------
def clean_article(url: str) -> dict:
    """
    1. ACM DOI → CrossRef → PDF fallback → merge
    2. Non-ACM → readability fallback
    """
    low = (url or "").lower()

    # ---------- ACM ----------
    if "dl.acm.org/doi" in low:
        doi = extract_doi_from_url(url)
        print(f"🔍 ACM detected → DOI: {doi}")

        meta = fetch_crossref_metadata(doi)

        if meta:
            print("✔ CrossRef metadata loaded")

            # PDF fallback if CrossRef missing important fields
            missing = (
                not meta.get("authors")
                or not meta.get("year")
            )

            if missing:
                print("⚠ CrossRef incomplete → trying PDF fallback")
                pdf_meta = extract_pdf_metadata_from_doi(doi)

                if pdf_meta:
                    for k, v in pdf_meta.items():
                        if v and not meta.get(k):
                            meta[k] = v

            # Content is not provided by CrossRef → use readability
            if not meta.get("content"):
                print("ℹ Adding readability content")
                fallback = readability_fallback(url)
                if fallback.get("content"):
                    meta["content"] = fallback["content"]

            return meta

        print("⚠ CrossRef failed → using readability fallback")

    # ---------- NON-ACM ----------
    return readability_fallback(url)
