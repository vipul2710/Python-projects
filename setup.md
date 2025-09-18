# 📘 Agentic AI Digest — Setup Documentation (Environment & Dependencies)

## 1. Python 3.11 Installation
- **What we did:** Installed Python 3.11 from python.org.  
- **Why:**  
  - Needed ≥3.11 for modern libraries (Pydantic v2, WeasyPrint).  
  - Faster + longer support than 3.9.  
- **Where used:** All project code runs under Python 3.11.

---

## 2. Virtual Environment (`.venv`)
- **What we did:** Created `.venv` in project folder with `python -m venv .venv`.  
- **Why:** Keeps dependencies isolated + reproducible.  
- **Where used:** All project libraries installed here.

---

## 3. Poetry Installation
- **What we did:** Installed Poetry (v2.1.4) globally.  
- **Why:** Dependency manager + project metadata handler.  
- **Where used:** Adds dependencies, creates `pyproject.toml` and `poetry.lock`.

---

## 4. Project Initialization
- **What we did:** Ran `poetry init` to generate `pyproject.toml`.  
- **Why:** Central config for dependencies + metadata.  
- **Where used:** Anyone can clone and run `poetry install`.

---

## 5. Core Libraries
Installed with:  
```bash
poetry add feedparser requests readability-lxml jinja2 weasyprint pydantic sqlite-utils loguru
````

| Library              | Why Installed     | Where We’ll Use It            |
| -------------------- | ----------------- | ----------------------------- |
| **feedparser**       | Parse RSS feeds   | Ingest articles/blogs         |
| **requests**         | HTTP requests     | Fetch web pages/APIs          |
| **readability-lxml** | Extract main text | Clean article content         |
| **jinja2**           | HTML templating   | Build digest reports          |
| **weasyprint**       | HTML→PDF          | Generate consulting-brief PDF |
| **pydantic**         | Data validation   | Configs + summary schema      |
| **sqlite-utils**     | SQLite helper     | Store items/summaries         |
| **loguru**           | Logging           | Debug + pipeline monitoring   |

---

## 6. Verification

* Activated Poetry venv
* Import test:

  ```bash
  python -c "import feedparser, requests, jinja2, pydantic; print('All good!')"
  ```
* ✅ Result: `All good!`

---

# 📌 Current Status

* Python 3.11 ✅
* Poetry ✅
* Venv ✅
* Dependencies ✅
* Imports working ✅

---

# 🔜 Next Steps

1. Scaffold folder structure (`src/`, `configs/`, `data/`).
2. Add `sources.yaml` + prompt templates.
3. Write CLI skeleton.
4. Commit setup & push to Git.

```

---

---
## 06/09/2025
## 7. Configuring Sources (sources.yaml)

- **What we did:** Created `configs/sources.yaml` to store curated RSS/blog feeds by category.  
- **Why:** Keeps the pipeline flexible — we can add/remove feeds without touching code.  
- **Where used:** The ingestion module will read this file to know which sources to fetch.  

### Notes for future
- Current version has 2–3 high-quality feeds per category for testing.  
- After MVP, we’ll expand using external discovery (e.g. Perplexity suggestions) and add a `priority` field.

```

---

## 8. Prompt templates (configs/prompts)

- **What we did:** Created two prompt template files:
  - `configs/prompts/brief.md` — short 2–3 bullet brief.
  - `configs/prompts/extended.md` — longer context: "Why it matters" + "Recommendations".

- **Why:** Keeping prompts in files makes the summarization behavior configurable without changing code. We can tweak tone, length, or structure anytime.

- **Where used:** The summarizer module will load these templates and send them to the LLM (GPT or Claude) to produce consistent outputs.

### Notes / Tips
- The `brief.md` currently limits output to 420 characters — this is adjustable (e.g., 1000 chars) by editing the file.
- Keep prompt wording explicit (tone, max length, required sections) to reduce hallucinations and get repeatable summaries.


---

## 9. YAML Support (PyYAML)

- **What we did:** Installed `pyyaml` using Poetry.
- **Why:** Required to parse `.yaml` configuration files (e.g., `sources.yaml`) into Python objects.
- **Where used:** The CLI (`cli.py`) loads `configs/sources.yaml` with PyYAML so the pipeline knows which feeds to process.



---

## 10. Ingestion (src/ingest/rss_loader.py)

- **What we did:** Created the ingestion module `rss_loader.py` in `src/ingest/`.  
- **Why:** To fetch live articles from RSS/Atom feeds defined in `configs/sources.yaml`.  
- **Where used:** This module will be the first stage of the pipeline — pulling in raw content before normalization and summarization.

### How it works
1. Load categories + feed URLs from `sources.yaml` (using PyYAML).  
2. For each feed, parse entries using `feedparser`.  
3. Normalize entries into a consistent dict with:  
   - `title`  
   - `link`  
   - `published`  
   - `summary` (short preview)  
4. Return everything grouped by category.  

### Example Output
📂 AI_ML_Analytics (4 items)

Get Gemini’s help in Google Sheets... (https://blog.google/products/workspace/workspace-feature-drop-ai-sheets/
)

Veo 3 comes to Google Photos... (https://blog.google/products/photos/google-photos-create-tab-editing-tools/
)


### Notes
- Currently fetches only the first 2–3 items per feed (for testing).  
- Later we’ll add caching, deduplication, and database storage.


---

## 11. Normalization, Deduplication & Storage

### Normalization (`text_cleaner.py`)
- **What we did:** Added a module to fetch full article content using `requests + readability-lxml + lxml`.
- **Why:** RSS feeds often only include short summaries. We need the full text for meaningful summarization.
- **Where used:** Each feed entry’s link is passed to `clean_article()` to extract the main article body.

### Deduplication (`deduper.py`)
- **What we did:** Created a deduper that fingerprints each article’s text (SHA256 hash).
- **Why:** Prevents storing/summarizing the same article multiple times across feeds.
- **Where used:** Before inserting into DB, every article is checked with `is_duplicate()`.

### Storage (`db.py`)
- **What we did:** Added SQLite storage using `sqlite-utils`.
- **Why:** Keeps articles persistent across runs, supports deduplication checks, and provides a base for search.
- **Where used:** `Database.insert_article()` inserts only new items into the `articles` table.

### Integration (`cli_ingest.py`)
- **What we did:** Connected ingestion → normalization → deduplication → storage in a single script.
- **Why:** This creates an end-to-end pipeline that:
  1. Loads sources from `sources.yaml`
  2. Fetches articles via feedparser
  3. Cleans article text with `text_cleaner`
  4. Deduplicates articles with `deduper`
  5. Inserts new articles into SQLite via `db.py`

### Example Run
🚀 Running ingestion pipeline...

📂 AI_ML_Analytics (4 items)
✅ Inserted: Welcome EmbeddingGemma, Google's new efficient embedding model
❌ Duplicate skipped: Welcome EmbeddingGemma, Google's new efficient embedding model

### PDF Export Setup (Windows)

- We use WeasyPrint for PDF generation. On Windows this requires GTK runtime.
- Download the latest GTK runtime `.exe` installer from:
  https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
- Install with default options (adds GTK to PATH).
- Restart VS Code / terminal.
- Generate PDF digest:
  ```bash
  poetry run python cli.py render --limit 5 --format pdf

Output is saved as output.pdf in project folder.

Notes:

Some warnings may appear on Windows but PDF still works.

HTML export (--format html) is available as fallback (no GTK needed).


---

## ✅ Final `progress.md` recap
Append to the bottom:  

```markdown
### MVP Recap (Days 1–7)
- Project setup with Python 3.11 + Poetry.
- Feed ingestion → DB (dedup, normalization, encoding fix).
- Summarizer with OpenAI provider (brief + extended consulting-style prompts).
- Renderer with Jinja2 templates for HTML output.
- Template polished: cover page, categories, spacing, footer.
- CLI commands: ingest, summarize, render (with --limit and --format).
- PDF export enabled via WeasyPrint + GTK runtime.
- End-to-end MVP pipeline: ingest → summarize → render → PDF working.