from __future__ import annotations

import html
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "journal.md"
TARGET = ROOT / "index.html"


def slugify(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[-\s]+", "-", text).strip("-")
    return text or "section"


def inline(text: str) -> str:
    placeholders: list[str] = []

    def stash_code(match: re.Match[str]) -> str:
        placeholders.append(f"<code>{html.escape(match.group(1))}</code>")
        return f"@@CODE{len(placeholders) - 1}@@"

    text = re.sub(r"`([^`]+)`", stash_code, html.escape(text))
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    for idx, value in enumerate(placeholders):
        text = text.replace(f"@@CODE{idx}@@", value)
    return text


def render_table(lines: list[str]) -> str:
    rows = [[cell.strip() for cell in line.strip().strip("|").split("|")] for line in lines]
    if not rows:
        return ""
    head = rows[0]
    body = rows[2:] if len(rows) > 1 and set(rows[1][0].replace(" ", "")) <= {"-", ":"} else rows[1:]
    if [cell.lower() for cell in head[:3]] == ["past", "present", "future"] and body:
        row = body[0]
        while len(row) < 3:
            row.append("")
        return (
            "<div class=\"knowledge-link\" aria-label=\"Past present future knowledge link\">"
            "<article><span>Past</span><p>" + inline(row[0]) + "</p></article>"
            "<div class=\"knowledge-arrow\">-></div>"
            "<article><span>Present</span><p>" + inline(row[1]) + "</p></article>"
            "<div class=\"knowledge-arrow\">-></div>"
            "<article><span>Future</span><p>" + inline(row[2]) + "</p></article>"
            "</div>"
        )
    out = ["<div class=\"table-wrap\"><table>"]
    out.append("<thead><tr>" + "".join(f"<th>{inline(cell)}</th>" for cell in head) + "</tr></thead>")
    if body:
        out.append("<tbody>")
        for row in body:
            out.append("<tr>" + "".join(f"<td>{inline(cell)}</td>" for cell in row) + "</tr>")
        out.append("</tbody>")
    out.append("</table></div>")
    return "\n".join(out)


def add_visual(title: str) -> str:
    lower = title.lower()
    if "control systems are the bridge" in lower:
        return """
<div class="visual-card feedback-visual" aria-label="Feedback loop diagram">
  <div class="node hot">Goal</div><div class="arrow"></div>
  <div class="node">Controller</div><div class="arrow"></div>
  <div class="node yellow">Action</div><div class="arrow"></div>
  <div class="node">Machine</div><div class="arrow"></div>
  <div class="node white">Sensor</div><div class="return-line">feedback</div>
</div>
"""
    if "what is computation" in lower:
        return """
<div class="visual-card flow-visual" aria-label="Input transform output diagram">
  <div class="chip">Input</div>
  <div class="pulse-line"></div>
  <div class="chip red">Transform</div>
  <div class="pulse-line"></div>
  <div class="chip yellow">Output</div>
</div>
"""
    if "how computers think" in lower:
        return """
<div class="visual-card stack-visual" aria-label="Computing abstraction stack">
  <span>Your code</span><span>Interpreter</span><span>Operating system</span><span>Machine code</span><span>Signals</span>
</div>
"""
    if "ai-native programming logic map" in lower:
        return """
<div class="visual-card agent-visual" aria-label="AI agent loop diagram">
  <div>Prompt</div><div>Plan</div><div>Tool</div><div>Observe</div><div>Revise</div>
</div>
"""
    if "variables" in lower:
        return """
<div class="visual-card flow-visual" aria-label="Variable reference diagram">
  <div class="chip">Name</div><div class="pulse-line"></div><div class="chip yellow">Value</div><div class="pulse-line"></div><div class="chip red">State</div>
</div>
"""
    if "data types" in lower:
        return """
<div class="visual-card agent-visual" aria-label="Data type shapes">
  <div>Text</div><div>Number</div><div>Boolean</div><div>None</div><div>Collection</div>
</div>
"""
    if "control flow" in lower:
        return """
<div class="visual-card flow-visual" aria-label="Control flow diagram">
  <div class="chip">Condition</div><div class="pulse-line"></div><div class="chip red">Branch</div><div class="pulse-line"></div><div class="chip yellow">Loop</div>
</div>
"""
    if "functions" in lower:
        return """
<div class="visual-card flow-visual" aria-label="Function diagram">
  <div class="chip">Input</div><div class="pulse-line"></div><div class="chip red">Named Process</div><div class="pulse-line"></div><div class="chip yellow">Return</div>
</div>
"""
    if "data structures" in lower:
        return """
<div class="visual-card agent-visual" aria-label="Data structure choices">
  <div>List: order</div><div>Dict: lookup</div><div>Set: unique</div><div>Tuple: fixed</div>
</div>
"""
    if "error handling" in lower or "debugging" in lower:
        return """
<div class="visual-card feedback-visual" aria-label="Debugging feedback loop">
  <div class="node hot">Assumption</div><div class="arrow"></div><div class="node">Run</div><div class="arrow"></div><div class="node yellow">Error</div><div class="arrow"></div><div class="node white">Correction</div>
</div>
"""
    if "modules" in lower:
        return """
<div class="visual-card stack-visual" aria-label="Module stack">
  <span>Function</span><span>Module file</span><span>Package</span><span>Project</span><span>Library</span>
</div>
"""
    if "cli" in lower or "command" in lower:
        return """
<div class="visual-card flow-visual" aria-label="CLI IO diagram">
  <div class="chip">Args</div><div class="pulse-line"></div><div class="chip red">Program</div><div class="pulse-line"></div><div class="chip yellow">stdout / file</div>
</div>
"""
    if "files" in lower:
        return """
<div class="visual-card flow-visual" aria-label="Persistent state diagram">
  <div class="chip">Memory</div><div class="pulse-line"></div><div class="chip yellow">File</div><div class="pulse-line"></div><div class="chip red">Reload</div>
</div>
"""
    if "api service" in lower or "fastapi" in lower:
        return """
<div class="visual-card flow-visual" aria-label="API request response diagram">
  <div class="chip">Request</div><div class="pulse-line"></div><div class="chip red">Handler</div><div class="pulse-line"></div><div class="chip yellow">Response</div>
</div>
"""
    if "pipeline" in lower:
        return """
<div class="visual-card flow-visual" aria-label="Data pipeline diagram">
  <div class="chip">Extract</div><div class="pulse-line"></div><div class="chip red">Transform</div><div class="pulse-line"></div><div class="chip yellow">Load</div>
</div>
"""
    if "threads" in lower or "cores" in lower or "accelerators" in lower or "cuda" in lower or "mlx" in lower or "mojo" in lower:
        return """
<div class="visual-card feedback-visual" aria-label="Hardware execution flow">
  <div class="node hot">Code</div><div class="arrow"></div>
  <div class="node">Runtime</div><div class="arrow"></div>
  <div class="node yellow">Thread</div><div class="arrow"></div>
  <div class="node">Core / GPU</div><div class="arrow"></div>
  <div class="node white">Memory / I/O</div><div class="return-line">bottleneck</div>
</div>
"""
    if "snowflake" in lower or "warehouse" in lower or "database" in lower or "schema" in lower:
        return """
<div class="visual-card stack-visual" aria-label="Snowflake compute and namespace diagram">
  <span>Warehouse: compute lane</span><span>Database: data domain</span><span>Schema: namespace</span><span>Object: table / view</span><span>AI: trusted context</span>
</div>
"""
    if "async" in lower:
        return """
<div class="visual-card agent-visual" aria-label="Async concurrency diagram">
  <div>Start A</div><div>Start B</div><div>Wait</div><div>Resume</div><div>Gather</div>
</div>
"""
    if "cooperative runtimes" in lower or "scheduler" in lower:
        return """
<div class="visual-card feedback-visual" aria-label="Cooperative runtime scheduler diagram">
  <div class="node hot">Task</div><div class="arrow"></div>
  <div class="node">Scheduler</div><div class="arrow"></div>
  <div class="node yellow">Yield / Offload</div><div class="arrow"></div>
  <div class="node white">Responsive System</div>
</div>
"""
    if "rust" in lower:
        return """
<div class="visual-card flow-visual" aria-label="Rust ownership diagram">
  <div class="chip">Owner</div><div class="pulse-line"></div><div class="chip red">Move / Borrow</div><div class="pulse-line"></div><div class="chip yellow">Safety</div>
</div>
"""
    if "java" in lower:
        return """
<div class="visual-card stack-visual" aria-label="Java structure diagram">
  <span>Type</span><span>Class</span><span>Interface</span><span>Package</span><span>Team Contract</span>
</div>
"""
    if "go" in lower:
        return """
<div class="visual-card flow-visual" aria-label="Go concurrency diagram">
  <div class="chip">go task</div><div class="pulse-line"></div><div class="chip red">channel</div><div class="pulse-line"></div><div class="chip yellow">wait group</div>
</div>
"""
    if "clean code" in lower:
        return """
<div class="visual-card stack-visual" aria-label="Clean code communication stack">
  <span>Honest names</span><span>Small functions</span><span>Clear errors</span><span>Tests</span><span>Future reader</span>
</div>
"""
    if "system design" in lower:
        return """
<div class="visual-card stack-visual" aria-label="System design layers">
  <span>Client</span><span>API</span><span>Business logic</span><span>Data</span><span>Observability</span>
</div>
"""
    return ""


def render_markdown(md: str) -> tuple[str, list[dict[str, str]]]:
    lines = md.splitlines()
    used_slugs: dict[str, int] = {}
    toc: list[dict[str, str]] = []
    out: list[str] = []
    section_open = False
    i = 0

    def unique_slug(title: str) -> str:
        base = slugify(title)
        count = used_slugs.get(base, 0)
        used_slugs[base] = count + 1
        return base if count == 0 else f"{base}-{count + 1}"

    def close_section() -> None:
        nonlocal section_open
        if section_open:
            out.append("</div></section>")
            section_open = False

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if stripped.startswith("```"):
            lang = stripped.strip("`").strip() or "text"
            code: list[str] = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            i += 1
            out.append(
                f"<figure class=\"code-card\"><figcaption>{html.escape(lang)}</figcaption>"
                f"<button class=\"copy-code\" type=\"button\">Copy</button>"
                f"<pre><code>{html.escape(chr(10).join(code))}</code></pre></figure>"
            )
            continue

        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading:
            level = len(heading.group(1))
            title_raw = heading.group(2).strip()
            title_html = inline(title_raw)
            anchor = unique_slug(title_raw)
            if level <= 2:
                close_section()
                section_open = True
                section_class = "entry-section hero-section" if level == 1 else "entry-section"
                out.append(f"<section id=\"{anchor}\" class=\"{section_class}\" data-title=\"{html.escape(title_raw.lower())}\">")
                out.append("<button class=\"section-toggle\" type=\"button\" aria-label=\"Collapse section\">Collapse</button>")
                out.append("<div class=\"entry-inner\">")
                toc.append({"level": str(level), "title": re.sub(r"<[^>]+>", "", title_raw), "id": anchor})
            else:
                toc.append({"level": str(level), "title": re.sub(r"<[^>]+>", "", title_raw), "id": anchor})
            out.append(f"<h{level} id=\"{anchor}-heading\"><a href=\"#{anchor}\">{title_html}</a></h{level}>")
            out.append(add_visual(title_raw))
            i += 1
            continue

        if stripped in {"***", "---", "___"}:
            out.append("<hr>")
            i += 1
            continue

        if stripped.startswith(">"):
            quote: list[str] = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip().lstrip(">").strip())
                i += 1
            out.append("<blockquote>" + "<br>".join(inline(q) for q in quote) + "</blockquote>")
            continue

        if "|" in stripped and i + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$", lines[i + 1]):
            table: list[str] = []
            while i < len(lines) and "|" in lines[i].strip() and lines[i].strip():
                table.append(lines[i])
                i += 1
            out.append(render_table(table))
            continue

        if re.match(r"^\s*[-*]\s+", line):
            items: list[str] = []
            while i < len(lines) and re.match(r"^\s*[-*]\s+", lines[i]):
                items.append(re.sub(r"^\s*[-*]\s+", "", lines[i]).strip())
                i += 1
            out.append("<ul>" + "".join(f"<li>{inline(item)}</li>" for item in items) + "</ul>")
            continue

        if re.match(r"^\s*\d+\.\s+", line):
            items = []
            while i < len(lines) and re.match(r"^\s*\d+\.\s+", lines[i]):
                items.append(re.sub(r"^\s*\d+\.\s+", "", lines[i]).strip())
                i += 1
            out.append("<ol>" + "".join(f"<li>{inline(item)}</li>" for item in items) + "</ol>")
            continue

        para: list[str] = []
        while i < len(lines):
            candidate = lines[i]
            if not candidate.strip():
                break
            if re.match(r"^(#{1,6})\s+", candidate) or candidate.strip().startswith(("```", ">", "***", "---")):
                break
            if re.match(r"^\s*[-*]\s+", candidate) or re.match(r"^\s*\d+\.\s+", candidate):
                break
            if "|" in candidate and i + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-{3,}:?", lines[i + 1]):
                break
            para.append(candidate.strip())
            i += 1
        if para:
            out.append("<p>" + "<br>".join(inline(p) for p in para) + "</p>")
        else:
            i += 1

    close_section()
    return "\n".join(out), toc


def build_html(rendered: str, toc: list[dict[str, str]], raw_md: str, version: str) -> str:
    toc_json = json.dumps(toc)
    raw_json = json.dumps(raw_md).replace("</", "<\\/")
    version_json = json.dumps(version)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Thinking in Code — Programming Journal</title>
  <style>
    :root {{
      --bg: #060606;
      --panel: #101010;
      --panel-2: #171717;
      --text: #f5f2e8;
      --muted: #b8b4aa;
      --line: #2c2c2c;
      --red: #ff2d2d;
      --yellow: #ffd21f;
      --white: #ffffff;
      --shadow: 0 24px 80px rgba(0,0,0,.45);
      --radius: 8px;
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      background:
        radial-gradient(circle at 12% 0%, rgba(255,45,45,.16), transparent 30%),
        linear-gradient(135deg, rgba(255,210,31,.08), transparent 28%),
        var(--bg);
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.65;
    }}
    body.light {{
      --bg: #faf7ed;
      --panel: #fffdf6;
      --panel-2: #f2eee2;
      --text: #111;
      --muted: #4b463c;
      --line: #ded6c5;
      --shadow: 0 24px 80px rgba(40,28,10,.14);
    }}
    .progress {{ position: fixed; z-index: 50; top: 0; left: 0; height: 4px; width: 0; background: linear-gradient(90deg, var(--red), var(--yellow)); }}
    .layout {{ display: grid; grid-template-columns: 320px minmax(0, 1fr); min-height: 100vh; }}
    aside {{
      position: sticky; top: 0; height: 100vh; overflow: auto;
      border-right: 1px solid var(--line); background: rgba(10,10,10,.88);
      backdrop-filter: blur(18px); padding: 22px;
    }}
    body.light aside {{ background: rgba(255,253,246,.9); }}
    .brand {{ display: grid; gap: 8px; margin-bottom: 18px; }}
    .brand strong {{ font-size: 1.02rem; line-height: 1.2; }}
    .brand span {{ color: var(--muted); font-size: .86rem; }}
    .mobile-menu-toggle {{ display: none; }}
    .controls {{ display: grid; gap: 10px; margin: 20px 0; }}
    input[type="search"] {{
      width: 100%; border: 1px solid var(--line); border-radius: var(--radius);
      background: var(--panel); color: var(--text); padding: 11px 12px; outline: none;
    }}
    input[type="search"]:focus {{ border-color: var(--yellow); box-shadow: 0 0 0 3px rgba(255,210,31,.15); }}
    .button-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }}
    button, .source-link {{
      border: 1px solid var(--line); border-radius: var(--radius); background: var(--panel-2);
      color: var(--text); padding: 9px 10px; cursor: pointer; font: inherit;
    }}
    button:hover, .source-link:hover {{ border-color: var(--yellow); color: var(--yellow); }}
    .score-panel {{
      margin: 18px 0; padding: 14px; border: 1px solid rgba(255,210,31,.38);
      border-radius: var(--radius); background: linear-gradient(135deg, rgba(255,210,31,.11), rgba(255,45,45,.08));
    }}
    .score-head {{ display: flex; justify-content: space-between; gap: 10px; align-items: baseline; margin-bottom: 10px; }}
    .score-head strong {{ font-size: .9rem; }}
    .score-head span {{ color: var(--yellow); font-weight: 900; font-size: 1.25rem; }}
    .score-meter {{ height: 8px; border-radius: 999px; background: var(--panel); border: 1px solid var(--line); overflow: hidden; }}
    .score-meter div {{ height: 100%; width: 0; background: linear-gradient(90deg, var(--red), var(--yellow)); transition: width .35s ease; }}
    .score-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 12px; }}
    .score-grid div {{ border: 1px solid var(--line); background: var(--panel); border-radius: 6px; padding: 8px; }}
    .score-grid b {{ display: block; color: var(--white); }}
    .score-grid span {{ color: var(--muted); font-size: .74rem; text-transform: uppercase; }}
    .score-note {{ color: var(--muted); font-size: .78rem; margin: 10px 0 0; line-height: 1.35; }}
    .reset-score {{ width: 100%; margin-top: 10px; font-size: .78rem; padding: 6px 8px; }}
    .release-meta {{ color: var(--muted); font-size: .72rem; margin-top: 8px; word-break: break-word; }}
    nav a {{
      display: block; color: var(--muted); text-decoration: none; padding: 7px 8px;
      border-left: 2px solid transparent; border-radius: 0 6px 6px 0; font-size: .91rem;
    }}
    nav a[data-level="1"] {{ color: var(--text); font-weight: 800; margin-top: 8px; }}
    nav a[data-level="2"] {{ padding-left: 14px; }}
    nav a[data-level="3"] {{ padding-left: 26px; font-size: .82rem; }}
    nav a.active {{ border-left-color: var(--red); background: rgba(255,45,45,.1); color: var(--white); }}
    main {{ min-width: 0; }}
    .hero {{
      min-height: 78vh; display: grid; align-items: end; padding: 72px clamp(24px, 6vw, 92px) 52px;
      border-bottom: 1px solid var(--line); position: relative; overflow: hidden;
      background:
        linear-gradient(180deg, rgba(6,6,6,.1), rgba(6,6,6,.72)),
        radial-gradient(circle at 74% 18%, rgba(255,210,31,.13), transparent 26%),
        radial-gradient(circle at 18% 12%, rgba(255,45,45,.2), transparent 31%);
    }}
    .hero::before {{
      content: ""; position: absolute; inset: 0; opacity: .32;
      background-image:
        linear-gradient(rgba(255,255,255,.05) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,.05) 1px, transparent 1px);
      background-size: 42px 42px; mask-image: linear-gradient(to bottom, black, transparent 78%);
    }}
    .hero-content {{ position: relative; max-width: 1040px; }}
    .kicker {{ color: var(--yellow); text-transform: uppercase; font-weight: 900; letter-spacing: .14em; font-size: .76rem; }}
    .hero h1 {{ margin: 14px 0 18px; font-size: clamp(3rem, 7.4vw, 6.35rem); line-height: .9; letter-spacing: 0; max-width: 980px; }}
    .hero p {{ color: var(--muted); color: color-mix(in srgb, var(--text) 78%, var(--muted)); font-size: clamp(1.05rem, 1.85vw, 1.42rem); max-width: 780px; line-height: 1.55; }}
    .signal-strip {{
      display: flex; gap: 10px; margin-top: 30px; flex-wrap: wrap; align-items: center;
      max-width: 820px;
    }}
    .signal-strip::before {{
      content: "Mental model";
      color: var(--muted); font-size: .72rem; font-weight: 900; text-transform: uppercase;
      letter-spacing: .12em; margin-right: 2px;
    }}
    .signal-strip span {{
      display: inline-flex; align-items: center; justify-content: center; min-height: 34px;
      border: 1px solid rgba(255,255,255,.16); padding: 6px 12px; border-radius: 999px;
      background: linear-gradient(180deg, rgba(255,255,255,.08), rgba(255,255,255,.02));
      box-shadow: inset 0 1px 0 rgba(255,255,255,.09), 0 10px 24px rgba(0,0,0,.18);
      color: var(--text); font-weight: 800; font-size: .86rem; line-height: 1;
    }}
    .signal-strip span:nth-child(1), .signal-strip span:nth-child(2) {{
      width: 34px; padding-inline: 0; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      color: var(--yellow); border-color: rgba(255,210,31,.34);
    }}
    .signal-strip span:last-child {{ border-color: rgba(255,45,45,.36); }}
    .journal {{ padding: 36px clamp(18px, 5vw, 84px) 96px; }}
    .entry-section {{
      position: relative; margin: 0 auto 28px; max-width: 980px; background: rgba(16,16,16,.82);
      border: 1px solid var(--line); border-radius: var(--radius); box-shadow: var(--shadow); overflow: hidden;
    }}
    body.light .entry-section {{ background: rgba(255,253,246,.92); }}
    .entry-inner {{ padding: clamp(22px, 4vw, 48px); }}
    .section-toggle {{ position: absolute; top: 14px; right: 14px; z-index: 2; font-size: .78rem; padding: 5px 8px; }}
    .entry-section.collapsed .entry-inner > *:not(h1):not(h2) {{ display: none; }}
    .entry-section.hidden {{ display: none; }}
    #thinking-in-code-from-zero-to-ai-native-systems-builder {{
      max-width: 980px; background: linear-gradient(135deg, rgba(255,210,31,.08), rgba(255,45,45,.06));
    }}
    #thinking-in-code-from-zero-to-ai-native-systems-builder .entry-inner {{ padding: clamp(20px, 3vw, 34px); }}
    #thinking-in-code-from-zero-to-ai-native-systems-builder h1 {{
      font-size: clamp(1.45rem, 2.7vw, 2.35rem); margin: 0 0 10px; max-width: 760px;
    }}
    #thinking-in-code-from-zero-to-ai-native-systems-builder h3 {{
      margin: 0 0 18px; font-size: clamp(.98rem, 1.7vw, 1.2rem); color: var(--yellow);
    }}
    #thinking-in-code-from-zero-to-ai-native-systems-builder p {{
      max-width: 880px; margin: 8px 0; color: var(--muted); font-size: .98rem;
    }}
    h1, h2, h3, h4 {{ line-height: 1.08; letter-spacing: 0; }}
    h1 a, h2 a, h3 a, h4 a {{ color: inherit; text-decoration: none; }}
    h1 {{ font-size: clamp(2.1rem, 5vw, 4.8rem); margin: 0 0 24px; }}
    h2 {{ font-size: clamp(1.6rem, 3.4vw, 3rem); margin: 0 0 24px; }}
    h3 {{ margin-top: 34px; color: var(--yellow); font-size: 1.23rem; }}
    h3[id^="dream-lab"] {{
      display: inline-flex; align-items: center; margin: 10px 0 12px; padding: 6px 10px;
      border-radius: 999px; background: var(--yellow); color: #000; font-size: .82rem;
      text-transform: uppercase; letter-spacing: .08em;
    }}
    h3[id^="dream-lab"] + p,
    h3[id^="dream-lab"] + p + p,
    h3[id^="dream-lab"] + p + p + p,
    h3[id^="dream-lab"] + p + p + p + p {{
      max-width: none; margin: 8px 0; padding: 10px 12px 10px 14px;
      border-left: 3px solid var(--red); background: rgba(255,255,255,.035);
      border-radius: 0 var(--radius) var(--radius) 0; line-height: 1.45;
    }}
    body.light h3[id^="dream-lab"] + p,
    body.light h3[id^="dream-lab"] + p + p,
    body.light h3[id^="dream-lab"] + p + p + p,
    body.light h3[id^="dream-lab"] + p + p + p + p {{ background: rgba(255,210,31,.12); }}
    h4 {{ color: var(--white); }}
    p {{ max-width: 76ch; margin: 14px 0; }}
    strong {{ color: var(--white); }}
    body.light strong {{ color: #000; }}
    em {{ color: var(--yellow); }}
    code {{ background: rgba(255,210,31,.13); color: var(--yellow); padding: .12em .34em; border-radius: 5px; }}
    blockquote {{ margin: 24px 0; border-left: 4px solid var(--red); padding: 10px 18px; background: rgba(255,45,45,.08); font-size: 1.06rem; }}
    hr {{ border: 0; height: 1px; background: var(--line); margin: 34px 0; }}
    ul, ol {{ padding-left: 1.3rem; }}
    li {{ margin: 7px 0; }}
    .table-wrap {{ overflow: auto; margin: 22px 0; border: 1px solid var(--line); border-radius: var(--radius); }}
    table {{ width: 100%; border-collapse: collapse; min-width: 620px; background: var(--panel); }}
    th, td {{ border-bottom: 1px solid var(--line); padding: 12px 14px; vertical-align: top; }}
    th {{ text-align: left; color: var(--yellow); background: rgba(255,210,31,.08); }}
    .code-card {{ position: relative; margin: 24px 0; border: 1px solid var(--line); border-radius: var(--radius); background: #050505; overflow: hidden; }}
    .code-card figcaption {{ padding: 8px 12px; color: var(--yellow); border-bottom: 1px solid var(--line); font-size: .78rem; text-transform: uppercase; }}
    .copy-code {{ position: absolute; top: 7px; right: 8px; padding: 4px 8px; font-size: .75rem; }}
    pre {{ margin: 0; overflow: auto; padding: 18px; line-height: 1.5; }}
    pre code {{ background: transparent; color: #f7f7f7; padding: 0; }}
    .visual-card {{ border: 1px solid var(--line); border-radius: var(--radius); background: linear-gradient(135deg, rgba(255,45,45,.12), rgba(255,210,31,.08)); margin: 24px 0; padding: 18px; }}
    .flow-visual, .feedback-visual, .agent-visual {{ display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }}
    .chip, .node, .agent-visual div {{ border: 1px solid var(--line); background: var(--panel); padding: 12px 14px; border-radius: var(--radius); font-weight: 800; }}
    .chip.red, .node.hot {{ border-color: var(--red); color: var(--red); }}
    .chip.yellow, .node.yellow {{ border-color: var(--yellow); color: var(--yellow); }}
    .node.white {{ border-color: var(--white); }}
    .pulse-line, .arrow {{ width: 54px; height: 2px; background: linear-gradient(90deg, var(--red), var(--yellow)); animation: pulse 1.6s infinite; }}
    .return-line {{ color: var(--yellow); font-size: .8rem; text-transform: uppercase; }}
    .stack-visual {{ display: grid; gap: 8px; }}
    .stack-visual span {{ display: block; border: 1px solid var(--line); padding: 10px 12px; background: var(--panel); }}
    .knowledge-link {{
      display: grid; grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr) auto minmax(0, 1fr);
      gap: 12px; align-items: stretch; margin: 24px 0; padding: 14px;
      border: 1px solid rgba(255,210,31,.42); border-radius: var(--radius);
      background: linear-gradient(135deg, rgba(255,210,31,.13), rgba(255,45,45,.1));
    }}
    .knowledge-link article {{
      border: 1px solid var(--line); background: var(--panel); border-radius: var(--radius);
      padding: 14px; min-height: 118px;
    }}
    .knowledge-link span {{
      display: inline-flex; margin-bottom: 8px; color: #000; background: var(--yellow);
      border-radius: 999px; padding: 3px 8px; font-weight: 900; font-size: .75rem; text-transform: uppercase;
    }}
    .knowledge-link p {{ margin: 0; color: var(--text); font-size: .95rem; }}
    .knowledge-arrow {{ align-self: center; color: var(--red); font-weight: 900; animation: pulse 1.8s infinite; }}
    .learning-check {{
      margin: 34px 0 0; border: 1px solid rgba(255,45,45,.42); border-radius: var(--radius);
      background: linear-gradient(135deg, rgba(255,45,45,.12), rgba(255,210,31,.08)); overflow: hidden;
    }}
    .learning-check summary {{
      cursor: pointer; padding: 14px 16px; list-style: none; display: flex; align-items: center;
      justify-content: space-between; gap: 12px; font-weight: 900;
    }}
    .learning-check summary::-webkit-details-marker {{ display: none; }}
    .learning-check summary span {{ color: var(--yellow); font-size: .8rem; text-transform: uppercase; }}
    .check-body {{ padding: 0 16px 16px; display: grid; gap: 16px; }}
    .check-stage {{ border: 1px solid var(--line); background: var(--panel); border-radius: var(--radius); padding: 14px; }}
    .check-stage h4 {{ margin: 0 0 8px; color: var(--yellow); }}
    .mcq-options {{ display: grid; gap: 8px; margin-top: 10px; }}
    .mcq-options button {{ text-align: left; }}
    .mcq-options button.correct-choice {{ border-color: #28d17c; color: #28d17c; }}
    .mcq-options button.wrong-choice {{ border-color: var(--red); color: var(--red); }}
    .check-feedback {{ min-height: 1.4em; color: var(--muted); margin: 8px 0 0; }}
    .recall-box {{
      width: 100%; min-height: 92px; resize: vertical; border: 1px solid var(--line);
      background: #050505; color: #f7f7f7; border-radius: var(--radius); padding: 10px; font: inherit;
    }}
    body.light .recall-box {{ background: #fff; color: #111; }}
    .confidence-row {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }}
    .confidence-row button.active {{ background: var(--yellow); color: #000; border-color: var(--yellow); }}
    .hard-prompt {{ color: var(--muted); }}
    .learning-check.done {{ border-color: rgba(255,210,31,.7); }}
    @keyframes pulse {{ 0%, 100% {{ opacity: .35; transform: scaleX(.82); }} 50% {{ opacity: 1; transform: scaleX(1); }} }}
    .compact .entry-inner {{ padding: 22px; }}
    .compact p, .compact li {{ line-height: 1.45; }}
    mark {{ background: var(--yellow); color: #000; padding: 0 .15em; }}
    dialog {{ max-width: min(920px, 92vw); max-height: 78vh; border: 1px solid var(--line); background: var(--panel); color: var(--text); border-radius: var(--radius); box-shadow: var(--shadow); }}
    dialog textarea {{ width: 100%; height: 55vh; background: #050505; color: #f7f7f7; border: 1px solid var(--line); border-radius: var(--radius); padding: 12px; }}
    @media (max-width: 900px) {{
      .layout {{ grid-template-columns: 1fr; }}
      aside {{
        position: sticky; top: 0; z-index: 60; height: auto; max-height: 72px; overflow: hidden;
        border-right: 0; border-bottom: 1px solid var(--line); padding: 12px 14px;
      }}
      aside.mobile-open {{ max-height: 82vh; overflow: auto; box-shadow: var(--shadow); }}
      .brand {{
        grid-template-columns: minmax(0, 1fr) auto; align-items: center; gap: 10px; margin-bottom: 0;
      }}
      .brand span {{ display: none; }}
      .mobile-menu-toggle {{ display: inline-flex; align-items: center; justify-content: center; min-width: 78px; }}
      aside:not(.mobile-open) .controls,
      aside:not(.mobile-open) .score-panel,
      aside:not(.mobile-open) nav {{ display: none; }}
      aside.mobile-open .controls {{ margin-top: 14px; }}
      .hero {{ min-height: 64vh; padding-top: 54px; }}
      .hero h1 {{ font-size: clamp(3rem, 16vw, 5rem); }}
      .hero p {{ font-size: 1rem; }}
      .signal-strip {{ gap: 8px; margin-top: 22px; }}
      .signal-strip::before {{ flex-basis: 100%; }}
      .journal {{ padding-top: 18px; }}
      .section-toggle {{ position: static; margin: 14px 0 0 14px; }}
      .knowledge-link {{ grid-template-columns: 1fr; }}
      .knowledge-arrow {{ text-align: center; transform: rotate(90deg); }}
    }}
    @media print {{
      body {{ background: #fff; color: #000; }}
      .layout {{ display: block; }}
      aside, .progress, .hero, .section-toggle, .learning-check, dialog {{ display: none !important; }}
      .journal {{ padding: 0; }}
      .entry-section {{ box-shadow: none; border: 0; break-inside: avoid; background: #fff; color: #000; }}
      .entry-inner {{ padding: 0 0 24px; }}
      h1, h2, h3, h4, strong {{ color: #000; }}
      a {{ color: #000; text-decoration: none; }}
      .code-card, pre {{ background: #f4f4f4; color: #000; border-color: #ccc; }}
      pre code, code {{ color: #000; background: transparent; }}
      .copy-code {{ display: none; }}
      .visual-card, .knowledge-link, .table-wrap {{ break-inside: avoid; }}
    }}
  </style>
</head>
<body>
  <div class="progress" id="progress"></div>
  <div class="layout">
    <aside>
      <div class="brand">
        <strong>Thinking in Code</strong>
        <span>Programming Journal by Anurag Atulya + Codex + Eight</span>
        <button id="mobileMenuToggle" class="mobile-menu-toggle" type="button" aria-expanded="false">Menu</button>
      </div>
      <div class="controls">
        <input id="search" type="search" placeholder="Search journal...">
        <div class="button-row">
          <button id="themeToggle" type="button">Light</button>
          <button id="compactToggle" type="button">Compact</button>
        </div>
        <div class="button-row">
          <button id="expandAll" type="button">Open all</button>
          <button id="sourceOpen" type="button">Source</button>
        </div>
        <div class="button-row">
          <button id="exportProgress" type="button">Export</button>
          <button id="importProgress" type="button">Import</button>
        </div>
        <div class="button-row">
          <button id="dueFilter" type="button">Due only</button>
          <button id="printPage" type="button">Print</button>
        </div>
        <input id="importFile" type="file" accept="application/json" hidden>
      </div>
      <section class="score-panel" aria-label="Learning score">
        <div class="score-head"><strong>Recall Score</strong><span id="scorePercent">0%</span></div>
        <div class="score-meter"><div id="scoreMeter"></div></div>
        <div class="score-grid">
          <div><b id="scoreCorrect">0/0</b><span>MCQ</span></div>
          <div><b id="scoreRecall">0</b><span>Recalls</span></div>
          <div><b id="scoreHard">0</b><span>Hard tests</span></div>
          <div><b id="scoreDue">0</b><span>Due</span></div>
        </div>
        <p class="score-note">Built on retrieval practice, confidence rating, spaced review, and transfer tests.</p>
        <button id="resetScore" class="reset-score" type="button">Reset learning data</button>
        <div class="release-meta">Journal version: <span id="journalVersion"></span></div>
      </section>
      <nav id="toc" aria-label="Journal map"></nav>
    </aside>
    <main>
      <header class="hero">
        <div class="hero-content">
          <div class="kicker">Interactive journal for future builders</div>
          <h1>Thinking in Code</h1>
          <p>Learn programming as the language of machines: from bits and control flow to production systems, feedback loops, and AI-native engineering.</p>
          <div class="signal-strip"><span>0</span><span>1</span><span>state</span><span>flow</span><span>feedback</span><span>agents</span></div>
        </div>
      </header>
      <article class="journal" id="journal">
        {rendered}
      </article>
    </main>
  </div>
  <dialog id="sourceDialog">
    <form method="dialog">
      <button type="submit">Close</button>
    </form>
    <h2>Embedded Markdown Source</h2>
    <textarea readonly id="sourceText"></textarea>
  </dialog>
  <script>
    const tocData = {toc_json};
    const rawMarkdown = {raw_json};
    const journalVersion = {version_json};
    const toc = document.getElementById('toc');
    const journal = document.getElementById('journal');
    const sourceText = document.getElementById('sourceText');
    sourceText.value = rawMarkdown;
    toc.innerHTML = tocData.map(item => `<a href="#${{item.id}}" data-level="${{item.level}}">${{item.title}}</a>`).join('');

    document.getElementById('journalVersion').textContent = journalVersion;
    const storeKey = `thinking-in-code-learning-${{journalVersion}}`;
    const legacyStoreKey = 'thinking-in-code-learning-v1';
    const nowDay = () => Math.floor(Date.now() / 86400000);
    const loadState = () => {{
      try {{
        const current = JSON.parse(localStorage.getItem(storeKey));
        if (current) return current;
        return JSON.parse(localStorage.getItem(legacyStoreKey)) || {{}};
      }}
      catch {{ return {{}}; }}
    }};
    let learningState = loadState();
    const saveState = () => localStorage.setItem(storeKey, JSON.stringify(learningState));

    const quizBank = [
      {{
        match: /computation|state|flow|transformation/i,
        q: 'Which model best describes computation in this journal?',
        options: ['Input -> transformation -> output', 'Syntax -> memorization -> certificate', 'Screen -> button -> decoration', 'Guess -> hope -> result'],
        correct: 0,
        why: 'Computation is a process: something enters, something changes, something comes out.'
      }},
      {{
        match: /computer|bits|memory|cpu|silicon/i,
        q: 'When a program feels slow, what is the strongest systems-thinking question?',
        options: ['Which layer is slow?', 'Which font is wrong?', 'Can I ignore it?', 'Should I rewrite everything immediately?'],
        correct: 0,
        why: 'Slow behavior can come from algorithm, memory, disk, network, OS, interpreter, model call, or hardware.'
      }},
      {{
        match: /decomposition|breaking problems/i,
        q: 'What is decomposition mainly for?',
        options: ['Making a big problem small enough to reason about', 'Making code look advanced', 'Avoiding planning', 'Memorizing syntax faster'],
        correct: 0,
        why: 'Decomposition reduces overwhelm by turning one large problem into solvable pieces.'
      }},
      {{
        match: /algorithm|pseudocode/i,
        q: 'A useful algorithm must be...',
        options: ['finite, unambiguous, and executable', 'long, clever, and mysterious', 'written only in Python', 'optimized before it works'],
        correct: 0,
        why: 'Algorithms are precise processes that eventually stop and can actually be carried out.'
      }},
      {{
        match: /variable/i,
        q: 'In Python, a variable is best understood as...',
        options: ['a name pointing at a value', 'a sealed box that owns a value forever', 'a comment for humans only', 'a type of loop'],
        correct: 0,
        why: 'Variables are labels/handles that point to values in memory.'
      }},
      {{
        match: /data types|type/i,
        q: 'Why do data types matter?',
        options: ['They define what operations make sense for a value', 'They make code slower on purpose', 'They replace logic', 'They only matter in old languages'],
        correct: 0,
        why: 'The type tells you the shape of data and what can legally be done with it.'
      }},
      {{
        match: /control flow|if|loop/i,
        q: 'Control flow gives a program the power to...',
        options: ['choose paths and repeat actions', 'store files permanently', 'change hardware voltage directly', 'avoid all bugs'],
        correct: 0,
        why: 'Selection and repetition are how programs respond to conditions and keep working.'
      }},
      {{
        match: /function|tool/i,
        q: 'A function is most like...',
        options: ['a named reusable process with inputs and outputs', 'a random code folder', 'a database row', 'a visual theme'],
        correct: 0,
        why: 'Functions package behavior so it can be reused, tested, and later exposed as a tool contract.'
      }},
      {{
        match: /data structures|list|dict|set|tuple/i,
        q: 'Which structure naturally maps keys to values?',
        options: ['dict', 'list', 'set', 'tuple'],
        correct: 0,
        why: 'A dictionary is a key-value lookup table.'
      }},
      {{
        match: /error|exception|debug/i,
        q: 'What is the healthiest way to treat an error?',
        options: ['as information about a mismatch in your model', 'as proof you are bad at coding', 'as something to hide with pass', 'as a reason to delete tests'],
        correct: 0,
        why: 'Errors are signals. They help locate where your assumption and reality diverged.'
      }},
      {{
        match: /modules/i,
        q: 'What problem do modules solve?',
        options: ['They let code be organized and reused across files', 'They make variables unnecessary', 'They stop all runtime errors', 'They replace functions'],
        correct: 0,
        why: 'Modules turn useful code into named files that can be imported and shared.'
      }},
      {{
        match: /cli|command-line|terminal/i,
        q: 'A good CLI is mainly a contract between...',
        options: ['terminal input, program behavior, and usable output', 'CSS, animation, and layout', 'database tables only', 'random scripts with no error messages'],
        correct: 0,
        why: 'A CLI accepts arguments/stdin, does a clear job, reports errors, and returns output.'
      }},
      {{
        match: /files|json|csv|pathlib/i,
        q: 'Why are files a major step beyond variables?',
        options: ['They preserve state after the program exits', 'They make memory infinite', 'They remove the need for errors', 'They only store Python code'],
        correct: 0,
        why: 'Files are persistent state: the program can stop and later recover stored data.'
      }},
      {{
        match: /api|fastapi|http|tool calling/i,
        q: 'What do APIs and AI tool calls have in common?',
        options: ['structured input, work, structured output', 'they never fail', 'they need no contracts', 'they only work in browsers'],
        correct: 0,
        why: 'Both depend on clear contracts at the boundary.'
      }},
      {{
        match: /pipeline|etl/i,
        q: 'A data pipeline is best understood as...',
        options: ['staged movement from source to cleaned destination', 'a single print statement', 'a UI color palette', 'a replacement for testing'],
        correct: 0,
        why: 'Pipelines extract, transform, and load data through inspectable stages.'
      }},
      {{
        match: /async|concurrency/i,
        q: 'Async helps most when code is...',
        options: ['waiting on I/O', 'doing pure heavy math', 'renaming variables', 'already synchronous and instant'],
        correct: 0,
        why: 'Async improves throughput when work spends time waiting on networks, files, APIs, or databases.'
      }},
      {{
        match: /cooperative runtimes|scheduler|backoff|event loop/i,
        q: 'What is the core production rule for cooperative runtimes?',
        options: ['never block the scheduler when the runtime expects cooperation', 'always use blocking sleep in request handlers', 'retry forever without cancellation', 'put CPU-heavy work directly on the event loop'],
        correct: 0,
        why: 'Cooperative runtimes scale when tasks yield, offload blocking work, and keep request paths responsive.'
      }},
      {{
        match: /threads|cores|accelerators|cuda|mlx|mojo|context switching|virtual threading/i,
        q: 'What is the most durable way to choose a concurrency or accelerator strategy?',
        options: ['classify the work as waiting, computing, memory-moving, or GPU-friendly', 'create as many runnable threads as possible', 'send every problem to the GPU', 'use the newest language name first'],
        correct: 0,
        why: 'Lasting engineering starts by understanding the work shape, then matching it to runtime, cores, memory, and accelerators.'
      }},
      {{
        match: /snowflake|warehouse|database|schema/i,
        q: 'In Snowflake, what is a virtual warehouse mainly responsible for?',
        options: ['compute and query execution', 'being the parent folder of every database', 'renaming table columns', 'replacing access control'],
        correct: 0,
        why: 'A warehouse is the compute lane. Databases and schemas organize objects; governance controls who may use them.'
      }},
      {{
        match: /capstone|scraper|intelligence service/i,
        q: 'What makes a capstone different from an isolated exercise?',
        options: ['It combines multiple skills into one system with boundaries', 'It avoids errors by being large', 'It should not be tested', 'It uses only one concept'],
        correct: 0,
        why: 'Capstones force integration: modules, storage, APIs, errors, async, and design trade-offs.'
      }},
      {{
        match: /rust|ownership/i,
        q: 'What value does Rust protect most aggressively?',
        options: ['memory safety and performance', 'minimum typing', 'dynamic flexibility', 'browser styling'],
        correct: 0,
        why: 'Rust uses ownership and compile-time checks to prevent whole classes of memory bugs.'
      }},
      {{
        match: /java|structure|oop/i,
        q: 'Why can Java verbosity become useful at scale?',
        options: ['It makes contracts explicit for large teams', 'It hides all types', 'It removes architecture decisions', 'It avoids compilation'],
        correct: 0,
        why: 'In large systems, explicit types, classes, and interfaces help teams coordinate safely.'
      }},
      {{
        match: /go|goroutine/i,
        q: 'Go is especially shaped around...',
        options: ['simple production concurrency', 'metaprogramming magic', 'browser-only apps', 'manual memory ownership'],
        correct: 0,
        why: 'Go makes concurrent service work approachable through goroutines, channels, and simple tooling.'
      }},
      {{
        match: /control systems|feedback|stability|overshoot/i,
        q: 'The control-systems lens says intelligence is not only output, but...',
        options: ['correction through feedback', 'more tokens', 'a prettier interface', 'one perfect action'],
        correct: 0,
        why: 'Control systems act, measure, compare, correct, and act again.'
      }},
      {{
        match: /reading other people|reading code|codebase/i,
        q: 'When reading unfamiliar code, what should come before reading every file?',
        options: ['build a map from README, entry point, tests, and one journey', 'rename everything immediately', 'delete tests', 'start with random helper functions'],
        correct: 0,
        why: 'Good code reading starts with purpose, entry points, tests, and one traceable flow.'
      }},
      {{
        match: /clean code|writing clean/i,
        q: 'Clean code is mainly about...',
        options: ['communication with future humans while preserving correctness', 'using clever names', 'making functions longer', 'avoiding tests'],
        correct: 0,
        why: 'The computer needs correctness; humans need names, structure, and intent.'
      }},
      {{
        match: /prompting|llm|agent|ai-native/i,
        q: 'Why is prompting closer to programming with uncertainty?',
        options: ['LLM output can vary, so constraints and evals matter', 'prompts are always deterministic', 'models cannot use tools', 'tests are useless for AI'],
        correct: 0,
        why: 'AI systems need clear goals, constraints, context, and evaluation because outputs are probabilistic.'
      }},
      {{
        match: /system design|production|scale|reliability/i,
        q: 'System design starts by asking...',
        options: ['what it does, scale, failure cost, and observability', 'which color palette is trendy', 'how to avoid requirements', 'how to write the longest function'],
        correct: 0,
        why: 'Systems need functional, scale, reliability, and observability thinking.'
      }}
    ];

    const precisionQuizBank = [
      {{
        match: /computation|state|flow|transformation/i,
        q: 'You are designing a habit app. The user taps "done", the streak changes, and the screen updates. Which answer names the computation most precisely?',
        options: ['tap event -> update stored state -> render new streak', 'button color -> user motivation -> app success', 'database -> CSS -> notification', 'AI prompt -> random output -> hope'],
        correct: 0,
        why: 'Good engineers trace the exact transformation: input enters, state changes, output appears.'
      }},
      {{
        match: /computer|bits|memory|cpu|silicon/i,
        q: 'An AI app feels slow. Which diagnosis shows the best hardware-stack thinking?',
        options: ['Separate model latency, network wait, CPU work, memory pressure, and disk/cache behavior before changing code', 'Increase font size so the app feels faster', 'Rewrite everything in a new language immediately', 'Assume the GPU is always the bottleneck'],
        correct: 0,
        why: 'High-IQ debugging separates layers before prescribing medicine.'
      }},
      {{
        match: /decomposition|breaking problems/i,
        q: 'Your idea is "build a personal AI study coach." Which decomposition is strongest?',
        options: ['auth, note capture, retrieval, quiz generation, scoring, review schedule, observability', 'frontend, backend, cool UI, launch', 'write code, fix bugs, add AI, ship', 'database first, everything else later'],
        correct: 0,
        why: 'Good decomposition creates testable responsibilities, not vague project phases.'
      }},
      {{
        match: /algorithm|pseudocode/i,
        q: 'A student says "the AI should help when I am stuck." Which algorithm is least ambiguous?',
        options: ['If attempts >= 2 and confidence <= 2, show a hint; if attempts >= 4, show solution with explanation', 'Help when stuck', 'Use AI when needed', 'Make it adaptive and friendly'],
        correct: 0,
        why: 'Algorithms convert intention into conditions, actions, and stopping rules.'
      }},
      {{
        match: /variable/i,
        q: 'A game needs health, score, and current level. What is the deepest reason variables matter here?',
        options: ['They name changing state so later logic can read and update it', 'They make code look professional', 'They permanently own memory forever', 'They replace the need for functions'],
        correct: 0,
        why: 'Variables matter because future decisions depend on named current state.'
      }},
      {{
        match: /data types|type/i,
        q: 'A checkout API receives price as "499" instead of 499. What is the real risk?',
        options: ['The program may concatenate, validate, compare, or calculate incorrectly because the shape is wrong', 'The database will always fix it automatically', 'Strings are faster than numbers', 'Types only matter in compiled languages'],
        correct: 0,
        why: 'Types are not trivia; they define legal operations and failure modes.'
      }},
      {{
        match: /control flow|if|loop/i,
        q: 'An AI tutor must decide between hint, quiz, and full answer. What concept is doing the real work?',
        options: ['control flow that maps learner state to the next action', 'a prettier prompt', 'a larger database table', 'a faster laptop'],
        correct: 0,
        why: 'Decision quality comes from explicit branches and repeated feedback.'
      }},
      {{
        match: /function|tool/i,
        q: 'Which function design is easiest to test and later expose as an AI tool?',
        options: ['score_answer(answer, rubric) -> score_report', 'do_everything(user_input)', 'process(data)', 'main() with hidden globals'],
        correct: 0,
        why: 'A strong function has a clear contract: named inputs, focused work, inspectable output.'
      }},
      {{
        match: /data structures|list|dict|set|tuple/i,
        q: 'You store chat messages in order, user profiles by id, and unique tags. Which structure mix is most logical?',
        options: ['list for messages, dict for profiles, set for tags', 'set for messages, list for profiles, dict for tags', 'tuple for everything', 'one giant string'],
        correct: 0,
        why: 'Structure choice should match access pattern: order, lookup, uniqueness, or fixed grouping.'
      }},
      {{
        match: /error|exception|debug/i,
        q: 'A file upload fails halfway through. Which response shows mature error handling?',
        options: ['Return a clear error, preserve consistent state, log context, and let the user retry safely', 'Hide the error and continue', 'Crash so the user knows something happened', 'Retry forever without limits'],
        correct: 0,
        why: 'Good error handling protects state, user trust, and observability.'
      }},
      {{
        match: /modules/i,
        q: 'Your app has auth, AI calls, database code, and UI helpers in one file. What is the strongest reason to split modules?',
        options: ['To create boundaries humans can navigate, test, and change independently', 'To increase file count', 'To make imports look advanced', 'To avoid learning functions'],
        correct: 0,
        why: 'Modules are cognitive architecture: they reduce blast radius and reading cost.'
      }},
      {{
        match: /cli|command-line|terminal/i,
        q: 'A CLI command silently fails but exits with success. What contract did it break?',
        options: ['It failed to communicate outcome through output, error message, and exit behavior', 'It used the wrong color theme', 'It had too many arguments', 'It did not use AI'],
        correct: 0,
        why: 'A CLI is a contract between human/automation input and reliable machine output.'
      }},
      {{
        match: /files|json|csv|pathlib/i,
        q: 'A task tracker forgets all tasks after closing. What missing concept is exposed?',
        options: ['persistent state outside process memory', 'a faster loop', 'more comments', 'a better variable name'],
        correct: 0,
        why: 'Files introduce durable memory: state that survives program exit.'
      }},
      {{
        match: /api|fastapi|http|tool calling/i,
        q: 'An AI agent calls `create_task` with no due date, bad JSON, and no user id. What should the API boundary do?',
        options: ['validate the contract before doing work and return structured errors', 'guess the missing fields', 'write partial data anyway', 'let the database crash'],
        correct: 0,
        why: 'APIs and tools are trust boundaries. Boundaries must validate intent.'
      }},
      {{
        match: /pipeline|etl/i,
        q: 'A dashboard sometimes shows nonsense because raw events feed it directly. What pipeline principle is missing?',
        options: ['separate raw, cleaned, validated, and published stages', 'make charts bigger', 'cache bad data harder', 'ask users to ignore edge cases'],
        correct: 0,
        why: 'Pipelines earn trust by making each transformation inspectable.'
      }},
      {{
        match: /cooperative runtimes|scheduler|backoff|event loop/i,
        q: 'An async web handler uses blocking validation and blocking sleep during retries. What is the real system risk?',
        options: ['one request can occupy the scheduler lane and raise latency for unrelated users', 'the function name becomes inaccurate', 'the database schema changes', 'the UI color palette breaks'],
        correct: 0,
        why: 'Cooperative runtimes depend on yielding, offloading, and cancellation-aware waits.'
      }},
      {{
        match: /async|concurrency/i,
        q: 'You need to fetch 20 URLs and most time is network wait. What execution model is the best first fit?',
        options: ['async I/O with timeouts and bounded concurrency', '20 CPU processes for every request', 'one blocking loop with no timeout', 'GPU kernels'],
        correct: 0,
        why: 'Async is for overlapping waiting, not magically speeding CPU math.'
      }},
      {{
        match: /threads|cores|accelerators|cuda|mlx|mojo|context switching|virtual threading/i,
        q: 'A service has 4 CPU cores and 400 runnable CPU-heavy threads. What is the sharpest diagnosis?',
        options: ['the scheduler and cache are being taxed by too many runnable paths for limited cores', 'virtual threads will create 400 physical cores', 'the GPU should handle all branching logic', 'context switching is always free'],
        correct: 0,
        why: 'Runnable CPU work competes for real cores. Parallelism must respect physical capacity.'
      }},
      {{
        match: /snowflake|warehouse|database|schema/i,
        q: 'Two teams query the same production table, but AI experiments are slowing dashboards. What is the best Snowflake-shaped fix?',
        options: ['separate compute warehouses and keep governed database/schema objects clear', 'duplicate every table into PUBLIC', 'rename the schema only', 'give the AI tool unlimited access'],
        correct: 0,
        why: 'Snowflake separates compute lanes from governed data namespaces.'
      }},
      {{
        match: /capstone|scraper|intelligence service/i,
        q: 'What makes the scraper intelligence service a real capstone instead of a demo?',
        options: ['it integrates fetching, cleaning, storage, API contracts, errors, async, and observability', 'it has the most files', 'it prints many lines', 'it avoids tests to move faster'],
        correct: 0,
        why: 'A capstone proves integration under realistic boundaries and failure modes.'
      }},
      {{
        match: /rust|ownership/i,
        q: 'A Python image pipeline is correct but too slow in one tight CPU loop. When might Rust enter the design?',
        options: ['when a small performance-critical component needs memory safety and predictable speed', 'when all Python code should be deleted', 'when the UI needs styling', 'when requirements are unclear'],
        correct: 0,
        why: 'Rust is a targeted tool for safety and speed, not a personality test.'
      }},
      {{
        match: /java|structure|oop/i,
        q: 'A large team keeps breaking each other\\'s feature logic. What does Java-style structure buy?',
        options: ['explicit contracts that help teams coordinate changes safely', 'less need for design', 'no runtime failures ever', 'automatic product-market fit'],
        correct: 0,
        why: 'Structure is social technology for large codebases.'
      }},
      {{
        match: /go|goroutine/i,
        q: 'A service needs many background workers reading jobs and reporting results. Why might Go feel natural?',
        options: ['goroutines and channels make simple production concurrency easy to express', 'Go hides all failure handling', 'Go is only for browsers', 'Go removes architecture decisions'],
        correct: 0,
        why: 'Go is shaped around simple concurrent services, not clever syntax.'
      }},
      {{
        match: /reading other people|reading code|codebase/i,
        q: 'You inherit a codebase before a deadline. What is the highest-leverage first move?',
        options: ['trace one real user journey through entry point, tests, data, and output', 'read random helper files alphabetically', 'rewrite naming immediately', 'delete old tests to reduce noise'],
        correct: 0,
        why: 'A traced journey turns unknown code into a map.'
      }},
      {{
        match: /clean code|writing clean/i,
        q: 'A function is 90 lines long, mutates globals, catches all errors, and returns mixed shapes. What is the true problem?',
        options: ['future readers cannot predict its contract, side effects, or failure behavior', 'it needs a shorter variable name', 'it should be moved to CSS', 'it is too beginner-friendly'],
        correct: 0,
        why: 'Clean code is about preserving human reasoning under change.'
      }},
      {{
        match: /system design|production|scale|reliability/i,
        q: 'Your study app works for 5 friends. Before 10,000 exam-week users arrive, what must system design answer?',
        options: ['traffic, data ownership, failure modes, security, latency, cost, and observability', 'only the logo and landing page', 'which syntax looks coolest', 'how to avoid logs'],
        correct: 0,
        why: 'System design is how a feature becomes a trustworthy product.'
      }},
      {{
        match: /control systems|feedback|stability|overshoot/i,
        q: 'An AI agent keeps taking stronger actions after weak signals. Which control-system concept is being violated?',
        options: ['stability through measured feedback and bounded correction', 'token count maximization', 'visual polish', 'one-shot execution'],
        correct: 0,
        why: 'Intelligent systems need feedback, limits, and correction without overshoot.'
      }},
      {{
        match: /prompting|llm|agent|ai-native/i,
        q: 'A prompt says "make it better" and the model rewrites everything. What was missing?',
        options: ['specification: goal, constraints, allowed changes, tests, and evaluation criteria', 'more enthusiasm', 'a longer chat history only', 'a random model switch'],
        correct: 0,
        why: 'Prompting becomes engineering when intent is constrained and verifiable.'
      }}
    ];

    function quizFor(title) {{
      const found = precisionQuizBank.find(item => item.match.test(title)) || quizBank.find(item => item.match.test(title));
      if (found) return found;
      return {{
        q: `A sharp learner reaches "${{title}}" and wants proof of understanding. What should they do?`,
        options: ['explain the concept, apply it to a real system, name a failure mode, and test the idea', 'recognize the heading and move on', 'copy one example without changing it', 'ask AI for the answer and trust it blindly'],
        correct: 0,
        why: 'Real mastery requires recall, transfer, failure awareness, and verification.'
      }};
    }}

    function recallPrompt(title) {{
      const precisionPrompts = [
        [/computation/i, 'No notes. Pick one app and explain its input, hidden state, transformation, output, and one failure mode.'],
        [/computer|bits|cpu|silicon/i, 'Trace one user action from screen input down through runtime, memory/CPU, and back to visible output. Name where latency could enter.'],
        [/decomposition/i, 'Take a dream app and split it into responsibilities. For each piece, say what it owns and what it must not own.'],
        [/algorithm/i, 'Write an algorithm in plain English with conditions and stopping rules. Then identify one ambiguous word and remove it.'],
        [/variable/i, 'Explain how one named value changes over time in a game, checkout flow, or AI tutor. Include who reads it later.'],
        [/data types/i, 'Choose four values from a real app and explain how the wrong type would create a bug.'],
        [/control flow/i, 'Describe a real decision tree: what condition is checked, what branch runs, what repeats, and what stops it.'],
        [/function/i, 'Explain one function as a contract: inputs, output, side effects, failure modes, and why it deserves a name.'],
        [/data structures/i, 'For one feature, justify list vs dict vs set vs tuple using access pattern, not memorized definitions.'],
        [/error|exception/i, 'Explain one failure as signal: what assumption broke, what state must be protected, and what the user should see.'],
        [/modules/i, 'Map a small app into modules and defend each boundary as if another engineer must maintain it.'],
        [/cli/i, 'Explain a CLI command as an automation contract: args, validation, stdout, stderr, exit behavior.'],
        [/files/i, 'Explain what state should survive program exit, why JSON/CSV/text fits or fails, and how corruption could happen.'],
        [/api|fastapi/i, 'Explain an API endpoint as a trust boundary: request shape, validation, work, response, and error contract.'],
        [/pipeline/i, 'Trace dirty data through raw, cleaned, validated, and published stages. Name what can be inspected at each stage.'],
        [/async/i, 'Explain which parts of a real AI app are waiting and how async prevents one wait from freezing unrelated work.'],
        [/cooperative runtimes|scheduler/i, 'Explain scheduler cooperation using yield, offload, cancellation, and backoff. Name one blocking smell.'],
        [/threads|cores|accelerators|cuda|mlx|mojo/i, 'Classify a workload as waiting, CPU-bound, memory-bound, or GPU-friendly. Explain what happens if you choose wrong.'],
        [/snowflake|warehouse|database|schema/i, 'Explain warehouse, database, schema, object, role, and cost using one production data example.'],
        [/capstone/i, 'Explain the capstone as a system path from input source to insight. Include where failures are logged.'],
        [/rust/i, 'Explain where Python should stay and where Rust might enter. Justify with safety, speed, and maintenance cost.'],
        [/java/i, 'Explain how explicit contracts help a team change code without silently breaking each other.'],
        [/go/i, 'Explain goroutines, channels, and worker boundaries using a background job system.'],
        [/debug/i, 'State a bug, three hypotheses, the smallest test for each, and what observation would change your mind.'],
        [/reading/i, 'Explain how you would build a map of an unknown repo before editing. Include entry point, tests, and one journey.'],
        [/clean/i, 'Explain how one messy function damages future reasoning. Name the contract you would extract first.'],
        [/system design/i, 'Explain a study app for 10,000 users: data, traffic, failure, security, latency, cost, and observability.']
      ];
      const sharp = precisionPrompts.find(([pattern]) => pattern.test(title));
      if (sharp) return sharp[1];
      const prompts = [
        [/computation/i, 'Explain computation using one app you used today. Name the input, state, transformation, and output.'],
        [/computer|bits|cpu/i, 'Explain how a tiny on/off signal can become a program layer by layer.'],
        [/decomposition/i, 'Take one big app idea and split it into five smaller tasks from memory.'],
        [/algorithm/i, 'Explain what makes instructions precise enough for a machine.'],
        [/variable/i, 'Explain variables without using the word box. Use the sticky-note model.'],
        [/data types/i, 'Explain type as shape: what can you do with text, number, boolean, and None?'],
        [/control flow/i, 'Trace a cursor through an if statement and a loop in plain language.'],
        [/function/i, 'Explain function as input, named process, output, and side effects.'],
        [/data structures/i, 'Explain when to choose list, dict, set, and tuple.'],
        [/error|exception/i, 'Explain why an error is information, not failure.'],
        [/modules/i, 'Explain why code needs to move from one file into reusable modules.'],
        [/cli/i, 'Explain the contract of a CLI: input, work, output, error.'],
        [/files/i, 'Explain persistent state and why files matter before databases.'],
        [/api|fastapi/i, 'Explain HTTP request-response as a function call across a network.'],
        [/pipeline/i, 'Explain extract-transform-load using a messy spreadsheet example.'],
        [/async/i, 'Explain async using waiting, not speed magic.'],
        [/cooperative runtimes|scheduler/i, 'Explain why blocking the scheduler is like stopping in front of a traffic controller.'],
        [/threads|cores|accelerators|cuda|mlx|mojo/i, 'Explain code flow from source code to runtime, thread, core or GPU, memory/I/O, and result.'],
        [/snowflake|warehouse|database|schema/i, 'Explain Snowflake as compute lane plus data namespace: warehouse, database, schema, object, governance.'],
        [/capstone/i, 'Explain how the capstone combines storage, API, async, pipeline, and modules.'],
        [/rust/i, 'Explain why Rust feels strict and what that strictness buys.'],
        [/java/i, 'Explain why explicit structure helps large teams.'],
        [/go/i, 'Explain goroutines as simple concurrent workers.'],
        [/debug/i, 'Explain debugging as hypothesis, test, observation, correction.'],
        [/reading/i, 'Explain how to map unfamiliar code before editing it.'],
        [/clean/i, 'Explain clean code as communication with future humans.'],
        [/system design/i, 'Explain scale, reliability, maintainability, and observability.']
      ];
      const found = prompts.find(([pattern]) => pattern.test(title));
      return found ? found[1] : `Explain "${{title}}" from memory: definition, example, mistake, future unlock.`;
    }}

    function hardPrompt(title) {{
      const precisionPrompts = [
        [/computation/i, 'Transfer boss: design a tiny fraud detector as input/state/transformation/output. Add one false-positive risk and one test.'],
        [/computer|bits|cpu/i, 'Transfer boss: an AI app is slow. Build a bottleneck tree from browser to network to server to model to memory/CPU/GPU. Pick the first measurement.'],
        [/decomposition/i, 'Transfer boss: decompose a personal AI study app into modules, data contracts, and failure boundaries. Mark one piece you would build first and why.'],
        [/algorithm/i, 'Transfer boss: write pseudocode for an adaptive quiz engine that gives hint, retry, or solution based on confidence and attempts. Include stopping rules.'],
        [/variable/i, 'Transfer boss: design the state model for a learning streak system. Include update rules and one bug caused by stale state.'],
        [/data types/i, 'Transfer boss: design request/response types for creating a task with title, due date, tags, priority, and optional AI summary. Include invalid examples.'],
        [/control flow/i, 'Transfer boss: design the decision flow for content moderation in a student app. Include allow, warn, block, escalate, and appeal paths.'],
        [/function/i, 'Transfer boss: turn three repeated product behaviors into functions with signatures, return values, and test cases. One must be safe for AI tool calling.'],
        [/data structures/i, 'Transfer boss: model a chat app with messages, users, unread counts, unique reactions, pinned config, and search tags. Justify every structure.'],
        [/error|exception/i, 'Transfer boss: design failure handling for an AI tool call that may timeout, return invalid JSON, or partially write data. Include rollback or compensation.'],
        [/modules/i, 'Transfer boss: split an AI tutor backend into modules. For each module, define public functions and forbidden dependencies.'],
        [/cli/i, 'Transfer boss: design a CLI for importing notes, generating quizzes, exporting progress, and reporting failures in automation-friendly output.'],
        [/files/i, 'Transfer boss: design a local progress file format with versioning, migration, backup, and corrupted-file recovery.'],
        [/api|fastapi/i, 'Transfer boss: design one API endpoint that a browser and an AI agent can both call safely. Include auth, validation, idempotency, and errors.'],
        [/pipeline/i, 'Transfer boss: design a pipeline from raw PDFs to searchable study cards. Include validation checkpoints and bad-data quarantine.'],
        [/async/i, 'Transfer boss: design bounded async work for 50 document uploads. Include timeouts, cancellation, backpressure, and progress streaming.'],
        [/cooperative runtimes|scheduler/i, 'Transfer boss: audit an async retry system. Find blocking waits, retry storms, cancellation leaks, and work that should be offloaded.'],
        [/threads|cores|accelerators|cuda|mlx|mojo/i, 'Transfer boss: design execution lanes for an AI product: request path, CPU workers, GPU batches, database calls, and observability. Name what must never be unbounded.'],
        [/snowflake|warehouse|database|schema/i, 'Transfer boss: design Snowflake layout for a factory AI assistant. Separate warehouses, databases, schemas, trusted views, roles, freshness, and cost controls.'],
        [/capstone/i, 'Transfer boss: turn the scraper into a production service. Add queueing, rate limits, retries, storage, observability, and one user-facing SLA.'],
        [/rust/i, 'Transfer boss: choose whether to rewrite a slow Python component in Rust. Include profiling evidence, interface boundary, and maintenance trade-off.'],
        [/java/i, 'Transfer boss: design interfaces for a team-owned learning platform. Include service contracts and how version changes stay safe.'],
        [/go/i, 'Transfer boss: design Go workers for processing learning analytics. Include job ownership, channels, cancellation, and leak prevention.'],
        [/debug/i, 'Transfer boss: debug a wrong Recall Score. Create a hypothesis table: symptom, suspected layer, test, expected observation, fix.'],
        [/reading/i, 'Transfer boss: map this HTML generator before adding a feature. Identify parse path, render path, script behavior, and release checks.'],
        [/clean/i, 'Transfer boss: refactor a long feature function into named steps. Preserve behavior, add tests, and explain the cognitive win.'],
        [/system design/i, 'Transfer boss: design cloud progress sync for this journal. Include offline mode, auth, conflict resolution, data model, API, rate limits, monitoring, and privacy.']
      ];
      const sharp = precisionPrompts.find(([pattern]) => pattern.test(title));
      if (sharp) return sharp[1];
      const prompts = [
        [/computation/i, 'Hard transfer: model an AI chatbot as input, state, transformation, output, and failure modes.'],
        [/computer|bits|cpu/i, 'Hard transfer: diagnose a slow AI app by listing possible bottleneck layers from model call down to hardware.'],
        [/decomposition/i, 'Hard transfer: decompose an AI tutor that refuses to give answers too quickly.'],
        [/algorithm/i, 'Hard transfer: write pseudocode for a feedback-controlled study coach.'],
        [/variable/i, 'Hard transfer: design the state variables an AI study coach needs to remember.'],
        [/data types/i, 'Hard transfer: define the types for an API request that creates a student task.'],
        [/control flow/i, 'Hard transfer: write the decision flow for when an AI tutor gives hint, asks question, or reveals answer.'],
        [/function/i, 'Hard transfer: design three functions that could become AI agent tools.'],
        [/data structures/i, 'Hard transfer: choose structures for chat history, known facts, unique tags, and fixed config.'],
        [/error|exception/i, 'Hard transfer: design error handling for a failed AI tool call.'],
        [/modules/i, 'Hard transfer: split an AI tutor project into modules and explain each boundary.'],
        [/cli/i, 'Hard transfer: design CLI commands for exporting and importing learning progress.'],
        [/files/i, 'Hard transfer: design a JSON format for saving recall scores and due reviews.'],
        [/api|fastapi/i, 'Hard transfer: design an API endpoint that an AI agent can call safely.'],
        [/pipeline/i, 'Hard transfer: design a pipeline that turns raw notes into quiz cards.'],
        [/async/i, 'Hard transfer: design async fetching for ten sources without blocking the UI.'],
        [/cooperative runtimes|scheduler/i, 'Hard transfer: design a retry-with-backoff system that yields, respects cancellation, and avoids retry storms.'],
        [/threads|cores|accelerators|cuda|mlx|mojo/i, 'Hard transfer: classify each step of an AI app as I/O-bound, CPU-bound, memory-bound, or GPU-friendly, then choose async, virtual threads, worker pools, processes, or accelerator batches.'],
        [/snowflake|warehouse|database|schema/i, 'Hard transfer: design a Snowflake layout for an industrial AI assistant with separate compute lanes, trusted schemas, governance, freshness, and cost limits.'],
        [/capstone/i, 'Hard transfer: add observability and rate limits to the scraper intelligence service.'],
        [/rust/i, 'Hard transfer: choose what part of a Python AI product might deserve Rust and why.'],
        [/java/i, 'Hard transfer: design interfaces for a team-owned learning platform.'],
        [/go/i, 'Hard transfer: design concurrent workers for processing learning analytics.'],
        [/debug/i, 'Hard transfer: form three hypotheses for a wrong score in this journal UI and one test for each.'],
        [/reading/i, 'Hard transfer: map this HTML generator before changing one feature.'],
        [/clean/i, 'Hard transfer: refactor a long function into named steps and explain the human benefit.'],
        [/system design/i, 'Hard transfer: design the production architecture for this journal if progress sync becomes cloud-based.']
      ];
      const found = prompts.find(([pattern]) => pattern.test(title));
      return found ? found[1] : `Transfer test: apply "${{title}}" to an AI study coach, a robot controller, or a real app. Name the past knowledge it uses, the present idea, the future concept it unlocks, and one failure mode.`;
    }}

    function buildLearningChecks() {{
      document.querySelectorAll('.entry-section').forEach((section, index) => {{
        const heading = section.querySelector('h1, h2');
        if (!heading || section.querySelector('.learning-check')) return;
        const title = heading.innerText.trim();
        const id = section.id || `section-${{index}}`;
        const quiz = quizFor(title);
        const saved = learningState[id] || {{}};
        const details = document.createElement('details');
        details.className = 'learning-check';
        if (saved.recalled || saved.hard || saved.correct) details.classList.add('done');
        section.dataset.due = saved.due !== undefined && saved.due <= nowDay() ? 'true' : 'false';
        details.innerHTML = `
          <summary>Brain Check <span data-check-status>${{saved.correct ? 'remembered' : 'active recall'}}</span></summary>
          <div class="check-body">
            <div class="check-stage">
              <h4>1. Scenario MCQ</h4>
              <p>${{quiz.q}}</p>
              <div class="mcq-options">
                ${{quiz.options.map((option, optionIndex) => `<button type="button" data-option="${{optionIndex}}">${{option}}</button>`).join('')}}
              </div>
              <p class="check-feedback">${{saved.correct ? quiz.why : ''}}</p>
            </div>
            <div class="check-stage">
              <h4>2. Causal Recall</h4>
              <p>${{recallPrompt(title)}}</p>
              <textarea class="recall-box" placeholder="Type from memory. Imperfect is fine. Retrieval is the exercise.">${{saved.recallText || ''}}</textarea>
              <div class="button-row">
                <button type="button" data-recall-save>Save recall</button>
                <button type="button" data-cue>Show cue</button>
              </div>
              <p class="check-feedback" data-cue-text></p>
            </div>
            <div class="check-stage">
              <h4>3. Confidence Rating</h4>
              <p>How confidently could you explain this tomorrow?</p>
              <div class="confidence-row">
                <button type="button" data-confidence="1">1 Hard</button>
                <button type="button" data-confidence="2">2 Shaky</button>
                <button type="button" data-confidence="3">3 Good</button>
                <button type="button" data-confidence="4">4 Solid</button>
              </div>
            </div>
            <div class="check-stage">
              <h4>4. Transfer Boss Test</h4>
              <p class="hard-prompt">${{hardPrompt(title)}}</p>
              <button type="button" data-hard-done>${{saved.hard ? 'Hard test marked' : 'Mark hard test done'}}</button>
            </div>
          </div>`;
        section.querySelector('.entry-inner')?.appendChild(details);

        details.querySelectorAll('[data-option]').forEach(button => {{
          button.addEventListener('click', () => {{
            const selected = Number(button.dataset.option);
            const correct = selected === quiz.correct;
            details.querySelectorAll('[data-option]').forEach(btn => {{
              btn.classList.remove('correct-choice', 'wrong-choice');
              if (Number(btn.dataset.option) === quiz.correct) btn.classList.add('correct-choice');
            }});
            if (!correct) button.classList.add('wrong-choice');
            learningState[id] = {{ ...learningState[id], attempted: true, correct, last: Date.now() }};
            details.querySelector('.check-feedback').textContent = correct ? `Correct. ${{quiz.why}}` : `Not quite. ${{quiz.why}}`;
            details.classList.add('done');
            saveState();
            updateScore();
          }});
        }});

        details.querySelector('[data-recall-save]').addEventListener('click', () => {{
          const text = details.querySelector('.recall-box').value.trim();
          learningState[id] = {{ ...learningState[id], recalled: Boolean(text), recallText: text, last: Date.now() }};
          saveState();
          updateScore();
        }});
        details.querySelector('[data-cue]').addEventListener('click', () => {{
          details.querySelector('[data-cue-text]').textContent = 'Cue: define it, give one example, name one mistake, then connect it to a future concept.';
        }});
        details.querySelectorAll('[data-confidence]').forEach(button => {{
          const value = Number(button.dataset.confidence);
          if (saved.confidence === value) button.classList.add('active');
          button.addEventListener('click', () => {{
            const intervals = {{ 1: 0, 2: 1, 3: 3, 4: 7 }};
            details.querySelectorAll('[data-confidence]').forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
          learningState[id] = {{ ...learningState[id], confidence: value, due: nowDay() + intervals[value], last: Date.now() }};
            section.dataset.due = learningState[id].due <= nowDay() ? 'true' : 'false';
            saveState();
            updateScore();
          }});
        }});
        details.querySelector('[data-hard-done]').addEventListener('click', e => {{
          learningState[id] = {{ ...learningState[id], hard: true, last: Date.now() }};
          e.currentTarget.textContent = 'Hard test marked';
          details.classList.add('done');
          saveState();
          updateScore();
        }});
      }});
    }}

    function updateScore() {{
      const sectionsForScore = [...document.querySelectorAll('.entry-section')].filter(section => section.querySelector('.learning-check'));
      const total = sectionsForScore.length || 1;
      let attempted = 0, correct = 0, recalled = 0, hard = 0, confidenceSum = 0, due = 0;
      sectionsForScore.forEach(section => {{
        const item = learningState[section.id] || {{}};
        if (item.attempted) attempted += 1;
        if (item.correct) correct += 1;
        if (item.recalled) recalled += 1;
        if (item.hard) hard += 1;
        confidenceSum += item.confidence || 0;
        if (item.due !== undefined && item.due <= nowDay()) due += 1;
      }});
      const mcqScore = correct / total;
      const recallScore = recalled / total;
      const hardScore = hard / total;
      const confidenceScore = confidenceSum / (total * 4);
      const mastery = Math.round((mcqScore * .35 + recallScore * .25 + confidenceScore * .2 + hardScore * .2) * 100);
      document.getElementById('scorePercent').textContent = `${{mastery}}%`;
      document.getElementById('scoreMeter').style.width = `${{mastery}}%`;
      document.getElementById('scoreCorrect').textContent = `${{correct}}/${{attempted}}`;
      document.getElementById('scoreRecall').textContent = recalled;
      document.getElementById('scoreHard').textContent = hard;
      document.getElementById('scoreDue').textContent = due;
    }}

    buildLearningChecks();
    updateScore();

    document.getElementById('resetScore').addEventListener('click', () => {{
      if (!confirm('Reset all local learning score data for this journal?')) return;
      learningState = {{}};
      saveState();
      location.reload();
    }});
    document.getElementById('exportProgress').addEventListener('click', () => {{
      const payload = {{
        artifact: 'thinking-in-code',
        version: journalVersion,
        exportedAt: new Date().toISOString(),
        learningState
      }};
      const blob = new Blob([JSON.stringify(payload, null, 2)], {{ type: 'application/json' }});
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `thinking-in-code-progress-${{journalVersion}}.json`;
      link.click();
      URL.revokeObjectURL(url);
    }});
    document.getElementById('importProgress').addEventListener('click', () => document.getElementById('importFile').click());
    document.getElementById('importFile').addEventListener('change', async e => {{
      const file = e.target.files?.[0];
      if (!file) return;
      try {{
        const payload = JSON.parse(await file.text());
        if (!payload.learningState || typeof payload.learningState !== 'object') throw new Error('Missing learningState');
        learningState = payload.learningState;
        saveState();
        location.reload();
      }} catch (error) {{
        alert('Could not import progress JSON: ' + error.message);
      }}
    }});
    let dueOnly = false;
    document.getElementById('dueFilter').addEventListener('click', e => {{
      dueOnly = !dueOnly;
      e.currentTarget.textContent = dueOnly ? 'Show all' : 'Due only';
      document.querySelectorAll('.entry-section').forEach(section => {{
        section.classList.toggle('hidden', dueOnly && section.dataset.due !== 'true');
      }});
    }});
    document.getElementById('printPage').addEventListener('click', () => window.print());

    document.querySelectorAll('.section-toggle').forEach(button => {{
      button.addEventListener('click', () => {{
        const section = button.closest('.entry-section');
        section.classList.toggle('collapsed');
        button.textContent = section.classList.contains('collapsed') ? 'Open' : 'Collapse';
      }});
    }});

    function setSectionCollapsed(section, collapsed) {{
      section.classList.toggle('collapsed', collapsed);
      const button = section.querySelector('.section-toggle');
      if (button) button.textContent = collapsed ? 'Open' : 'Collapse';
    }}

    function collapseForOverview() {{
      document.querySelectorAll('.entry-section').forEach((section, index) => {{
        if (index === 0) return setSectionCollapsed(section, false);
        setSectionCollapsed(section, true);
      }});
      document.getElementById('expandAll').textContent = 'Open all';
    }}

    function openSectionFromLink(hash) {{
      let section = null;
      try {{
        section = hash ? document.getElementById(decodeURIComponent(hash.slice(1))) : null;
      }} catch {{
        section = null;
      }}
      if (!section) return;
      section.classList.remove('hidden');
      setSectionCollapsed(section, false);
      document.querySelector('aside')?.classList.remove('mobile-open');
      const mobileButton = document.getElementById('mobileMenuToggle');
      if (mobileButton) {{
        mobileButton.textContent = 'Menu';
        mobileButton.setAttribute('aria-expanded', 'false');
      }}
    }}

    collapseForOverview();
    if (location.hash) openSectionFromLink(location.hash);

    document.querySelectorAll('.copy-code').forEach(button => {{
      button.addEventListener('click', async () => {{
        const code = button.parentElement.querySelector('code').innerText;
        await navigator.clipboard.writeText(code);
        const old = button.textContent;
        button.textContent = 'Copied';
        setTimeout(() => button.textContent = old, 900);
      }});
    }});

    document.getElementById('themeToggle').addEventListener('click', e => {{
      document.body.classList.toggle('light');
      e.currentTarget.textContent = document.body.classList.contains('light') ? 'Dark' : 'Light';
    }});
    document.getElementById('compactToggle').addEventListener('click', e => {{
      document.body.classList.toggle('compact');
      e.currentTarget.textContent = document.body.classList.contains('compact') ? 'Roomy' : 'Compact';
    }});
    document.getElementById('expandAll').addEventListener('click', e => {{
      const shouldOpen = e.currentTarget.textContent !== 'Collapse all';
      document.querySelectorAll('.entry-section').forEach(section => {{
        section.classList.remove('hidden');
        setSectionCollapsed(section, !shouldOpen);
      }});
      e.currentTarget.textContent = shouldOpen ? 'Collapse all' : 'Open all';
      document.getElementById('search').value = '';
    }});
    document.getElementById('sourceOpen').addEventListener('click', () => document.getElementById('sourceDialog').showModal());

    const search = document.getElementById('search');
    search.addEventListener('input', () => {{
      const q = search.value.trim().toLowerCase();
      document.querySelectorAll('.entry-section').forEach(section => {{
        const match = !q || section.innerText.toLowerCase().includes(q);
        section.classList.toggle('hidden', !match);
        if (q && match) setSectionCollapsed(section, false);
      }});
    }});

    const links = [...toc.querySelectorAll('a')];
    links.forEach(link => link.addEventListener('click', () => openSectionFromLink(link.getAttribute('href'))));
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    mobileMenuToggle.addEventListener('click', () => {{
      const aside = document.querySelector('aside');
      const open = !aside.classList.contains('mobile-open');
      aside.classList.toggle('mobile-open', open);
      mobileMenuToggle.textContent = open ? 'Close' : 'Menu';
      mobileMenuToggle.setAttribute('aria-expanded', String(open));
    }});
    window.addEventListener('hashchange', () => openSectionFromLink(location.hash));

    const sectionForHash = hash => {{
      try {{ return hash ? document.getElementById(decodeURIComponent(hash.slice(1))) : null; }}
      catch {{ return null; }}
    }};
    const sections = links.map(link => sectionForHash(link.getAttribute('href'))).filter(Boolean);
    const observer = new IntersectionObserver(entries => {{
      entries.forEach(entry => {{
        if (entry.isIntersecting) {{
          links.forEach(link => link.classList.toggle('active', link.getAttribute('href') === '#' + entry.target.id));
        }}
      }});
    }}, {{ rootMargin: '-30% 0px -60% 0px', threshold: 0 }});
    sections.forEach(section => observer.observe(section));

    window.addEventListener('scroll', () => {{
      const max = document.documentElement.scrollHeight - window.innerHeight;
      document.getElementById('progress').style.width = `${{(window.scrollY / max) * 100}}%`;
    }}, {{ passive: true }});
  </script>
</body>
</html>"""


def main() -> None:
    raw = SOURCE.read_text(encoding="utf-8")
    version = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]
    rendered, toc = render_markdown(raw)
    TARGET.write_text(build_html(rendered, toc, raw, version), encoding="utf-8")
    print(f"Wrote {TARGET}")


if __name__ == "__main__":
    main()
