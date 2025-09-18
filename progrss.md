# Agentic AI Digest — Progress & Plain-English Guide

**Last updated:** 2025-09-08

## 1) Project purpose (short)
Agentic AI Digest is a small pipeline that automatically pulls tech & industry updates, cleans and deduplicates them, summarizes them (brief + extended), and produces a weekly consulting-style PDF digest for personal use. The system is modular so we can swap models (GPT / Claude) and add features later (Notion export, search, UI).

---

## 2) Current snapshot (what we have right now)
- **Environment:** Python 3.11, Poetry, project `.venv`.  
- **Core libs installed:** feedparser, requests, readability-lxml, jinja2, weasyprint, pydantic, sqlite-utils, loguru, pyyaml.  
- **Files & modules created:**
  - `configs/sources.yaml` — curated RSS feeds per category.
  - `configs/prompts/brief.md` and `extended.md` — prompt templates for summarization.
  - `cli.py` — simple CLI skeleton that loads `sources.yaml`.
  - `src/ingest/rss_loader.py` — fetches feeds with feedparser.
  - `src/normalize/text_cleaner.py` — fetches article pages and extracts main text.
  - `src/normalize/deduper.py` — in-memory SHA256 dedup checker.
  - `src/normalize/db.py` — sqlite-utils based DB (stores articles).
  - `cli_ingest.py` — integration runner connecting ingestion → clean → dedup → DB.
  - `setup.md` — setup + reasoning docs (technical).
  - `progress.md` — this plain-language daily summary.

---

## 3) How the system works (plain language)
1. **Sources config:** We keep a human-editable `sources.yaml` listing feeds by category. This tells the system *where* to look.
2. **Ingestion:** The pipeline reads the feed URLs and downloads the feed entries (titles, short summaries, links).
3. **Normalization:** For each feed item we visit the linked page, and use Readability to extract the article’s main content (not menus or ads).
4. **Deduplication:** Each cleaned article is fingerprinted (SHA256). If the fingerprint already exists (in memory or DB), we skip it — so we don’t repeat the same article.
5. **Storage:** New, cleaned articles are saved into `data/cache/digest.db` (SQLite). This keeps history across runs and supports later summarization and search.
6. **(Next) Summarization & Render:** We will pull articles from DB, ask the LLM to create a short brief (2–3 bullets) and an extended note (why it matters + recommendations), then render a PDF via Jinja2 → WeasyPrint.

---

## 4) Why we picked the main tools (short)
- **feedparser:** easy RSS/Atom parsing.  
- **readability-lxml + lxml:** reliably extract main article text.  
- **sqlite-utils:** lightweight, zero-ops database for persisting articles.  
- **Poetry:** reproducible environment and dependency management.  
- **Jinja2 + WeasyPrint:** simple HTML → PDF pipeline for clean output.

---
**Day 5**
- Added Renderer module with Jinja2 templates (HTML digest working).
- Digest now shows date and clickable source links.
- CLI updated with subcommands: ingest, summarize, render.
- Ingestion now supports --limit flag for safe fetching.
- Confirmed DB deduplication (46 articles stored, no duplicates).

**Day 6**
  - Polished digest template:
  - Cover page with title + date
  - Styled category headers with dividers
  - Improved article spacing, fonts, and source link styling
  - Added footer with generated date
  - Verified clean HTML rendering via CLI

