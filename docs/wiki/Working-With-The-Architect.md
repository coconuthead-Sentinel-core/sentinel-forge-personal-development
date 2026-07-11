# Working With The Architect — collaboration & accessibility notes

> Notes for any assistant, collaborator, or future maintainer working
> with **Shannon Brian Kelley** — this project's owner, architect, and
> primary user. Sentinel Forge is neurodivergent-first *because its
> owner is*; these notes make that concrete. Written with his consent
> as part of the July 2026 top-down review. Tone rule #1: **dignity.
> These are engineering requirements, not limitations.**

---

## 1. Who you're working with

- **Role:** architect / stakeholder / QA — he directs and reviews; the
  assistant implements. Human-in-the-loop boundaries in specs (like
  RELAY-SRS-001's "Shannon reviews and merges") are real and binding.
- **Background:** CNA → AI-systems-developer transition, age 55,
  actively in coursework. Beginner at *writing* code, strong and
  fast at *judging* products, scope, and honesty.
- **Accessibility profile (his own public framing):** ADHD, dyslexia,
  dysgraphia, dyscalculia; monitored for full-spectrum autism. Every
  rule below traces back to one of these.

## 2. How to communicate (classroom-structured)

- **Plain language, short sentences.** One idea per sentence. Define
  any term a coding class would define (and anchor it to HIS code:
  "a tab — like the Study workspace buttons you built").
- **Lead with the outcome.** What happened, in the first line. Detail
  after, for when he wants it.
- **One question maximum,** and only when the code can't answer it.
  Guess-and-execute on reversible work ("act, don't interrogate").
- **He evaluates by what's on screen.** If a feature works invisibly,
  it reads as broken. Every action needs visible feedback (the Daily
  10 Goals "✓ Saved" lesson).
- **Honesty is the brand.** Never overclaim ("enterprise-grade",
  "production-ready"). Correct his overclaims gently — he *asks* for
  this (interview-vocabulary coaching). If something can't be done,
  say so plainly; he explicitly prefers "it can't be done" to a
  flattering maybe.
- **Speech-to-text quirks:** he dictates. Expect mangled words
  ("Cobain's Burrito", "in print" = Imprint, "sitional" = Sentinel,
  "panels" = tabs). Read for intent; confirm by restating, not by
  quizzing him.

## 3. Design laws (violations are bugs)

| Law | Why |
| --- | --- |
| Size every window from `winfo_screenwidth/height`; never hardcode | His display is ~1097×617 effective; fixed sizes cut off bottom buttons |
| Row heights from font metrics, never fixed pixels | High-DPI + dyslexia: clipped text is unreadable text |
| One primary action per screen; ≤5 major choices | ADHD executive-function load |
| Big, colored, labeled buttons | Small targets cost attention |
| Reading surfaces honor the user's font choice (OpenDyslexic first) | Dyslexia |
| **Numbers need a picture** — gauges, meters, progress bars, "hours of life" translations alongside raw figures | Dyscalculia: a wall of digits doesn't parse; the Run-Rate battery and Time-Cost translator are the model |
| Files NEVER leave the laptop — "remove" means archive/move, not delete | Trust + data safety; Recycle-Bin prompts read as danger |
| Visible confirmation for every save/action | "Invisible success" reads as failure |
| Predictable, calm feedback; no surprise sounds outside opted-in alerts | Sensory regulation (autism-spectrum consideration); the ONE exception is the appointment siren he explicitly loves |
| Rescue, never shame (Never-Miss-Twice, streaks) | Recovery-first is a hard product value |
| Tuple `pady` only in `.pack()/.grid()`, never widget constructors | The codebase's oldest recurring crash |

## 4. Session rhythm (paraprofessional-style)

- He runs **Pomodoro-style blocks** and sometimes works very long
  stretches (24-hour sessions have happened). If he mentions being
  up long: finish the task cleanly, keep replies short, and gently
  reinforce his own rest protocol — his app preaches it.
- **End every work block shippable:** commit → push → pull both
  clones → no dangling branches. He should never return to a
  half-done state.
- **Session continuity is a product feature and a personal need:**
  handoff notes, memory files, and this wiki exist so neither he nor
  the assistant ever starts cold.

## 5. Workflow laws (mechanics)

- GitHub `main` is the source of truth. Three-way mirror: laptop
  install ⇄ OneDrive clone ⇄ GitHub. **After every push, pull
  `Desktop\Sentinel-Forge`** — that's the copy his shortcut runs.
- Work in a fresh branch per session; merge to main; **delete child
  branches** when done (his standing order).
- Verify on his hardware. Cloud-written code has shipped silent
  breakage here before (see Former-Bugs, July 2026 batch).
- Tests before ship: full suite headless; UI flows via smoke scripts
  under a real `mainloop()`.

## 6. The goal behind everything

A full-time job in the field. Every feature, README line, and commit
message is also a portfolio artifact. Ask of any change: *"does this
make the project easier to demo, easier to defend in an interview,
and truthful?"* If yes to all three, it fits.
