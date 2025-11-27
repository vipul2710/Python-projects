import os
import textwrap
import hashlib
from graphviz import Digraph

VIS_DIR = os.path.join("data", "visuals")
os.makedirs(VIS_DIR, exist_ok=True)


# ------------------------------------------------
# Utility: Shorten text to fit inside nodes
# ------------------------------------------------
def _shorten(text: str, width: int = 80) -> str:
    if not text:
        return ""
    text = " ".join(text.split())
    return textwrap.fill(text, width=width)


# ------------------------------------------------
# Extract key sections from extended summary
# ------------------------------------------------
def _extract_sections_from_extended(ext: str) -> dict:
    sections = {
        "Contribution": None,
        "Method": None,
        "Findings": None,
        "Implications": None
    }

    if not ext:
        return sections

    ext = ext.strip()

    def extract_between_markers(text, start_marker, end_markers=None):
        if start_marker not in text:
            return None
        parts = text.split(start_marker, 1)
        if len(parts) < 2:
            return None
        content = parts[1]

        if end_markers is None:
            end_markers = ["\n**", "\n##", "\n###"]

        min_pos = len(content)
        for marker in end_markers:
            pos = content.find(marker)
            if pos != -1 and pos < min_pos:
                min_pos = pos

        content = content[:min_pos].strip()
        content = content.strip("*").strip("#").strip(":\n -").strip()
        return content if content else None

    # Contribution
    for marker in [
        "**Key Contribution**", "**Key Contributions**", "**Main Contribution**",
        "**Overview**", "## Key Contribution", "## Key Contributions", "## Overview"
    ]:
        sections["Contribution"] = extract_between_markers(ext, marker)
        if sections["Contribution"]:
            break

    # Method
    for marker in [
        "**Method/Approach**", "**Approach**", "**Method**", "**Methodology**",
        "**Technical Approach**", "## Method/Approach", "## Method", "## Approach"
    ]:
        sections["Method"] = extract_between_markers(ext, marker)
        if sections["Method"]:
            break

    # Findings
    for marker in [
        "**Applications**", "**Key Findings**", "**Results**", "**Findings**",
        "**Main Results**", "**Outcomes**", "## Applications", "## Results", "## Findings"
    ]:
        sections["Findings"] = extract_between_markers(ext, marker)
        if sections["Findings"]:
            break

    # Implications
    for marker in [
        "**Limitations/Future Work**", "**Limitations and Future Work**",
        "**Limitations**", "**Future Work**", "**Implications**", "**Impact**",
        "## Limitations/Future Work", "## Limitations", "## Future Work"
    ]:
        sections["Implications"] = extract_between_markers(ext, marker)
        if sections["Implications"]:
            break

    # Shorten each text
    for k, v in sections.items():
        if v:
            v = " ".join(v.split())
            sections[k] = _shorten(v, width=180)

    return sections


# ------------------------------------------------
# Compute stable hash for filename
# ------------------------------------------------
def _compute_hash(row):
    h = row.get("hash")
    if h:
        return h
    seed = (row.get("doi") or row.get("title") or "paper")[:300]
    return hashlib.sha256(seed.encode()).hexdigest()[:16]


# ------------------------------------------------
# Generate Top–Down Flowchart (FIX)
# ------------------------------------------------
def generate_flowchart_png(title, brief, extended, outfile):

    sec = _extract_sections_from_extended(extended)

    g = Digraph(format="png")

    # ⭐ NEW FIXED TOP-DOWN SETTINGS ⭐
    g.attr(
        rankdir="TB",        # TOP → BOTTOM
        dpi="220",           # High DPI for readability
        nodesep="0.7",       # vertical spacing
        ranksep="0.9",       # horizontal spacing
        bgcolor="white",
        fontname="Helvetica"
    )

    g.attr('graph', splines="ortho", concentrate="true")

    # Node styling
    g.attr('node', fontsize="18", fontname="Helvetica", margin="0.3,0.2")
    g.attr('edge', fontsize="14", fontname="Helvetica", penwidth="2")

    # Title node
    title_text = _shorten(title, 60)
    g.node("t", title_text, shape="box", style="filled,rounded",
           fillcolor="#E8F4F8", fontsize="20")

    # Contribution / Context node
    context_text = brief or sec["Contribution"] or "No context extracted"
    context_wrapped = _shorten(context_text, 120)
    g.node("c", context_wrapped, shape="ellipse", style="filled",
           fillcolor="#FFF9E6")

    # Method node
    method_text = sec["Method"] or "No method extracted"
    method_wrapped = _shorten(method_text, 120)
    g.node("m", method_wrapped, shape="box", style="filled,rounded",
           fillcolor="#E8F8E8")

    # Findings node
    findings_text = sec["Findings"] or "No findings extracted"
    findings_wrapped = _shorten(findings_text, 120)
    g.node("f", findings_wrapped, shape="note", style="filled",
           fillcolor="#FFE6E6")

    # Implications node
    implications_text = sec["Implications"] or "No implications extracted"
    implications_wrapped = _shorten(implications_text, 120)
    g.node("i", implications_wrapped, shape="folder", style="filled",
           fillcolor="#F0E6FF")

    # Top-down edges
    g.edge("t", "c", label="")
    g.edge("c", "m", label="")
    g.edge("m", "f", label="")
    g.edge("f", "i", label="")

    # Output
    os.makedirs(os.path.dirname(outfile), exist_ok=True)
    if os.path.exists(outfile + ".png"):
        os.remove(outfile + ".png")

    g.render(filename=outfile, cleanup=True)
    return outfile + ".png"


# ------------------------------------------------
# Generate per-row
# ------------------------------------------------
def generate_visual_for_row(row):
    try:
        h = _compute_hash(row)
        filename = os.path.join(VIS_DIR, f"visual_{h}")
        return generate_flowchart_png(
            title=row.get("title", ""),
            brief=row.get("summary_brief", ""),
            extended=row.get("summary_extended", ""),
            outfile=filename
        )
    except Exception as e:
        print("⚠️ VISUAL GENERATION FAILED:", e)
        return None


# ------------------------------------------------
# Update DB row
# ------------------------------------------------
def update_visual_path_safely(table, hash_value, visual_path):
    try:
        # hash IS the primary key
        table.update(hash_value, {"visual_path": visual_path})
        print(f"✓ Updated visual for hash={hash_value}")
        return 1

    except Exception as e:
        print("❌ Update failed:", e)
        return 0


# ------------------------------------------------
# Generate ALL missing visuals
# ------------------------------------------------
def generate_all_visuals(limit=None):
    from src.normalize.db import Database
    db = Database()
    table = db.db["articles"]

    rows = [r for r in table.rows if r.get("summary_extended") and not r.get("visual_path")]
    rows.sort(key=lambda r: r.get("published_at") or "", reverse=True)

    if limit:
        rows = rows[:limit]

    print(f"Generating {len(rows)} visuals...")

    count = 0
    for row in rows:
        visual_path = generate_visual_for_row(row)
        if visual_path:
            count += update_visual_path_safely(table, row["hash"], visual_path)

    print("Done. Generated", count)


# ------------------------------------------------
# Regenerate ALL visuals
# ------------------------------------------------
def regenerate_all_visuals(limit=None):
    from src.normalize.db import Database
    db = Database()
    table = db.db["articles"]

    rows = [r for r in table.rows if r.get("summary_extended")]
    rows.sort(key=lambda r: r.get("published_at") or "", reverse=True)

    if limit:
        rows = rows[:limit]

    print(f"Regenerating {len(rows)} visuals...")

    count = 0
    for row in rows:
        if row.get("visual_path") and os.path.exists(row["visual_path"]):
            os.remove
        visual_path = generate_visual_for_row(row)
        if visual_path:
            count += update_visual_path_safely(table, row["hash"], visual_path)

    print("Done. Regenerated", count)
