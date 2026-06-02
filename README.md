# Thinking in Code

**A future-facing interactive programming journal about silicon, code, control systems, and AI-native software.**

Thinking in Code is built for young learners, self-taught builders, and engineers who want programming to feel connected instead of fragmented. It starts from the machine: signals, `0` and `1`, memory, control systems, feedback, code, production systems, and AI agents.

The published artifact is a single self-contained HTML file:

- no external JavaScript dependencies
- no external CSS dependencies
- full journal source embedded
- interactive sidebar
- reading progress
- search
- recall score
- MCQs
- active recall prompts
- hard transfer tests
- Past -> Present -> Future knowledge links
- export/import of learning progress
- print mode

## Open The Journal

Open `index.html` in any modern browser.

## Files

- `index.html` — the release artifact
- `journal.md` — the source journal
- `build_journal_html.py` — generator for the self-contained HTML
- `release_check.py` — validation script for release readiness

## Rebuild

```bash
python3 build_journal_html.py
python3 release_check.py
```

## Release Status

This is a **v0.1 Foundations Preview**. The system is release-ready as a self-contained learning artifact. The journal content is a living work that will expand entry by entry.

## Authors

Anurag Atulya + Codex + Eight

Eight is Anurag's personal AI companion and collaborator.
