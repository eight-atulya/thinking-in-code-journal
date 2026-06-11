---
name: thinking-in-code-journal-companion
description: Maintain, expand, validate, publish, or recreate the Thinking in Code interactive programming journal as a self-contained GitHub Pages site, including content edits, UI/UX work, learning checks, pitch pages, release validation, and public cache verification.
---

# Thinking In Code Journal Companion

Use this skill whenever a user wants to build something like this journal, edit this journal, add a feature, fix the UI, add a page such as a pitch deck, or publish the GitHub Pages artifact.

The job is not only to change files. The job is to preserve a learning product: a readable, interactive, mobile-safe journal that helps a beginner understand code as flow, state, checks, branches, feedback, and production reality.

## Mental Model

Think of this project as four connected layers:

```text
journal.md -> build_journal_html.py -> index.html -> GitHub Pages
```

Each layer has one job:

```text
journal.md              = source manuscript and learning content
build_journal_html.py   = renderer, CSS, JS, UI behavior, quizzes, learning checks
index.html              = generated published artifact
release_check.py        = release guard that catches broken promises
if-may-pitch.html       = standalone pitch page linked from the journal
programing-language.md  = local editor copy synced from journal.md when present
modular-journal-topic-spaces = four-word topic rooms built by the same renderer
.nojekyll               = tells GitHub Pages to serve static files plainly
```

Rule: do not hand-edit `index.html` for durable changes. Edit `journal.md` or `build_journal_html.py`, rebuild, then validate.

## First Decision

Before changing anything, decide which route applies:

```text
Route A: edit words/content        -> journal.md
Route B: add a new lesson/entry    -> journal.md + build_journal_html.py quizzes/prompts if needed
Route C: change layout/UI/UX       -> build_journal_html.py CSS/HTML/JS, then rebuild index.html
Route D: add a standalone page     -> add the .html file + link from build_journal_html.py
Route E: change release promises   -> release_check.py
Route F: validate                  -> rebuild, sync editor copy, run release and syntax checks
Route G: publish                   -> commit, push, verify raw or Pages URL
Route H: create a new journal      -> copy the architecture, then customize content, renderer, checks, and Pages config
Route I: add modular topic space   -> add a four-word topic folder with one source file, then rebuild generated pages
```

If the request says "fix the website" or "phone view is broken," inspect the rendered HTML/CSS and test with a browser-sized check before editing.

## Route A: Edit Existing Content

1. Search the manuscript:

```bash
rg -n "phrase or heading" journal.md
```

2. Edit `journal.md` at the smallest correct location.
3. Preserve Anurag's operational voice: entry point, first checks, inputs, scheduled work, state changes, `if/else`, retries, exits, waits.
4. Avoid polishing concrete understanding into abstract slogans.
5. Rebuild and validate with the standard commands below.

When the user says "put it above/below this quote," edit that exact local spot. Do not move the idea into a disconnected note.

## Route B: Add A New Entry

Use this structure for major learning entries:

```markdown
## Entry X: Clear Title

### Dream Lab
**The dream:** ...
**The pressure:** ...
**The unlock:** ...
**Do this now:** ...

### Senior Cut
Direct production explanation.

**Decision rule:** ...

### Cold Open
Concrete situation.

### What You Unlock
Specific capabilities.

### Knowledge Link
| Past | Present | Future |
|---|---|---|
| ... | ... | ... |

### Tiny Model
Diagram or execution flow.

### First Action / Make It Real
Small concrete build step.

### Debugging Smell
What failure looks like.

### Memory Lock
Durable bullets.

### Boss Fight
Transfer challenge.

### AI Collaboration
Prompt that helps without replacing thinking.

### Future Connection
How this scales into AI-native or production work.
```

Every serious entry should give the learner:

```text
definition -> consequence -> failure mode -> practical rule -> tiny action -> memory lock -> transfer test
```

If the new entry introduces a major concept, also update the quiz/prompt logic in `build_journal_html.py`:

```text
quizBank or precisionQuizBank
recallPrompt precisionPrompts
hardPrompt precisionPrompts
```

Then update `release_check.py` only when the new structure must never regress.

## Route C: Change UI Or UX

All durable UI lives in `build_journal_html.py`.

Common UI surfaces:

```text
sidebar/nav/search/buttons      -> CSS near sidebar rules + sidebar HTML
hero                            -> hero CSS + header markup
entry cards                     -> .entry-section, .entry-inner, section-toggle
code blocks and copy buttons    -> code-card renderer + .code-card CSS
Brain Check                     -> buildLearningChecks() + .learning-check CSS
quizzes and scoring             -> quizBank, precisionQuizBank, updateScore()
mobile menu                     -> @media (max-width: 900px) + mobileMenuToggle JS
print behavior                  -> @media print
```

UI quality rules:

1. Test at phone width and desktop width.
2. No horizontal overflow.
3. No text collision inside buttons, chips, cards, or nav rows.
4. Large touch targets on mobile.
5. Use hierarchy through spacing, type, subtle fills, and alignment. Avoid noisy borders when the user dislikes them.
6. Do not create nested cards or card-heavy decoration.
7. Keep controls stable: dynamic text must not resize the layout badly.
8. If a chip or label can vary in length, use `auto minmax(0, 1fr)`, `white-space: nowrap`, and measured gaps.

For left navigation specifically:

```text
tocData is generated from headings in journal.md
toc.innerHTML renders the visible nav
.toc-link, .toc-kicker, .toc-title control hierarchy
IntersectionObserver updates active links
```

If a nav chip overflows, the usual root cause is a fixed grid column that is too narrow. Prefer content-sized columns:

```css
grid-template-columns: auto minmax(0, 1fr);
```

## Route D: Add A Standalone Page

Use this route for pitch pages, demos, diagrams, or extra artifacts.

1. Add the standalone file beside `index.html`, for example:

```text
if-may-pitch.html
```

2. Link to it from `build_journal_html.py`, not directly in `index.html`.
3. Use a normal relative link so GitHub Pages serves it:

```html
<a href="if-may-pitch.html" target="_blank" rel="noopener">Pitch</a>
```

4. If replacing an existing nav action, remove dead JS and hidden inputs too.
5. Update `release_check.py` if the new link/page is a release promise.
6. Validate both `index.html` and the standalone page parse.

## Route E: Update Release Checks

Use `release_check.py` to lock in important promises:

```text
required controls exist
new page links exist
important CSS hooks exist
content sections render
code cards render
knowledge links render
visual cards render
embedded JS parses
artifact is not suspiciously small
```

When a feature becomes part of the product, add a small required snippet. Do not add overly fragile checks for incidental wording unless the user explicitly needs that wording protected.

## Route I: Add Modular Topic Space

Use this route when an idea deserves its own mental room but should still use the same journal renderer, search, copy buttons, source dialog, and validation system.

Every new modular folder and file must have four plain words:

```text
future-firewall-decision-layer
agentic-loops-control-cycle
core-topic-source-file.md
built-topic-page-file.html
topic-space-index-file.json
```

Write only the source file by hand:

```text
modular-journal-topic-spaces/<four-word-topic-folder>/core-topic-source-file.md
```

Do not hand-edit:

```text
modular-journal-topic-spaces/<four-word-topic-folder>/built-topic-page-file.html
```

The generator builds the topic page, updates `topic-space-index-file.json`, and adds the linked topic shelf to the main `index.html`.

Topic prose should use old school English:

```text
short sentences
plain words
clear checks
clear state
clear allow / deny logic
clear next action
```

After adding a topic, run the Route F validation commands.

## Route F: Validate

Run these after content, UI, quiz, release-check, or standalone-page changes:

```bash
python3 build_journal_html.py
cp journal.md programing-language.md
python3 release_check.py
python3 -m py_compile build_journal_html.py release_check.py
```

If `programing-language.md` is absent in a new clone, skip the copy or create the editor copy intentionally.

Validate embedded JavaScript:

```bash
node - <<'NODE'
const fs = require('fs');
const html = fs.readFileSync('index.html', 'utf8');
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
for (const script of scripts) new Function(script);
console.log('script-syntax-ok', scripts.length);
NODE
```

Validate standalone pages parse:

```bash
python3 - <<'PY'
from html.parser import HTMLParser
from pathlib import Path
for name in ["index.html", "if-may-pitch.html"]:
    if Path(name).exists():
        HTMLParser().feed(Path(name).read_text(encoding="utf-8"))
        print("html-parse-ok", name)
PY
```

For UI work, use browser geometry checks when possible. Minimum checks:

```text
desktop width around 1280px
phone width around 390px
narrow phone width around 320px for nav/chips/buttons
documentElement.scrollWidth <= clientWidth
important buttons/chips have no text overflow
```

## Route G: Publish

Before publishing:

```bash
git status --short --branch
git diff --stat
```

Stage only in-scope files. Common examples:

```bash
git add journal.md programing-language.md build_journal_html.py index.html release_check.py SKILL.md
git add if-may-pitch.html
git commit -m "<clear message>"
git push origin main
```

After pushing, verify:

```bash
git status --short --branch
git rev-parse --short HEAD
```

Check raw GitHub first when Pages may be stale:

```bash
curl -L --max-time 20 -s "https://raw.githubusercontent.com/eight-atulya/thinking-in-code-journal/main/index.html" | rg "Expected new phrase"
```

Then check GitHub Pages with cache busting:

```bash
curl -L --max-time 20 -s "https://eight-atulya.github.io/thinking-in-code-journal/?v=<commit>" | rg "Expected new phrase"
```

For standalone pages:

```bash
curl -L --max-time 20 -s "https://eight-atulya.github.io/thinking-in-code-journal/if-may-pitch.html?v=<commit>" | rg "Expected pitch phrase"
```

GitHub Pages can serve old content for several minutes. A pushed commit can be correct while the public edge cache is still catching up.

## Route H: Start A New Journal From This Pattern

For a new repo or new learner journal:

1. Create the source manuscript:

```text
journal.md
```

2. Create the renderer:

```text
build_journal_html.py
```

Minimum renderer responsibilities:

```text
read journal.md
parse markdown headings, paragraphs, lists, tables, code fences
generate a table of contents
render sections/cards
emit one self-contained index.html
embed CSS and JS
embed raw markdown only if Source view is wanted
add copy buttons for code blocks
add mobile menu behavior
add print CSS
```

3. Create the release guard:

```text
release_check.py
```

Minimum release checks:

```text
index.html exists
journal.md exists
HTML parser accepts artifact
embedded JS syntax is valid
key controls exist
section count is plausible
artifact is larger than source when expected
no accidental missing learning blocks
```

4. Add GitHub Pages basics:

```text
index.html
.nojekyll
```

5. Configure Pages:

```text
Repository -> Settings -> Pages
Source: Deploy from a branch
Branch: main
Folder: / (root)
```

6. First publish loop:

```bash
python3 build_journal_html.py
python3 release_check.py
git add .
git commit -m "Publish first journal"
git push origin main
```

## Debugging Map

Use symptoms to find the layer:

```text
Words wrong                         -> journal.md
Generated HTML missing new content   -> rebuild did not run or wrong file edited
Public site old after push           -> GitHub Pages cache; check raw GitHub
Button exists but does nothing       -> JS listener id mismatch
Release check fails missing snippet  -> feature renamed; update check intentionally
Phone has sideways scroll            -> CSS width, fixed grid column, long text, pre/table overflow
Chip text overlaps title             -> fixed chip column too small; use auto minmax(0, 1fr)
Copy button misaligned               -> code-card header layout; inspect .code-card-head
Brain Check broken on mobile         -> summary/check-body grid/flex rules
TOC confusing                        -> nav hierarchy, level labels, spacing, active state
Standalone page 404                  -> file not committed or wrong relative link
```

## Voice Rules

The user's preferred explanation style is concrete and execution-first.

Prefer:

```text
where does it start?
what gets checked first?
what input enters?
what state changes?
what task gets scheduled?
what happens in the if branch?
what happens in the else branch?
what can fail?
how do we verify reality?
```

Avoid:

```text
vague inspiration
long poetic buildup
abstract claims without operational consequence
generic AI enthusiasm
```

## Release Quality Bar

Do not call the task done until:

1. Source file is edited, not only generated artifact.
2. `index.html` is regenerated.
3. `release_check.py` passes.
4. Embedded JS syntax passes.
5. Python files compile.
6. `journal.md` and `programing-language.md` are synced when both exist.
7. UI changes have a phone and desktop sanity check.
8. Public or raw GitHub verification is reported when publishing.
9. Git worktree state is clean after publish, unless explicitly left dirty.

## Useful URLs

```text
Main site:
https://eight-atulya.github.io/thinking-in-code-journal/

Cache-busted main site:
https://eight-atulya.github.io/thinking-in-code-journal/?v=<commit>

Pitch page:
https://eight-atulya.github.io/thinking-in-code-journal/if-may-pitch.html

Cache-busted pitch page:
https://eight-atulya.github.io/thinking-in-code-journal/if-may-pitch.html?v=<commit>
```
