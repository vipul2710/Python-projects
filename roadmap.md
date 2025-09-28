# Productization Roadmap — Agentic AI Digest

## Goal
Turn the MVP (ingest → summarize → render → PDF) into a usable product for researchers and professionals.

## Phase 1: Source Expansion
- Replace AI-heavy feeds with domain-specific feeds (e.g., research, business).
- Use Perplexity or curated RSS lists to identify better sources.
- Update `configs/sources.yaml`.

## Phase 2: Output Options
- Add Markdown export (`digest.md`) for easy sharing.
- Optional: Integrate with Notion to push digest weekly.

## Phase 3: Automation
- Add GitHub Action or cron job for weekly pipeline run.
- Automate full flow: ingest → summarize → render → export.

## Phase 4: Design & Polish
- Improve PDF design (logo, colors, consulting style).
- Optional: cover page images.

## Phase 5: Pilot & Feedback
- Deliver weekly digest for a researcher (pilot case).
- Collect feedback and iterate.

---
**Tracking**
- Branch: `productization`
- MVP remains stable in `master`.

## Phase 6: arXiv Integration (Complete ✅)
- Added arXiv ingestion via `arxiv` Python library.
- Integrated dedup + DB insertion.
- Summarization works category-specific (`Arxiv_AI_Gaming`).
- Renderer and CLI updated to filter by category.
- Successfully rendered arXiv-only digest in HTML/PDF/Markdown.

## Phase 7: Researcher-Focused Summaries (Complete ✅)
- Replaced consulting-style prompts with academic prompts.
- Brief: key contributions in 2–3 bullets.
- Extended: structured summary (contribution, method, applications, limitations).
- Verified new summaries generated for arXiv papers.
- Note: `master` branch keeps consulting mode, `productization` branch now targets researchers.

## Phase 8: CLI Polish & DB Cleanup (Complete ✅)
- Added `--refresh` flag in `summarize` to reset and regenerate summaries in one step.
- Configured CLI to default to researcher-style outputs.
- Introduced DB cleanup utility (`cli.py clean`):
  - `--days N`: delete articles older than N days.
  - `--all`: reset DB completely.
  - Uses `retention_days` from `configs/config.yaml` if no flag is given (default: 180 days).
- Ensures DB stays lean and manageable over time.

