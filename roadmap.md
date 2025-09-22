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
