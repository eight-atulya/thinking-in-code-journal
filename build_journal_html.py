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
      min-height: 88vh; display: grid; align-items: end; padding: 72px clamp(24px, 6vw, 92px) 40px;
      border-bottom: 1px solid var(--line); position: relative; overflow: hidden;
    }}
    .hero::before {{
      content: ""; position: absolute; inset: 0; opacity: .45;
      background-image:
        linear-gradient(rgba(255,255,255,.05) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,.05) 1px, transparent 1px);
      background-size: 42px 42px; mask-image: linear-gradient(to bottom, black, transparent 78%);
    }}
    .hero-content {{ position: relative; max-width: 980px; }}
    .kicker {{ color: var(--yellow); text-transform: uppercase; font-weight: 900; letter-spacing: .12em; font-size: .78rem; }}
    .hero h1 {{ margin: 12px 0; font-size: clamp(2.7rem, 8vw, 7rem); line-height: .92; letter-spacing: 0; }}
    .hero p {{ color: var(--muted); font-size: clamp(1rem, 2vw, 1.32rem); max-width: 760px; }}
    .signal-strip {{ display: flex; gap: 8px; margin-top: 24px; flex-wrap: wrap; }}
    .signal-strip span {{ border: 1px solid var(--line); padding: 6px 9px; border-radius: 999px; background: var(--panel); }}
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
    h1, h2, h3, h4 {{ line-height: 1.08; letter-spacing: 0; }}
    h1 a, h2 a, h3 a, h4 a {{ color: inherit; text-decoration: none; }}
    h1 {{ font-size: clamp(2.1rem, 5vw, 4.8rem); margin: 0 0 24px; }}
    h2 {{ font-size: clamp(1.6rem, 3.4vw, 3rem); margin: 0 0 24px; }}
    h3 {{ margin-top: 34px; color: var(--yellow); font-size: 1.23rem; }}
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
      aside {{ position: relative; height: auto; }}
      .hero {{ min-height: 68vh; }}
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
      </div>
      <div class="controls">
        <input id="search" type="search" placeholder="Search journal...">
        <div class="button-row">
          <button id="themeToggle" type="button">Light</button>
          <button id="compactToggle" type="button">Compact</button>
        </div>
        <div class="button-row">
          <button id="expandAll" type="button">Expand</button>
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
          <div class="kicker">Silicon -> Code -> Control -> AI</div>
          <h1>Thinking in Code</h1>
          <p>A self-contained interactive programming journal about machines, feedback, language, and AI-native systems.</p>
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

    function quizFor(title) {{
      const found = quizBank.find(item => item.match.test(title));
      if (found) return found;
      return {{
        q: `What is the strongest way to learn "${{title}}"?`,
        options: ['connect past knowledge, explain the present idea, and name the future unlock', 'read once and move on', 'copy code without testing', 'skip the hard parts'],
        correct: 0,
        why: 'Durable learning comes from retrieval, connection, transfer, and feedback.'
      }};
    }}

    function recallPrompt(title) {{
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
              <h4>1. Quick MCQ</h4>
              <p>${{quiz.q}}</p>
              <div class="mcq-options">
                ${{quiz.options.map((option, optionIndex) => `<button type="button" data-option="${{optionIndex}}">${{option}}</button>`).join('')}}
              </div>
              <p class="check-feedback">${{saved.correct ? quiz.why : ''}}</p>
            </div>
            <div class="check-stage">
              <h4>2. Active Recall</h4>
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
              <h4>4. Hard Transfer Test</h4>
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
    document.getElementById('expandAll').addEventListener('click', () => {{
      document.querySelectorAll('.entry-section').forEach(section => section.classList.remove('collapsed', 'hidden'));
      document.querySelectorAll('.section-toggle').forEach(button => button.textContent = 'Collapse');
      document.getElementById('search').value = '';
    }});
    document.getElementById('sourceOpen').addEventListener('click', () => document.getElementById('sourceDialog').showModal());

    const search = document.getElementById('search');
    search.addEventListener('input', () => {{
      const q = search.value.trim().toLowerCase();
      document.querySelectorAll('.entry-section').forEach(section => {{
        section.classList.toggle('hidden', q && !section.innerText.toLowerCase().includes(q));
      }});
    }});

    const links = [...toc.querySelectorAll('a')];
    const sections = links.map(link => document.querySelector(link.getAttribute('href'))).filter(Boolean);
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
