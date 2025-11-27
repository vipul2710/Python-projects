# src/normalize/acm_parser.py
import requests
from lxml import html

import cloudscraper
from lxml import html

scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'mobile': False
    }
)


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/121.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Referer": "https://dl.acm.org/",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Upgrade-Insecure-Requests": "1",
}

def extract_acm_metadata(url: str) -> dict:
    """Extract metadata from ACM Digital Library article page."""
    try:
        resp = scraper.get(url, timeout=12)
        resp.raise_for_status()
    except Exception as e:
        print(f"⚠️ ACM fetch failed: {e}")
        return None

    tree = html.fromstring(resp.text)

    # Title
    title = tree.xpath('//h1[@class="citation__title"]/text()')
    title = title[0].strip() if title else None

    # Authors
    authors = tree.xpath('//span[@class="loa__author-name"]/text()')
    authors = "; ".join(a.strip() for a in authors) if authors else None

    # DOI
    doi = tree.xpath('//a[contains(@class,"issue-item__doi")]/text()')
    doi = doi[0].replace("https://doi.org/", "").strip() if doi else None

    # Year
    year = tree.xpath('//span[contains(@class,"CitationCoverDate")]/text()')
    year = year[0][-4:] if year else None

    # Venue
    venue = tree.xpath('//span[@class="epub-section__title"]/text()')
    venue = venue[0].strip() if venue else None

    # Abstract
    abstract = tree.xpath('//div[contains(@class,"abstractSection")]//p/text()')
    abstract = " ".join(a.strip() for a in abstract) if abstract else None

    # Keywords
    keywords = tree.xpath('//div[contains(@class,"keywords-section")]//span/text()')
    keywords = ", ".join(k.strip() for k in keywords) if keywords else None

    # Main body
    paras = tree.xpath('//div[contains(@class,"article__body")]//p/text()')
    content = "\n".join(p.strip() for p in paras) if paras else abstract

    return {
        "title": title,
        "authors": authors,
        "venue": venue,
        "doi": doi,
        "year": year,
        "keywords": keywords,
        "abstract": abstract,
        "content": content,
    }
