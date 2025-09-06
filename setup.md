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
