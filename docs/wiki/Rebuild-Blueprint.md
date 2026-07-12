# Rebuild Blueprint — the house plans for Sentinel Forge

> **Purpose:** disaster-recovery seed file. If every line of code were
> lost, this document + `Database-Schema.md` + the README is enough to
> reconstruct the product. Everything below is **pseudocode and
> blueprint** — not runnable, deliberately language-portable. It would
> all have to be recoded — but recoded in *days instead of months*,
> because the decisions are already made and written down.
> Maintained by the assistant; checked during README reviews.

_Blueprint drawn 2026-07-11 from the as-built structure (commit
`33f16f71`, 172 tests green)._

---

## 1. The lot and square footage (what you're building)

| Measure | As built |
| --- | --- |
| Shell | ONE Python/Tkinter file, ~24,000 lines (`sentinel_personal_development.py`) |
| Functional core | `lyceum/` package, ~20 modules, zero Tkinter imports |
| Foundation | One SQLite file, ~40 tables, additive-only migrations |
| Tests | 172, all headless (temp DBs, injectable clocks) |
| Data on disk | `Books/` folder of .md excerpts + `.meta.json` sidecars; `HANDOFF_STATE.json` |
| Utilities | Ollama (llama3.2:3b) via loopback; Piper TTS binaries in `tts/`; faster-whisper |
| Bill of materials | faster-whisper, sounddevice, numpy, noisereduce, python-docx, pypdf, beautifulsoup4, send2trash, tkinterdnd2, openpyxl, fsrs |

**The prime directive of the lot:** local-first. No cloud APIs, no
keys. Files never leave the laptop; "delete" always means "move to
archive."

## 2. The foundation (pour this first)

SQLite + one atomic primitive. Everything stands on it.

```pseudocode
module study_db:
    STUDY_DB = local_appdata / "study.db"       # live DB is LOCAL,
    snapshot_to_onedrive_on_init()              # backup is synced

    function connect():
        con = sqlite.connect(STUDY_DB)
        con.execute("PRAGMA foreign_keys = ON")
        return con

    contextmanager transaction():
        con = connect()
        with con:            # commit on success, ROLLBACK on exception
            yield con
        con.close()

    function init_schema():
        executescript(SCHEMA)   # every statement CREATE ... IF NOT EXISTS
        # additive-only law: never ALTER existing columns; new features
        # get new tables. Old databases must upgrade in place, silently.
```

**Inspection rule:** any multi-statement write MUST go through
`transaction()`. The FSRS review loop is the reference example (§6).

## 3. The load-bearing wall (do not cut into it)

**Functional core / imperative shell.** One wall separates the house:

```pseudocode
lyceum/          # THE CORE: pure logic, no UI imports, no wall-clock
    every function that touches "now" takes now: datetime = None
    every module unit-testable headless
shell (one file) # THE SHELL: Tkinter windows, buttons, threads
    reads/writes ONLY through core functions
    owns all widgets, all event bindings, all after() scheduling
```

Everything hard that ever happened in this house happened when
something leaned on this wall wrong (UI-thread file I/O, swallowed
exceptions). Rebuild rule: **write the core module + its tests before
its window.**

## 4. The electrical system (threading — how power moves)

```pseudocode
MAIN THREAD: owns Tk. mainloop() runs always. NEVER blocks on I/O.

WORKER PATTERN (the only approved circuit):
    on user action:
        capture inputs from widgets            # main thread
        Thread(target=work, daemon=True).start()
    function work():                           # background
        result = slow_thing()                  # model call, file move, TTS
        root.after(0, deliver, result)         # ONLY way back to the UI
    function deliver(result):                  # main thread again
        update widgets, refresh lists, set status

FUSES (lessons paid for):
    - after() from a worker silently dies without a running mainloop
      → all headless tests must run a real mainloop
    - never call winfo_children() on a possibly-dead widget unguarded
    - bare `except: pass` around a feature = a fuse that hides fires;
      every failure must surface somewhere visible
```

## 5. The plumbing (how data flows through the house)

```pseudocode
READING PIPE:  book file → parser (docx/pdf/md/txt/rtf/html, each
               try/except-optional) → text_area → highlight tags

EXCERPT PIPE:  selection → .md with YAML front-matter
               {doc_id, zone GREEN/YELLOW/RED, cognitive_load 1-10,
                source_book, timestamp, tags[]}
               + sidecar <file>.md.meta.json → Books/ (OneDrive-synced)

CONTEXT PIPE (feeds the small local model — the model never touches
network or disk itself):
    retrieval: score(text, query_terms) → rank docs → top passages
               capped ~6000 chars   # lyceum/local_context pattern
    sources:   library index (cached by path+mtime) | OneDrive index
               (same, repo-dirs pruned) | attachment | web search
               (DuckDuckGo lite, stdlib urllib)
    combined context string → ollama.chat(system + context, num_ctx=2048)
               # num_ctx pinned: default 128K tries to allocate ~15 GB

SESSION PIPE:  start goal/notes → HANDOFF_STATE.json → next-session
               roundup   # the cross-session memory loop

VOICE PIPES:   mic: sounddevice 16k mono → faster-whisper (Fast/
               Accurate/Best = base/small/medium.en) → target widget
               tts: text → normalize_for_speech() → piper.exe → wav →
               winsound.PlaySound (SYNC; stop = SND_PURGE)
               # NOT pyaudio — PortAudio dies on this hardware
```

## 6. The rooms (one per feature wing; rebuild in this order)

**Room 1 — the Reader (living room).** Big text area, sentence/word/
paragraph highlighting with 8 colors, font/size controls persisted.
Everything else attaches to this room.

**Room 2 — the Library (study).** Scan `Books/` recursively (skip
`Commentaries/`), Treeview list + in-window reading pane with
chapters/synthetic pages (~1800 chars). Row height FROM FONT METRICS.
Buttons: `+ Add files…` and the study-hub tab jumps. Remove = archive
move, background thread.

**Room 3 — the Study workspace.** Tabs: Study Notes, AI Chat, Topics,
Glossary, Commentary, Journal, Matrix (4 quadrants + checkbox lines),
Planner (week columns). All autosaving (debounced or on-switch).

**Room 4 — the Dashboard (front hall).** MDP marquee, Scoreboard
(3 lead-measure cards + marks-by-day + streaks), Idea Warehouse,
Focus Mode, Not-To-Do + hosts-file site blocker, Session Start panel.

**Room 5 — the Money wing.** ~15 calculators sharing two laws:
education-only (never execute trades) and **numbers need a picture**
(every figure gets a gauge/meter/translation). Tables: pay-first
balance, expenses, buckets, wishlist(+cooldown timestamps), holdings.

**Room 6 — the Memory room (FSRS).** The reference core module:

```pseudocode
class SRSService(db):
    scheduler = FSRS(enable_fuzzing=False)     # determinism law
    add_card(deck, front, back, source_ref):
        reject duplicate (source_kind, source_ref)   # unique index
        store fsrs_card_json (AUTHORITATIVE) + denormalized due/state
    review_card(card_id, rating 1..4, now):
        ONE transaction:
            card = from_json; card, log = scheduler.review(card, rating, now)
            UPDATE card json + due/state/reps/lapses
            INSERT append-only review_log row      # optimizer's food
    get_due_cards(now):  due <= now, unsuspended, oldest first, LIMIT small
    sync_from_glossary(rows): idempotent import, skip existing
    resync(): rebuild denormalized cols from json  # json always wins
window: front → "Show answer" → rate 1-4 → honest "comes back in N days"
```

**Room 7 — the AI room.** Chat with context sources (§5 pipe),
📎 attach, 📄 draft-document flow (model text → parse table → real
.xlsx with =SUM() / .docx paragraphs; refusal-guarded system prompts).

**Room 8 — the floating toolbar (hallway lighting).** Dockable bar:
quality picker, 🎤 voice, 🔊 read + scope/color/speed, ➕/➖ context-
routed add/remove, ❓ step-flash tour, dock menu of open windows;
host-destroy rescue re-docks to main.

## 7. The roof (UI laws that keep the weather out)

```pseudocode
size every window:  w = min(design_w, screen_w - margin)  # ~1097×617 usable
row heights:        from font.metrics("linespace") * 1.5+, never fixed px
one primary action per screen; <= 5 major choices
tuple pady ONLY in .pack()/.grid(), NEVER widget constructors
every save/action → visible confirmation (invisible success = bug)
reading surfaces honor user font (OpenDyslexic first)
palette: BG_DARK #0f172a, BG_PANEL #1e293b, BG_INPUT #0b1220,
         accents green/red/amber/cyan/purple/slate (see constants)
```

## 8. Construction schedule (the rebuild order, with acceptance gates)

```pseudocode
PHASE 0  foundation: study_db + transaction + schema     GATE: atomicity tests
PHASE 1  Reader room + fonts + highlighting              GATE: open/read/highlight
PHASE 2  Library + excerpt pipe + archive workflow       GATE: save/scan/archive tests
PHASE 3  Study tabs + autosave                           GATE: notes survive restart
PHASE 4  Dashboard + Scoreboard + Focus                  GATE: streak math tests
PHASE 5  Voice (whisper in, piper/winsound out, speed)   GATE: on-hardware audio check
PHASE 6  Money wing                                      GATE: finance kernel tests
PHASE 7  AI room + context pipes + doc writer            GATE: end-to-end model answer
PHASE 8  FSRS room                                       GATE: the 10 spec tests (RELAY-SRS-001 §5)
PHASE 9  toolbar + tour + polish                         GATE: full suite green + wiki current
EVERY PHASE: core module + tests FIRST, window second; commit; mirror 3 ways.
```

## 9. Replacement-cost note (why this document exists)

From bare ground with only this blueprint + `Database-Schema.md` +
the README: estimated **8–12 focused sessions** to functional parity,
because every architectural decision, every trap, and every acceptance
gate is pre-answered here. Without it: months, and the traps get paid
for twice. This is the cheapest insurance in the repo — keep it
current when rooms are added.

---

## 10. The floating-toolbar control cluster (the "safe spot")

The floating toolbar is the ONE fixed command locus — same controls, same
colors, same place, docked or floating, in every panel. Intent:
zero-instruction recognition for a visual/tactile, ADHD/dyslexia learner by
borrowing universal real-world signal grammar.

```pseudocode
build_floating_toolbar(body):
    ... mic / read / voice / speed / format-preset pickers ...

    # ── A− / A+  as ROAD-MARKER signs = ONE black/white toggle ──
    make_font_marker(parent, text, dir):
        canvas 52x40, bg = panel
        plate  = rounded_rect(canvas, inset, r=9, fill=white, outline=black, w=2)
        letter = canvas_text(center, text, big bold, fill=black)
        on click: study_font_step(dir); set_font_toggle(dir<0 ? "dec" : "inc")
        return (canvas, plate, letter)
    dec = make_font_marker(body, "A-", -1);  inc = make_font_marker(body, "A+", +1)
    set_font_toggle(active):                 # ONE always white, ONE always black
        paint(active_marker, fill=white, ink=black)   # last-pressed = white
        paint(other_marker,  fill=black, ink=white)
        persist active                       # survives dock/undock rebuild

    # ── Traffic light: the WORD sits ABOVE a colored lamp ──
    signal(word, icon, lamp_color, cmd, ink=white):
        cell = frame
          label(word)              packed TOP     # names the action
          button(icon, lamp_color) packed below   # colored lamp == meaning
        return button
    signal("Add",    +,   GREEN)          -> ftb_action_add
    signal("Save",   disk, YELLOW, black) -> ftb_action_save
    signal("Delete", bin,  RED)           -> ftb_action_remove

    # ── Universal, context-dispatched actions (identical in every panel) ──
    ftb_action_add:    try each panel's add-from-toolbar; else click an
                       "add/new/create/upload" button in the active context
    ftb_action_save:   journal? save entry. notes? save. else click the active
                       panel/dialog's "Save" button; else fire Ctrl+S
    ftb_action_remove: try each panel's remove-from-toolbar; else click a
                       "delete/remove/clear" button; ALWAYS confirm first
```

**Design laws carried here:** color == meaning (green go / yellow hold /
red stop); the word sits ABOVE the color so it reads without training;
A−/A+ keep one marker white and one black at all times, so "which way did I
size it?" is answerable at a glance. Text-size + Format presets touch the
READING panes only, never the navigation lists (that scaling bug is fixed
and lint-gated). The three actions are one context-dispatch each, so the
cluster behaves the same everywhere it appears.
