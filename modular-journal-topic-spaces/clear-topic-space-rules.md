# Clear Topic Space Rules

This folder is the modular layer of the journal.

Each topic gets its own room.

Each room keeps the idea separate.

The main journal links to the room.

The same render engine builds the room.

## Naming Rule

Every new folder name must have four plain words.

Every new file name must have four plain words.

Use lower case words.

Use hyphens between words.

Good:

```text
future-firewall-decision-layer
core-topic-source-file.md
built-topic-page-file.html
```

Avoid:

```text
firewall
topic.md
agi_agent_firewall_notes.md
```

## Source Rule

Write the topic in:

```text
core-topic-source-file.md
```

Do not hand edit:

```text
built-topic-page-file.html
```

The generator owns the HTML file.

## Render Rule

Run:

```bash
python3 build_journal_html.py
```

The generator will:

```text
read each topic source file
build each topic page file
build the topic index file
add the topic shelf to the main journal
reuse the same CSS and JavaScript
```

## Writing Rule

Use old school English.

Use short sentences.

Use simple words.

Explain the thing as a working system.

Show:

```text
what enters
what is checked
what changes
what is allowed
what is denied
what happens next
```

## Growth Rule

Add a topic folder when the idea deserves its own mental space.

Keep small edits in the main journal.

Move recurring ideas into topic rooms.

