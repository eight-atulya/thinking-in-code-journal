from __future__ import annotations

import re
import subprocess
import sys
import json
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parent
HTML = ROOT / "index.html"
MD = ROOT / "journal.md"
GENERATOR = ROOT / "build_journal_html.py"
TOPIC_ROOT = ROOT / "modular-journal-topic-spaces"
TOPIC_INDEX = TOPIC_ROOT / "topic-space-index-file.json"
TOPIC_SOURCE_NAME = "core-topic-source-file.md"
TOPIC_PAGE_NAME = "built-topic-page-file.html"


REQUIRED_SNIPPETS = [
    "Recall Score",
    "exportProgress",
    "if-may-pitch.html",
    "pitch-link",
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
    "search-panel",
    "searchResults",
    "scoreSearchItem",
    "applySearch",
    "search-muted",
    "@media (max-width: 430px)",
    ".confidence-row { grid-template-columns: 1fr; }",
    "overflow-wrap: anywhere",
    "white-space: normal",
    "Publish Your First Page for Free",
    "GitHub Pages deployment flow",
    "Pages source main / (root)",
    "first deployment loop",
    "Modular Journal Topic Spaces",
    "topic-space-card",
    "future-firewall-decision-layer",
    "agentic-loops-control-cycle",
]


class Parser(HTMLParser):
    pass


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def validate_embedded_scripts(html: str, label: str) -> None:
    scripts = re.findall(r"<script>(.*?)</script>", html, flags=re.S)
    if not scripts:
        fail(f"no embedded script found in {label}")

    js_path = ROOT / f".release-check-{label}.js"
    js_path.write_text("\n".join(scripts), encoding="utf-8")
    try:
        subprocess.run(["node", "--check", str(js_path)], check=True, capture_output=True, text=True)
    except FileNotFoundError:
        fail("node is required for JS syntax validation")
    except subprocess.CalledProcessError as exc:
        fail(f"JS syntax validation failed in {label}:\n{exc.stderr}")
    finally:
        js_path.unlink(missing_ok=True)


def is_four_word_name(path: Path) -> bool:
    return len(path.stem.split("-")) == 4


def validate_topic_spaces() -> int:
    if not TOPIC_ROOT.exists():
        fail("missing modular topic root")
    if not is_four_word_name(TOPIC_ROOT):
        fail("topic root name must be four words")
    if not TOPIC_INDEX.exists():
        fail("missing topic-space-index-file.json")
    if not is_four_word_name(TOPIC_INDEX):
        fail("topic index file name must be four words")

    try:
        index = json.loads(TOPIC_INDEX.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"topic index JSON is invalid: {exc}")

    if len(index) < 2:
        fail("too few modular topic spaces")

    for item in index:
        folder = TOPIC_ROOT / item["folder"]
        source = folder / TOPIC_SOURCE_NAME
        page = folder / TOPIC_PAGE_NAME
        for path in [folder, source, page]:
            if not path.exists():
                fail(f"missing topic path: {path.relative_to(ROOT)}")
            if not is_four_word_name(path):
                fail(f"topic path is not four words: {path.relative_to(ROOT)}")

        page_html = page.read_text(encoding="utf-8")
        try:
            Parser().feed(page_html)
        except Exception as exc:
            fail(f"HTML parser rejected topic page {page.name}: {exc}")
        validate_embedded_scripts(page_html, folder.name)

    return len(index)


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

    validate_embedded_scripts(html, "main")

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

    topic_count = validate_topic_spaces()

    print("release-check-ok")
    print(f"sections={section_count}")
    print(f"code_cards={code_count}")
    print(f"knowledge_links={knowledge_count}")
    print(f"visual_cards={visual_count}")
    print(f"dream_labs={dream_lab_count}")
    print(f"senior_cuts={senior_cut_count}")
    print(f"topic_spaces={topic_count}")
    print(f"html_bytes={len(html)}")


if __name__ == "__main__":
    main()
