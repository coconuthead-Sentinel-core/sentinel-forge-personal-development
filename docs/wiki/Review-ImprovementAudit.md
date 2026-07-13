# Review — "Codebase Improvement Audit" (external research document, July 2026)

Shannon supplied an external evidence-based audit ("Codebase Improvement
Audit: Sentinel Forge Personal Development, July 2026") and asked whether it
helps the work, hurts it, or can be built in sprints. This page is the
verdict, produced the house way: every claim checked against the ACTUAL
codebase, every load-bearing citation fact-checked, and each adoptable item
worked out in pseudocode BEFORE any code is written. Nothing here tears down
existing work; every adopted item is additive.

**Bottom line: the audit helps — as a source of ideas, not as a source of
truth.** Four of its nine items are worth building (one already matches a
standing guardrail), three are docs-only honesty fixes, and two rest on
premises that are false for this codebase. At least two of its citations do
not exist and its sample code contains real bugs, so NOTHING from the audit
is to be copied verbatim — ideas in, our own kernels and verified citations
out.

---

## 1. Citation audit (checked 2026-07-13)

| Audit citation | Status | Notes |
| --- | --- | --- |
| Zorzi et al. 2012, PNAS (letter spacing & dyslexia) | ✅ real | Genuine finding; but see Tk limitation below. |
| Kollins et al. 2020, Lancet Digital Health (STARS-ADHD, N=348) | ✅ real | Correct trial, correct N. |
| Gollwitzer & Sheeran 2006 (implementation intentions, d≈0.65) | ✅ real | Meta-analysis of 94 studies. |
| Oettingen 2014 (WOOP / mental contrasting) | ✅ real | Multiple RCTs behind WOOP. |
| Dai, Milkman & Riis 2014 (fresh-start effect) | ✅ real | Management Science. |
| Neff 2003 (self-compassion) | ✅ real | Self and Identity. |
| Thaler & Benartzi 2004 (Save More Tomorrow) | ✅ real | Already the basis of our SMarT feature. |
| Roediger & Karpicke 2006 (retrieval practice) | ✅ real | Already the basis of the SRS work. |
| Roncalli 2013; Maillard et al. 2010 (risk parity / ERC) | ✅ real | Math is standard. |
| Locke & Latham 2002 (goal setting) | ✅ real | |
| **"Pijpker et al. 2025, Annals of Dyslexia, 18-study meta-analysis"** | ❌ **not found — likely fabricated** | Pijpker is a 2013 Twente master's thesis on the Dyslexie font. The real no-benefit findings for specialized dyslexia fonts are Wery & Diliberto (Annals of Dyslexia, 2017) and Kuster et al. (Annals of Dyslexia, 2017). Conclusion survives; citation does not. |
| **"Cortese et al. 2024, JAMA Psychiatry, digital-ADHD SMD=0.28"** | ❌ **not found** | Real meta-analyses exist (e.g. Frontiers in Psychiatry 2023: 31 RCTs, inattention SMD ≈ −0.20) but not this one. |

**Lesson recorded:** an AI-assisted research audit can mix genuine science
with invented references in the same paragraph. Every citation entering this
repo's docs gets verified first — same rule as code: nothing ships unproven.

## 2. Claims that don't match this codebase

| Audit premise | Reality here |
| --- | --- |
| "README … calls this 'risk-budget, not dollar-budget'" (item 1) | The phrase appears nowhere in the repo. README says "Dalio's exact All-Weather allocation" — a different (smaller) overstatement, fixed in the honesty pass below. |
| "'STAR RUCKUS' with N=122 doesn't match published trials" (item 2) | No such citation exists anywhere in this repo. Nothing to correct. |
| OpenDyslexic presented as evidence-backed (item 3) | `lyceum/legibility.py` already labels OpenDyslexic as **the owner's stated preference** and ranks the evidence-backed sans-serifs (Rello & Baeza-Yates, ASSETS 2013) around it. Already honest. |
| Letter-spacing functions for the reader (items 3, 7) | **Tkinter Text widgets have no inter-letter spacing control.** The Zorzi ratio is unimplementable in this shell; line spacing (`spacing1/3`) is the lever we have, and legibility.py already uses it. |
| Touch-target sizes by age band, animation-duration caps (items 7, 8) | Mouse-driven desktop app with essentially no animation. Not applicable. |
| Sample code offered as "production-ready" (items 1, 7) | Contains real defects: a `scipy` dependency (core app is stdlib-only by design), `font_config_for_profile` KeyErrors on its own `'standard'` fallback, and `dollar_to_risk_budget` returns dollar weights while claiming risk contributions (its own comment admits it). Reinforces: ideas in, our own code out. |

## 3. Verdict by item

| # | Audit item | Verdict | Why |
| --- | --- | --- | --- |
| 1 | Risk-parity math for All Seasons | ⚠ **Adopt the honesty, reject the optimizer** | Relabel README: it's Robbins' simplified public mix, a fixed target allocation — not risk parity, not "Dalio's exact" (the fund's weights are proprietary + leveraged). The scipy ERC optimizer breaks the stdlib-core architecture and needs volatility data the app doesn't have. A pure-Python inverse-volatility *educational* view is possible later if wanted (Sprint E, parked). |
| 2 | STARS-ADHD citation correction | ❌ **No action** | Nothing to correct — the wrong citation isn't in this repo. (If we ever cite digital-ADHD evidence: Kollins et al. 2020 is the real trial.) |
| 3 | OpenDyslexic evidence | ✅ **Already done / tiny top-up** | legibility.py already honest. Top-up: add the real Wery & Diliberto 2017 / Kuster et al. 2017 references to its docstring. The "Pijpker 2025" citation must not enter the repo. |
| 4 | Two-lapse streak protocol | ✅ **Adopt — best item in the audit** | Real evidence (what-the-hell effect; self-compassion → faster recovery; fresh-start effect; implementation intentions). Directly improves the Never-Miss-Twice banner, which today shows red + "NEVER MISS TWICE" on the first miss. Sprint B below. |
| 5 | WOOP / if-then plans | ✅ **Adopt additively — do NOT demote V2MOM** | V2MOM is Shannon's shipped workflow; it stays as-is. Add one evidence-backed field: an "If ⟨obstacle⟩, then I will ⟨action⟩" line (Gollwitzer d≈0.65). Also fix attribution: V2MOM is Benioff/Salesforce, not Robbins. Sprint D below. |
| 6 | 5-4-3-2-1 honest labeling | ✅ **Adopt** | One-line README relabel: trade-book technique, plausible mechanism (implementation intentions), no direct RCT. Matches the "honesty over polish" guardrail. |
| 7 | `accessibility.py` module | ⚠ **Adopt one function** | Take the WCAG 2.1 `contrast_ratio` kernel (pure, testable, W3C-specified). Skip spacing (Tk can't), touch targets and animation caps (N/A). Sprint C below. |
| 8 | Linter accessibility rules | ⚠ **Adopt as a palette test, not an AST rule** | A test that every foreground/background pair actually used for TEXT meets WCAG AA (4.5:1) is enforceable and valuable. A blanket "no fonts <12pt" AST gate would fail the intentional 8–9pt chrome labels; the 12pt floor already governs READING surfaces via `legibility.MIN_SIZE` — the right scope split, learned before. |
| 9 | README claims audit | ✅ **Adopt — all three targets verified present** | "program your reticular activating system", "programs them into the subconscious", "refuses any budget line". Reworded with real citations in the honesty pass. |

## 4. Sprint blueprint (pseudocode first — the build order)

### Sprint A — Docs honesty pass (no code; shipped with this page)
README rewords (claims → mechanisms, real citations only):
RAS "programming" → goal-priming/motivation framing; "programs them into
the subconscious" → retrieval-practice effect (Roediger & Karpicke 2006);
savings "refuses" → labeled a pre-commitment device (Thaler & Benartzi 2004);
All Seasons → "Robbins' simplified public version … fixed target allocation";
5-4-3-2-1 → trade-book origin + implementation-intention mechanism;
V2MOM attribution → Benioff (Salesforce). Plus the legibility.py citation
top-up (item 3).

### Sprint B — Two-lapse streak protocol (kernel → tests → wire → smoke)
```
lyceum/streaks.py (pure; no Tk, no I/O)
  LAPSE_STATES = (done_today, active, first_miss, recovery)

  classify_lapse(done_today, missed_yesterday, missed_day_before) -> state
      done_today                      -> "done_today"
      missed_yesterday AND day_before -> "recovery"      # 2+ consecutive misses
      missed_yesterday                -> "first_miss"
      else                            -> "active"

  lapse_message(state, streak, best) -> (text, level)
      done_today  -> ("✅ Done today. The chain grows.",            "green")
      active      -> ("Keep the chain alive — green dot today.",    "muted")
      first_miss  -> ("One day off — a rest day, not a broken       "amber"
                       chain. Do it today and the streak survives."
                      # self-compassion beats shame: Neff 2003)
      recovery    -> ("Two misses. Fresh start today: pick the      "red"
                       exact time you'll do it, then hit the
                       button."
                      # fresh-start: Dai/Milkman/Riis 2014;
                      # implementation intention: Gollwitzer 1999)

tests/test_streaks.py
  - all four states classified correctly (inject the three booleans)
  - first miss is AMBER not red; message contains no shame words
  - two consecutive misses -> recovery; three -> still recovery
  - message/level pairs stable for the GUI mapping

wire: open_streak_tracker banner block (currently hardcodes red on
  yest_miss) -> compute day-before-yesterday miss, call kernel, map level
  to color {green:#22c55e, amber:ACCENT_AMBER, red:#f87171, muted:FG_MUTED}.
  Button label follows state. Visible behavior change: FIRST miss = amber
  encouragement; SECOND consecutive miss = red fresh-start prompt.

smoke: xvfb mainloop — seed temp DB with (a) no miss, (b) 1 miss,
  (c) 2 misses; assert banner color/text per state.
```

### Sprint C — WCAG contrast kernel + palette gate (kernel → tests → gate)
```
lyceum/wcag.py (pure)
  relative_luminance(rgb)  # W3C: linearize sRGB, 0.2126/0.7152/0.0722
  contrast_ratio(rgb1, rgb2) -> float   # (L1+0.05)/(L2+0.05), 1.0..21.0
  meets_aa(ratio, large=False) -> bool  # 4.5:1 text, 3:1 large text

tests/test_wcag.py
  - black/white = 21.0; white/white = 1.0; symmetry
  - known W3C example values within tolerance
  - PALETTE GATE: every (fg, bg) pair the app uses for body text —
    (FG_TEXT, BG_DARK), (FG_TEXT, BG_PANEL), (FG_TEXT, BG_INPUT),
    (FG_MUTED, BG_DARK), (FG_MUTED, BG_PANEL), ("white", each ACCENT_*
    used as a button bg) — meets AA (4.5:1; buttons may use 3:1 large-text
    threshold since they're bold ≥10pt).
  NOTE: run the numbers FIRST in a scratch probe. If a pair fails, that is
  a finding to show Shannon with a proposed nudged hex — do not silently
  recolor the app.
```

### Sprint D — If-then plan line in V2MOM (small feature)
```
schema: v2mom_goals + if_then TEXT (additive column migration, same
  pattern as goals.baseline/target_level)
kernel: no new kernel needed — validation is "obstacle text present ->
  encourage if-then"; keep the existing hard gate (Why + Obstacles) as-is,
  if-then is ENCOURAGED not required (don't stiffen Shannon's flow without
  asking).
wire: one labeled Entry under Obstacles: "If ⟨your obstacle⟩ happens,
  then I will …" + muted evidence line ("if-then plans ~double follow-
  through — Gollwitzer & Sheeran 2006"). Saved with the record; shown on
  load.
smoke: save/load round-trip incl. blank if_then (old rows).
```

### Parked (Sprint E, only if Shannon asks)
Pure-Python inverse-volatility view for All Seasons (no scipy; diagonal
approximation; label as educational). Rejected for now: needs volatility
inputs the app doesn't track, and the honest relabel already fixes the
integrity problem.

---
*Reviewed by the assistant, 2026-07-13. Audit text kept out of the repo;
this page is the durable record of what was adopted, corrected, rejected —
and why.*
