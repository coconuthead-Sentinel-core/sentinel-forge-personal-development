# Sentinel Forge — Personal Development

> **A native Windows desktop personal-development workstation: read `.docx`,
> `.pdf`, `.md`, `.txt`, `.rtf`, and `.html` with highlight-by-sentence,
> capture by Whisper voice dictation, and run focused sessions with goals,
> accountability tracking, and a zone-tagged Library.**

![Status](https://img.shields.io/badge/status-v0.9%20release--candidate-success)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Platform: Windows](https://img.shields.io/badge/platform-Windows-0078d4.svg)

---

## ⚑ For the desktop coding assistant (Claude, by Anthropic) — start here

Your working orders live in
[`docs/DESKTOP_ASSISTANT_HANDOFF.md`](docs/DESKTOP_ASSISTANT_HANDOFF.md).
Summary of the standing guardrails, set by the owner:

1. **Strict Clinical Science 2026.** Nothing enters this repo without a
   verified, real citation — fabricated references have already been caught
   in supplied research material, so check every one yourself. Trade-book
   ideas are labeled honestly, never called "proven".
2. **Classroom textbook computer science.** Every feature goes through the
   [`/sentinel-sprint`](.claude/skills/sentinel-sprint/SKILL.md) pipeline:
   pure kernel → headless tests green → wire with visible feedback → smoke
   under a real `mainloop()` → design-law linter → paperwork (CHANGELOG,
   wiki, whitepaper notes) → merge to `main` → delete the session branch →
   mirror both clones (Desktop + OneDrive) as exact clones.
3. **Functional code only.** A button that does nothing is a defect. Before
   coding anything new, re-derive the queued sprint blueprints
   (handoff §2) in your own pseudocode, reconcile differences, then build.
4. **Evidence-based learning only.** Study/review features and teaching use
   the [`learning-science`](.claude/skills/learning-science/SKILL.md) skill:
   retrieval practice, spacing (FSRS), worked examples with fading — and
   never the known neuromyths (learning-styles matching, the 10,000-hour
   rule). Access accommodations are legitimate as access; they are not
   claimed as learning efficacy.

## Engineering & SDLC status

This project follows an **iterative / incremental** software life cycle
(single-developer **Kanban**), documented in
[`docs/SDLC_STATUS.md`](docs/SDLC_STATUS.md) against ISO/IEC/IEEE 12207 and the
IEEE SWEBOK. Current working version: **v0.9 (release-candidate track)**.

**Architecture — functional core / imperative shell.** The Tkinter app
(`sentinel_personal_development.py`) is the UI shell; reusable, UI-free logic
lives in the `lyceum/` package and is unit-tested in isolation:

| Module | Responsibility |
| --- | --- |
| `lyceum/db/study_db.py` | SQLite schema, queries, and an atomic `transaction()` primitive (ACID) |
| `lyceum/metrics.py` | Pure progress math (`progress_pct`, `wheel_progress`, `goal_progress`) |
| `lyceum/text_norm.py` | `normalize_for_speech()` — expands numbers/currency/ordinals/abbreviations before TTS |
| `lyceum/reminders.py` | Windows scheduled-task appointment reminders |

**Tests** (run from the repo root):

```
python -m unittest discover -s tests
```

359 automated tests cover the **WCAG contrast kernel**, the **two-lapse streak protocol**, the **job-readiness audit kernel**, the password-strength estimator, the ECA automation engine, the prompt coach, the readability analyzer, the spreadsheet formula engine, the knowledge harvester, the Commentary store, the progress kernels, database atomicity
(commit + rollback), the speech normalizer, the hands-free
dictation-command parser, local retrieval (RAG), the document writer,
the cached file indexer, the FSRS spaced-repetition core, the study-panel
legibility kernel, the **design-law linter**, and the **live-DB isolation
guard** — all logic kept free of Tkinter so it is testable without launching
the GUI.

---

## What it does

- **Open** any book (`.docx`, `.pdf`, `.md`, `.txt`, `.rtf`, `.html`) and
  read it in a big, readable single-window UI
- **Highlight by sentence, word, or paragraph** with 8 colour swatches
- **Session Start**: Pre-commit to a single task, write a brief handoff note, and start your session with standard Pomodoro intervals (e.g. 25 minutes) using the **🔥 Do Now** feature.
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

- **⭐ Major Definite Purpose banner** — a permanent scrolling marquee sign pinned
  to the very top of the dashboard. Your one burning goal (e.g. *"Earn my
  Computer Science Degree by 2028"*) moves across the screen whatever you're
  doing — schedule, bills, reading — because Hill and Tracy found that one
  organizing goal is what separates the achievers. Click it to edit; it persists
  across sessions.
- **🌤 Blue-Sky Vision Board** — upload images of the life you want (the exact
  car, the house, the diploma), add captions, and play the **60-second slideshow**
  — optionally set to your own **WAV music** — to keep your goals primed and
  vivid each morning. (Tracy and Robbins call this "programming the reticular
  activating system"; the measured mechanism is goal-priming and motivation —
  Oettingen, 2014 — not neural reprogramming.) A daily nudge reminds you to watch it
  before the day begins; play/pause, prev/next, and a countdown included.
- **🧭 V2MOM "Why" Engine** — knowing *why* beats knowing *how* (Sinek, Robbins).
  Every major goal is captured through the V2MOM intake (Marc Benioff's
  Salesforce planning method) — **Vision, Values
  (your Why), Methods, Obstacles, Measurement** — and the app **won't let you
  save** until you've written your **Why** and named the **Obstacles** in the
  way. Goals you can't justify don't get made.
- **✍ Daily 10 Goals (spiral notebook)** — Brian Tracy's exercise: each morning
  the app gives you a **blank, numbered list** and you rewrite your top 10 goals
  **from memory, in the present tense** (*"I earn $80,000 as a software
  engineer."*). Daily recall from memory strengthens the goals' hold on your
  attention — the retrieval-practice effect (Roediger & Karpicke, 2006); a
  🔥 **day-streak** rewards the habit, and it nudges you each morning until it's
  done. (Blank each day on purpose — recalling them is the point.)
- **🪜 Systems & Checklists (A→B→Z)** — goals set the direction; *systems* get
  you there (James Clear). Break a big goal (**Z**) into an ordered checklist,
  and the tool always highlights **your next step (B)** — the only one you need
  to know — with a progress bar as you check each off. A checklist makes success
  ~10× likelier (Tracy). Reorder steps, run multiple systems, watch *"Z reached"*
  light up at 100%.
- **⏪ Back-From-The-Future planner (PERT)** — *project forward, look backward.*
  Set the date of the result you want (*"Graduate with my CS degree, June 2027"*),
  list the milestones, and it **schedules them backward** to a visual timeline —
  computing **exactly when each must begin** and whether you're on track or need
  to start today (*"you needed to begin by Nov 18, 2025"*). With a TODAY marker,
  per-milestone date ranges, and check-off.
- **🎯 Lead vs. Lag (4DX)** — you can't manage a **lag** measure (the result —
  pounds lost, dollars earned), only the **lead** measures (the daily activities
  that predict it). This view pairs the two: name the results you're after up
  top, and tap your daily levers below (shared with the 🏆 Scoreboard, with
  streaks and a WINNING tally) — so you always act where you actually have
  control.
- **🔁 Habit Stacker + Two-Minute Rule (James Clear)** — write each habit as a
  formula, **"After I [current habit], I will [new habit]"**, anchoring the new
  one to something you already do, and shrink it to a **2-minute gateway version**
  (*"read one page"*, *"put on my running shoes"*) so starting is effortless.
  Tap ✓ each day; 🔥 streaks build the chain.
- **📅 Never Miss Twice (dopamine streak tracker)** — a gamified **calendar** for
  any habit: a bright **green dot** for every day you show up (with a 🎆 fireworks
  burst + chime — visible progress releases dopamine, per Sinek), a **red dot**
  for a miss, and a hard rule — *never miss twice*: miss yesterday and the whole
  thing turns red and dares you to save the chain today. Tracks current streak,
  best streak, and month navigation.
- **Study tabs** — autosaving **Study Notes**, **Topics**, **Glossary**,
  dated **Journal**, a four-quadrant **Eisenhower Matrix**, and a
  Sunsama-style weekly **Planner**. The three reference panels (Topics,
  Glossary, Commentary) share one clean **Journal-style layout** with a
  horizontal reading slider, and secondary actions live on a right-click menu.
- **🚦 Floating toolbar as the fixed "safe spot"** — one uniform control
  cluster, docked or floating, identical in every panel: a **traffic light**
  with the word above each colored lamp (**green Add · yellow Save · red
  Delete**), and **A− / A+** drawn as **road-marker signs** that hold one
  white and one black at all times (last-pressed = white). Add / Save / Delete
  each **context-dispatch** to the active panel, and text-input boxes are
  **toolbar-driven** — no OK/Cancel: right-click to Cut/Copy/Paste/Clear, then
  **Enter or the yellow Save** commits. Designed for zero-instruction
  recognition by a visual/tactile, ADHD/dyslexia learner.
- **🚀 Performance dashboard** (4DX + Ziglar): a **🏆 Compelling
  Scoreboard** of daily lead measures with streaks, a **🧠 Idea
  Warehouse** (ABCDE priorities, Big-Three, schedule-to-planner,
  implementation intentions), **🎯 Focus Mode** with timed focus blocks,
  a **🚫 Not-To-Do list + website blocker**, **☸ Wheel of Life** and
  **🎯 Goals**, and **🧭 Weekly Roles**.
- **⏱ Winner's Time Log (time auditor)** — a low-friction chime every
  5, 10, 15, 20, 25, 30, 60, 90, or 120 minutes asks "what did you work on?"; one tap
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
  *move* before your brain talks you out of it. (Trade-book technique — no
  direct trials of the countdown itself; the mechanism matches
  implementation-intention research, Gollwitzer, 1999.)
- **💰 Pay Yourself First** — Clason's first law of wealth: *a part of all you
  earn is yours to keep.* Enter a paycheck and the app deducts your savings
  **first** (10%, or start at 1% if money's tight), **locks** it into a
  Financial Independence balance you can't budget away, and only lets you
  allocate the **spendable remainder** across rent, gas, food, etc. — it
  refuses any budget line that would dip into your savings — a deliberate
  pre-commitment device (Thaler & Benartzi's *Save More Tomorrow*, 2004).
- **🛡 Core Four (Defense Mode)** — when money's tight, strip the budget down
  to the four survival numbers: **Rent · Utilities · Food · Transportation**.
  A bold 2×2 grid checks them against the cash you have — each box turns
  **green when secured, red when not covered** — and tells you if you're short
  and by how much, so your most basic needs get covered *first*. Can pull the
  spendable figure straight from your latest paycheck.
- **📒 Spending — Financial Defense** — a low-friction expense ledger: log any
  expense (amount + category + note) in seconds, then see where the money goes
  over **this month / 30 days / year / all** in a colored category bar chart
  (defense = green, discretionary = amber). Your **Core Defense** numbers (Rent /
  Utilities / Food / Transportation) sit up top, checked against your Core Four
  targets — wealth is won with great financial defense.
- **🔎 Hidden Fee Checker** — Wall Street fees can quietly eat 50–70% of a
  lifetime nest egg. Enter your balance, contributions, return, and your fund's
  expense ratio, and it shows the **lifetime cost vs a low-cost index fund** in a
  side-by-side bar chart — *"those fees will cost you $398k — 22% of your nest
  egg, ~18 years of retirement"* — and lists low-cost index funds to switch to.
  (Manual entry — it does not connect to your accounts.)
- **☕ Latte Factor (expense auditor)** — the small daily leaks sink the ship.
  Fast-entry (one-tap chips for coffee, snacks, subscriptions, or any custom
  amount) logs every little purchase, and the weekly total projects it out to
  the **month and year** — plus the **real cost**: what that daily leak would
  become if **invested at 8% for 20 years** (a $10/day habit ≈ $166k of lost
  compound wealth), and what it could have funded in a Dream Bucket instead.
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
- **🔋 Run Rate (Law-of-Three emergency-fund meter)** — how many months you could
  survive if income stopped today: cash savings ÷ your Core Four monthly
  expenses. A **battery meter** shows the charge (*"You have exactly 1.5 months
  of survival fuel"*) with Tracy's **Law of Three** protected band shaded from
  **2 to 6 months** (2-month floor + 3-month safe line marked), and one tap sets
  an automatic **3-month Emergency Fund goal** as a Dream Bucket. Pulls expenses
  from Core Four and cash from your Pay-First balance.
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
  *$20/week at 8% → ~$179,000 by 65, only $36k of it your own money*). A visual
  **Rule-of-72 doubling ladder** shows your current savings stepping up
  **now → 2× → 4× → 8× → 16×**, one rung every *72 ÷ rate* years (so $10k at 8%
  becomes $160k in 36 years). Open it whenever you feel poor or stuck and *see*
  your future wealth — instant hope.
- **📊 Expected Net Worth (PAW vs. UAW)** — a high income isn't wealth (*The
  Millionaire Next Door*). It runs the formula **age × income ÷ 10** for your
  target net worth, compares it to what you actually have on a **continuum gauge**,
  and tells you whether you're a **Prodigious** (≥2×) or **Under** (≤½×)
  Accumulator of Wealth — so you know exactly where you stand.
- **🧺 Three-Bucket Asset Allocator (Tony Robbins)** — asset allocation is the
  most important investment decision of your life. Split your holdings across
  **🛡 Security** (cash, bonds, TIPS — can't lose), **📈 Risk/Growth** (stocks,
  equities, real estate), and **✨ Dream** (strategic splurges). Each bucket shows
  its total and **% of your portfolio** with a share bar; move any holding
  between buckets with → to tune the balance of safety and growth.
- **🌦 All Seasons Portfolio (Ray Dalio)** — a calculator pre-programmed with
  the simplified public **All-Weather** mix Robbins published from his Dalio
  interview (**30%** stocks · **40%** long-term bonds · **15%** intermediate
  bonds · **7.5%** gold · **7.5%** commodities). Enter an amount and it splits
  it across the mix in a pie chart with dollar figures. Honest label: this is
  a **fixed target allocation**, not risk parity — the actual All-Weather
  fund's weights are proprietary and use leverage; the historical record
  (positive ~85% of years; −3.93% in 2008) belongs to backtests of the
  simplified mix.
- **🏁 Critical Mass (decumulation simulator)** — accumulating is only half the
  climb; you must not outlive your money. It finds your **Critical Mass** (income
  to replace ÷ safe-withdrawal rate — e.g. $40k ÷ 4% = **$1M**, the point where
  your money earns your salary), tracks your **progress** to it, models how many
  **years your nest egg lasts** under withdrawals (or whether it's self-sustaining),
  and shows what a **Fixed Indexed Annuity** could guarantee for life — upside
  participation, zero downside.
- **🔍 Zero-Based Audit (KWINK)** — Brian Tracy's "Knowing What I Now Know" cure
  for the sunk-cost trap. Every recurring charge *and investment holding* must
  re-earn its place: **every ~90 days the app forces an audit** that walks each
  subscription **and** each holding from your Allocator and asks, *"Knowing what
  you now know, would you do this again today?"* A **No** cancels the sub or
  **liquidates the investment** on the spot — *don't throw good money after bad.*
  Shows your total subscription burn at a glance.
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
git clone https://github.com/coconuthead-Sentinel-core/sentinel-forge-personal-development.git
cd sentinel-forge-personal-development

# 2. Install Python deps
py -3 -m pip install -r requirements.txt

# 3. Run it
py -3 sentinel_personal_development.py
```

Or double-click **`run_sentinel.bat`** for a no-console launch.

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
| `send2trash` | recoverable deletes from the Library |
| `tkinterdnd2` | drop-files-on-the-Library-window support (optional) |
| `openpyxl` | read/write `.xlsx` for the assistant (read Excel context, draft real spreadsheets) |
| `fsrs` | py-fsrs — MIT-licensed FSRS scheduler behind the 🧠 Memory Review flashcards |

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
├── sentinel_personal_development.py ← the entire desktop app (single file)
├── run_sentinel.bat               ← no-console launcher
├── run_sentinel_debug.bat         ← console launcher for debugging
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
- ✅ 🧠 Spaced-repetition memory training (FSRS) — Glossary terms become
  scheduled flashcards with a review window, streaks, and an append-only
  review log (`lyceum/srs.py`, see `docs/SRS_MODULE.md`)
- ✅ AI Chat context sources — 🌐 web search (DuckDuckGo, no key),
  ☁ OneDrive file retrieval, 📎 attachments incl. Excel/CSV, and
  📄 drafting real Word/Excel documents with live formulas
- ✅ 🐢/🐇 reading-speed control wired through every voice path
- ✅ Library 🗃 archive workflow — removals move files to `Books Archive`,
  never the Recycle Bin
- ✅ 🔒 Password-strength estimator (`lyceum/password_strength.py`) — a
  Shannon-entropy strength meter (bits + band + crack-time) surfaced as a
  local, private 🔒 utility; nothing is stored, sent, or logged
- ✅ 🤖 Automation engine (`lyceum/automation.py`) — an Event-Condition-Action
  (ECA) rule engine: WHEN an app event fires AND conditions pass, THEN it
  suggests actions (e.g. after a 25-min focus block, prompt to mark the
  Scoreboard). A pure decision engine — it never acts on its own
- ✅ ✨ Prompt Coach (`lyceum/prompt_coach.py`) — a live prompt-quality
  analyzer that scores your AI-Chat draft against the prompt-engineering
  rubric (role/task/context/format/specificity) and teaches the biggest
  fix as you type, with a ✨ Improve button
- ✅ 📖 Readability analysis (`lyceum/readability.py`) — Flesch-Kincaid grade
  level + Reading Ease over a syllable-counting kernel; saved excerpts get an
  objective difficulty badge ("📖 Grade 8 · Plain") beside the cognitive-load
  zone — an accessibility signal for a dyslexia-first reader
- ✅ 🧮 Spreadsheet formula engine (`lyceum/formula.py`) — a tokenizer →
  recursive-descent parser → evaluator for Excel-style formulas (SUM,
  AVERAGE, IF, lookups, A1 ranges); the assistant computes the totals it
  writes into .xlsx and reports the real numbers
- ✅ 🧠 Knowledge Harvester — mine any Library book for term/definition
  pairs (checkbox preview, human-approved) straight into the Glossary,
  where the FSRS review deck picks them up: read → harvest → remember
- ✅ 🚦 Accessibility toolbar cluster — traffic-light **Add/Save/Delete** +
  road-marker **A−/A+**, all context-dispatched; text inputs are non-modal and
  toolbar-driven (right-click clipboard menu, Enter/Save to commit)
- ✅ 🛡 Engineering guardrails — a **design-law linter** (`lyceum/lint_designlaws.py`,
  AST; blocks constructor-tuple `pady` and hardcoded window sizes) and a
  **live-DB isolation guard** (`db_location.assert_not_live_db` +
  `study_db.temp_study_db`), both enforced by the test suite; plus the
  project-local `/sentinel-sprint` build-pipeline skill
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