# Sentinel Forge Library

This folder doubles as a **Sentinel Forge library** and an **Obsidian vault**.
Every file Sentinel Forge saves carries YAML front-matter that Obsidian's
Dataview plugin can query directly.

## Schema

```yaml
---
doc_id: BOOKREADER-EXCERPT-<source>_<YYYY-MM-DDTHH-MM-SS>_v001
zone: GREEN | YELLOW | RED
cognitive_load: 1-10
source_book: <full path to the source book>
timestamp: 2026-05-21T18:48:54
selection: true | false
word_count: <int>
tags: []
---
```

## Useful Dataview queries

Install the Dataview community plugin (Settings → Community plugins → Browse → "Dataview"). Then paste any of these into a note.

### All GREEN-zone excerpts saved this week

````
```dataview
table file.ctime as Saved, source_book, word_count
where zone = "GREEN" and file.ctime >= date(today) - dur(7 days)
sort file.ctime desc
```
````

### Excerpts grouped by source book

````
```dataview
table without id
  source_book as "Source",
  length(rows.file.link) as "Saves"
from "."
where source_book
group by source_book
sort length(rows.file.link) desc
```
````

### Cognitive-load heatmap

````
```dataview
table cognitive_load, zone, source_book, file.ctime as Saved
sort cognitive_load desc, file.ctime desc
```
````

## Workflow notes

- The Sentinel Forge app's **Three-Zone Library** filter and Obsidian's Dataview queries read the same source of truth.
- The `tags` field in the front-matter is yours — add anything, Dataview can group on them.
- Deleting a file in Obsidian leaves its `.meta.json` sidecar behind unless you delete that too. Sentinel Forge's 🗑 Remove button cleans both at once.
- To hide `.meta.json` files in Obsidian's file pane: Settings → Files → uncheck "Detect all file extensions."
