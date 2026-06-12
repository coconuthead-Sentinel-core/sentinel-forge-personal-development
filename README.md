# Sentinel Screen Reader

> **A native Windows desktop reading app for `.docx`, `.pdf`, `.md`,
> `.txt`, `.rtf`, and `.html` — with neural read-aloud, highlight-by-sentence,
> voice dictation, a zone-tagged Library, and a focus & study dashboard.**

![Status](https://img.shields.io/badge/status-MVP-success)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Platform: Windows](https://img.shields.io/badge/platform-Windows-0078d4.svg)

---

## What it does

- **Open** any book (`.docx`, `.pdf`, `.md`, `.txt`, `.rtf`, `.html`) and
  read it in a big, readable single-window UI
- **Read aloud** with the bundled **Piper neural voice** (offline,
  high-quality) or fall back to Windows SAPI5
- **Highlight by sentence, word, or paragraph** with 8 colour swatches
- **Save excerpts** — click Save, the selected (or whole) passage is
  written as a `.md` with YAML front-matter recording zone, cognitive
  load, source book, and timestamp
- **Library with in-window reading view** — pick a book and read it in
  place with chapter / page navigation. Saved excerpts are tagged with a
  **GREEN / YELLOW / RED** zone (recorded in their front-matter), and the
  Library can filter by zone
- **Timed focus blocks** — distraction-free **Focus Mode** with 60 / 90-minute
  work blocks (see the dashboard section below)
- **Session continuity** — start / end of session is written to
  `HANDOFF_STATE.json` so the next session knows where you left off
- **Cross-excerpt AI search (✨ Ask Library)** — if the optional
  [Sentinel Forge platform](https://github.com/coconuthead-Sentinel-core/Sentinel-of-sentinel-s-Forge)
  is running on localhost, the in-app Ask Library button scores every
  excerpt against your question and surfaces matches with snippets

## Study workspace & dashboard

Beyond reading, the app is a study and focus workstation:

- **⭐ Major Definite Purpose banner** — a permanent North Star pinned to the
  very top of the dashboard. Your one burning goal (e.g. *"Earn my Computer
  Science Degree by 2028"*) stares back at you whatever you're doing — schedule,
  bills, reading — because Hill and Tracy found that one organizing goal is what
  separates the achievers. Click it to edit; it persists across sessions.
- **🧭 V2MOM "Why" Engine** — knowing *why* beats knowing *how* (Sinek, Robbins).
  Every major goal is captured through the V2MOM intake — **Vision, Values
  (your Why), Methods, Obstacles, Measurement** — and the app **won't let you
  save** until you've written your **Why** and named the **Obstacles** in the
  way. Goals you can't justify don't get made.
- **✍ Daily 10 Goals (spiral notebook)** — Brian Tracy's exercise: each morning
  the app gives you a **blank, numbered list** and you rewrite your top 10 goals
  **from memory, in the present tense** (*"I earn $80,000 as a software
  engineer."*). Writing them daily programs them into the subconscious; a
  🔥 **day-streak** rewards the habit, and it nudges you each morning until it's
  done. (Blank each day on purpose — recalling them is the point.)
- **Study tabs** — autosaving **Study Notes**, **Topics**, **Glossary**,
  dated **Journal**, a four-quadrant **Eisenhower Matrix**, and a
  Sunsama-style weekly **Planner** — each with 🎤 dictation and 🔊
  read-aloud.
- **🎤 Voice dictation (Whisper)** — on-device, offline speech-to-text
  with a Fast / Accurate / Best accuracy selector.
- **🚀 Performance dashboard** (4DX + Ziglar): a **🏆 Compelling
  Scoreboard** of daily lead measures with streaks, a **🧠 Idea
  Warehouse** (ABCDE priorities, Big-Three, schedule-to-planner,
  implementation intentions), **🎯 Focus Mode** with timed focus blocks,
  a **🚫 Not-To-Do list + website blocker**, **☸ Wheel of Life** and
  **🎯 Goals**, and **🧭 Weekly Roles**.
- **⏱ Winner's Time Log (time auditor)** — a low-friction chime every
  60 or 90 minutes asks "what did you work on for the last hour?"; one tap
  files it, and the dashboard draws a **weekly pie chart** of where your
  time actually went (A-1 task, studying, distracted, …). Toggle it on/off
  and pick the interval from the ⏱ Time Log window. In Ziglar's words,
  knowing where your minutes go is a *freeing* factor, not a limiting one.
- **🪞 After-Action Review (daily reflection)** — Brian Tracy's end-of-day
  questions, *"What did I do right?"* and *"What would I do differently next
  time?"*, plus an optional 1–5 day rating. One reflection per day, with a
  list of past days so the week can be reviewed (James Clear). A gentle
  evening nudge reminds you if today's is still blank. *Experience alone
  doesn't make you better — evaluated experience does.*
- **🚀 5-4-3-2-1 Momentum button** — Mel Robbins' 5-Second Rule + Tracy's
  *"Do it now!"*: when starting feels impossible, hit it and the screen
  counts down **5 – 4 – 3 – 2 – 1 – GO!** with a beat per second, then drops
  you straight into **Focus Mode** on your #1 task — the activation energy to
  *move* before your brain talks you out of it.
- **💰 Pay Yourself First** — Clason's first law of wealth: *a part of all you
  earn is yours to keep.* Enter a paycheck and the app deducts your savings
  **first** (10%, or start at 1% if money's tight), **locks** it into a
  Financial Independence balance you can't budget away, and only lets you
  allocate the **spendable remainder** across rent, gas, food, etc. — it
  refuses any budget line that would dip into your savings.
- **🛡 Core Four (Defense Mode)** — when money's tight, strip the budget down
  to the four survival numbers: **Rent · Utilities · Food · Transportation**.
  A bold 2×2 grid checks them against the cash you have — each box turns
  **green when secured, red when not covered** — and tells you if you're short
  and by how much, so your most basic needs get covered *first*. Can pull the
  spendable figure straight from your latest paycheck.
- **☕ Latte Factor (expense auditor)** — the small daily leaks sink the ship.
  Fast-entry (one-tap chips for coffee, snacks, subscriptions, or any custom
  amount) logs every little purchase, and the weekly total projects it out to
  the **month and year** — showing what slipped through and what it could have
  funded in a Dream Bucket instead.
- **🪣 Dream Buckets (target funder)** — save cash for the big things (fridge,
  washer, dryer, car) so you never need debt. Each bucket has a **visual
  progress bar** that fills as you transfer in money you saved by skipping a
  purchase (one-tap +$5/+$10/+$20), with a 🎉 reward — instant dopamine for an
  ADHD brain. Add your own buckets, set targets, and drop in a picture of the
  exact thing you want.
- **⏳ Wishlist (7-day purchase delay)** — fast money decisions are usually poor
  ones. Park anything you want-but-don't-need here and it's **locked with a 7-
  or 30-day countdown** — you literally can't mark it "bought" until the timer
  hits zero. By then the urge has usually cooled and you **let it go** (one tap),
  which tallies the **money kept**. Buying stays disabled while it's cooling.
- **🔋 Run Rate (emergency-fund meter)** — how many months you could survive if
  income stopped today: cash savings ÷ your Core Four monthly expenses. A
  **battery meter** shows the charge (*"You have exactly 1.5 months of survival
  fuel"*) with a marked 3-month safe line, and one tap sets an automatic
  **3-month Emergency Fund goal** as a Dream Bucket. Pulls expenses from Core
  Four and cash from your Pay-First balance.
- **⌛ Time Cost (time vs. money translator)** — a price isn't dollars, it's the
  hours of life you traded to earn it. Type a price and your after-tax wage and
  it flashes the real cost: *"This costs 6.5 hours of your life working at The
  Brixton. Is it worth 6.5 hours of your life?"* — an instant cure for impulse
  buys. **Sleep on it** parks the item in your 7-day Wishlist; **Skip it** tells
  you the hours of life you just kept.
- **💵 Money Hub** — your whole financial picture in one glance: locked savings,
  run-rate months, Core Four status, this week's leaks, your nearest Dream
  Bucket, and the cooling-off Wishlist — each on a card with a one-tap jump to
  the full tool, so you don't have to open every window to check in.
- **📈 Save More Tomorrow (raise auto-escalator)** — we hate giving up money we
  have but happily commit *future* money. Sign a one-time contract and, by the
  **Wedge Theory**, **half of every future raise is swept into savings** before
  you ever feel it. Log a raise (e.g. $21→$22/hr) and it splits the increase
  50/50 — lifestyle vs. wealth — tracks your committed monthly/yearly savings,
  and can sweep it into your Financial Independence balance.
- **🌱 Compound Simulator (Rule of 72)** — compound interest is the most powerful
  force there is. Plug in a few dollars a week, a return rate, and your age, and
  a **growth graph** forecasts the fortune it becomes by retirement (e.g.
  *$20/week at 8% → ~$179,000 by 65, only $36k of it your own money*). Shows how
  often your money doubles (Rule of 72). Open it whenever you feel poor or stuck
  and *see* your future wealth — instant hope.
- **🔍 Zero-Based Audit** — every recurring charge must re-earn its place. List
  your subscriptions (Netflix, internet, phone, apps) and **every ~90 days the
  app forces an audit** that walks each one and asks, *"Knowing what you know
  now, would you sign up for this again today?"* A **No** cancels it on the spot
  and tells you the yearly drain you just cut. Shows your total monthly/yearly
  subscription burn at a glance.
- **SQLite-backed** — all of the above persists in a local database
  managed by `lyceum/db/study_db.py`.

## Why it exists

I built this for myself — a CNA → AI-systems-developer transition who
needs to read a lot of technical material while managing ADHD, dyslexia,
and dysgraphia. Every feature is there because something else got in
the way:

- Tk windows because the browser was distracting
- Big colored buttons because small targets cost attention
- Neural TTS because the standard Windows voice was draining to listen to
- Zone-tagged saves because flat dumps of highlights become noise

---

## Quick start

```powershell
# 1. Get the code
git clone https://github.com/coconuthead-Sentinel-core/Sentinel-screen-reader. sentinel-screen-reader
cd sentinel-screen-reader

# 2. Install Python deps
py -3 -m pip install -r requirements.txt

# 3. (Optional) Install the Piper neural TTS bundle (~100 MB)
#    The app will fall back to Windows SAPI5 if you skip this.
powershell -ExecutionPolicy Bypass -File scripts\install_tts.ps1

# 4. Run it
py -3 book_reader.py
```

Or double-click **`run_book_reader.bat`** for a no-console launch.

To install a Desktop shortcut:
```powershell
powershell -ExecutionPolicy Bypass -File scripts\install_book_reader_shortcut.ps1
```

---

## Requirements

| | |
|---|---|
| **OS** | Windows 10 / 11 |
| **Python** | 3.11+ (3.13 tested) — `py` launcher recommended |
| **Disk** | ~5 MB without TTS · ~105 MB with Piper voices |
| **Other** | Tk is bundled with the Python.org installer; nothing else mandatory |

### Python dependencies

| Package | Why |
|---|---|
| `faster-whisper` | on-device Whisper voice dictation (downloads its model on first use) |
| `sounddevice` · `numpy` · `noisereduce` | mic capture, audio buffers, and noise suppression for dictation |
| `python-docx` | parse `.docx` |
| `pypdf` | parse `.pdf` |
| `beautifulsoup4` | parse `.html` |
| `pyttsx3` | Windows SAPI5 fallback voice |
| `send2trash` | recoverable deletes from the Library |
| `tkinterdnd2` | drop-files-on-the-Library-window support (optional) |

All listed in [`requirements.txt`](requirements.txt). Each parser is
imported with `try/except ImportError` and the app degrades gracefully —
e.g. with no `pypdf` installed, `.pdf` open is disabled but `.docx` /
`.txt` / `.md` still work.

---

## How the saved-excerpt format works

Every excerpt is a plain Markdown file with YAML front-matter:

```yaml
---
doc_id:         BOOKREADER-EXCERPT-bushido_2026-05-22T13-04-11_v001
zone:           GREEN
cognitive_load: 8
source_book:    "C:/Users/sbrya/OneDrive/Documents/Bushido 1.docx"
timestamp:      2026-05-22T13:04:11
selection:      true
word_count:     412
tags:           []
---

# Saved 2026-05-22 13-04 — copy from Bushido 1

- Saved: 2026-05-22T13:04:11
- Source: C:/Users/sbrya/OneDrive/Documents/Bushido 1.docx
- Word count: 412

---

(... excerpt body ...)
```

A sidecar `<filename>.md.meta.json` carries the same metadata for fast
scans. Either is authoritative — the platform-side reader uses the YAML
front-matter; the desktop Library uses the sidecar.

The folder where these land defaults to
`%USERPROFILE%\OneDrive\Desktop\Books\`. Override with the
`SENTINEL_FORGE_BOOKS_DIR` env var.

---

## Layout

```
.
├── book_reader.py                 ← the entire desktop app (single file)
├── run_book_reader.bat            ← no-console launcher
├── run_book_reader_debug.bat      ← console launcher for debugging
├── requirements.txt
├── Sentinel-Forge.spec            ← PyInstaller spec for one-folder build
├── sentinel.ico                   ← app icon
├── sentinel_preview.png           ← preview image
└── scripts/
    ├── build_exe.ps1              ← one-command PyInstaller build
    ├── install_book_reader_shortcut.ps1
    ├── install_tts.ps1            ← downloads Piper + en_US-amy voice
    ├── make_sentinel_icon.py      ← regenerates sentinel.ico
    └── sentinel-library-readme.md ← drop-in README for the Books vault
```

---

## Build a standalone `.exe`

Verified build, one command:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\build_exe.ps1
```

…or by hand:

```powershell
py -3 -m pip install pyinstaller
py -3 -m PyInstaller Sentinel-Forge.spec --clean --noconfirm
```

**Output:**
- `dist\Sentinel-Forge\Sentinel-Forge.exe` — ~6 MB launcher
- `dist\Sentinel-Forge\_internal\` — Python runtime + bundled libs
- Folder total: ~30 MB without TTS · ~175 MB with the Piper voice bundle

Ship the whole `dist\Sentinel-Forge\` folder — it's a one-folder build
(intentional: cold-start is fast and the 60 MB voice model doesn't get
extracted to `%TEMP%` on every launch).

To skip bundling TTS (smaller .exe; app falls back to SAPI5):
```powershell
powershell -ExecutionPolicy Bypass -File scripts\build_exe.ps1 -NoTTS
```

---

## Roadmap / what's open

- ✅ Single-distributable `.exe` via the existing PyInstaller spec — `scripts\build_exe.ps1`
- 🔲 Voice-note recording (browser MediaRecorder; or `pyaudio` in Tk)
- 🔲 Tagging UI for the `tags: []` field (schema already supports it)
- 🔲 Two-way sync with the [Sentinel Forge platform](https://github.com/coconuthead-Sentinel-core/Sentinel-of-sentinel-s-Forge)
  (write-back zone migration from the web dashboard)
- 🔲 macOS / Linux ports (Tk is portable; Piper has Linux builds)

## License

MIT — see [LICENSE](LICENSE).

## Author

**Shannon Brian Kelley** (*Coconut head*) · United States ·
[github.com/coconuthead-Sentinel-core](https://github.com/coconuthead-Sentinel-core)

> Healthcare CNA → AI Systems Developer transition · neurodivergent-first
> design · accessibility-focused AI engineering.
