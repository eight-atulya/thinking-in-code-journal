from __future__ import annotations

import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parent
HTML = ROOT / "index.html"
MD = ROOT / "journal.md"
GENERATOR = ROOT / "build_journal_html.py"


REQUIRED_SNIPPETS = [
    "Recall Score",
    "exportProgress",
    "importProgress",
    "dueFilter",
    "printPage",
    "@media print",
    "journalVersion",
    "knowledge-link",
    "learning-check",
    "precisionQuizBank",
    "Scenario MCQ",
    "Causal Recall",
    "Transfer Boss Test",
    "rawMarkdown",
    "sourceDialog",
]


class Parser(HTMLParser):
    pass


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def main() -> None:
    for path in [HTML, MD, GENERATOR]:
        if not path.exists():
            fail(f"missing {path.name}")

    html = HTML.read_text(encoding="utf-8")
    md = MD.read_text(encoding="utf-8")

    try:
        Parser().feed(html)
    except Exception as exc:
        fail(f"HTML parser rejected artifact: {exc}")

    scripts = re.findall(r"<script>(.*?)</script>", html, flags=re.S)
    if not scripts:
        fail("no embedded script found")

    js_path = ROOT / ".release-check.js"
    js_path.write_text("\n".join(scripts), encoding="utf-8")
    try:
        subprocess.run(["node", "--check", str(js_path)], check=True, capture_output=True, text=True)
    except FileNotFoundError:
        fail("node is required for JS syntax validation")
    except subprocess.CalledProcessError as exc:
        fail(f"JS syntax validation failed:\n{exc.stderr}")
    finally:
        js_path.unlink(missing_ok=True)

    if "<link" in html:
        fail("artifact contains external link tags")

    missing = [snippet for snippet in REQUIRED_SNIPPETS if snippet not in html]
    if missing:
        fail("missing required release snippets: " + ", ".join(missing))

    section_count = html.count('class="entry-section')
    code_count = html.count('class="code-card')
    knowledge_count = html.count('class="knowledge-link')
    visual_count = html.count('class="visual-card')
    dream_lab_count = html.count('id="dream-lab')
    senior_cut_count = html.count('id="senior-cut')

    if section_count < 70:
        fail(f"too few rendered sections: {section_count}")
    if code_count < 100:
        fail(f"too few code cards: {code_count}")
    if knowledge_count < 27:
        fail(f"too few knowledge-link cards: {knowledge_count}")
    if visual_count < 57:
        fail(f"too few visual cards: {visual_count}")
    if dream_lab_count < 27:
        fail(f"too few dream lab anchors: {dream_lab_count}")
    if senior_cut_count < 27:
        fail(f"too few senior cut anchors: {senior_cut_count}")
    if len(html) < len(md):
        fail("HTML artifact is unexpectedly smaller than markdown source")

    print("release-check-ok")
    print(f"sections={section_count}")
    print(f"code_cards={code_count}")
    print(f"knowledge_links={knowledge_count}")
    print(f"visual_cards={visual_count}")
    print(f"dream_labs={dream_lab_count}")
    print(f"senior_cuts={senior_cut_count}")
    print(f"html_bytes={len(html)}")


if __name__ == "__main__":
    main()
