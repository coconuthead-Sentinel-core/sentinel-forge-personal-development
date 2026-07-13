# Handoff Memo — 2026-07-13 (final, end of cloud session)

**From:** the cloud assistant (Claude, Anthropic — Claude Code session)
**To:** the laptop coding assistant (Claude, Anthropic) and Shannon
**Read next:** `docs/DESKTOP_ASSISTANT_HANDOFF.md` (your working orders)

---

## Your assignment, in one sentence

> Install the three guardrail skills as your own (handoff §6), do the
> desktop-only checklist below, then follow
> `docs/DESKTOP_ASSISTANT_HANDOFF.md` in order — pseudocode before code,
> always.

## 1. The permanent rules (install these FIRST — handoff §6)

Three skills live in `.claude/skills/`. They are Shannon's standing
rules for **every project from now on**, not just this repo. Mirror
them into your user-level skills directory so they load everywhere:

| Skill | What it governs |
| --- | --- |
| `clinical-science-gate` | What CLAIMS get in: every citation verified against real literature; labels match evidence tier (RCT / guideline / trade book); never "proven" without a study; no clinical claims — software is scaffolding, diagnoses belong to clinicians. |
| `classroom-code` | How CODE gets built: five SDLC stages in order, pseudocode before code (re-derive inherited blueprints in your own words), tests before UI, functional code only — a control that does nothing is a defect — and honest reporting. |
| `learning-science` | How LEARNING gets built: retrieval practice, spacing via FSRS, worked examples with fading, expertise reversal (fade scaffolds), delayed self-testing. Neuromyths blocked (learning-styles matching, the 10,000-hour rule). Access accommodations are legitimate as access, never claimed as efficacy. |

Fallback for surfaces that can't load skills: concatenate the SKILL.md
files verbatim into a bootstrap prompt — never re-summarize (one source
of truth, no drift).

## 2. What the cloud session shipped (all merged to `main`)

- **PR #50** (`da0252a`): 💼 **Job Readiness audit** — six-pillar
  self-examination (Story, Proof, Skills, People, Pipeline, Interview),
  pure kernel + Planning-hub window, 15 tests, additive
  `job_readiness_checks` table. Plus the **README evidence-honesty
  pass** (every claim names its real mechanism; two fabricated citations
  in supplied research were caught and kept out — see
  `docs/wiki/Review-ImprovementAudit.md`), dead-code removal, and the
  desktop handoff document.
- **PR #51** (`88f5f8e`): the **three guardrail skills** above, this
  memo, the mirror-skills order, and **interview-ownership framing** in
  the Job Readiness Story/Interview steps ("I built…", "I implemented…",
  STAR answer shape).
- Suite at handoff: **339 headless / 341 with display, all green**; CI
  green on Python 3.11 and 3.13; design-law linter green (Rules A and B
  hard-gated).

## 3. Desktop-only checklist (cloud could not reach these)

| # | Item | How |
| --- | --- | --- |
| 1 | Delete the merged session branch `claude/sentinel-forge-personal-dev-j10gax` | "Delete branch" button on the merged PR #51 page, or `git push origin --delete <branch>`. |
| 2 | Mirror both clones as EXACT clones of `main` | `git pull` in `Desktop\Sentinel-Forge` AND the OneDrive clone; no stray files. |
| 3 | Install the three mirror skills (user-level) | Handoff §6. Do before any coding. |
| 4 | Dead-button audit on the real display | Shannon reports buttons that don't work. Handoff §4 — probe with `.invoke()` AND real clicks; log findings in Assistant-Notes §5; fix through the pipeline. |
| 5 | Sprint queue **B → C → D → F** | Handoff §2 — re-derive each blueprint in YOUR OWN pseudocode first: B two-lapse streak protocol · C WCAG contrast gate · D V2MOM if-then line · F **Bill Sentinel** (bills/prospective-memory scaffold — Shannon's own ask). |
| 6 | The ~202 research files | Not in the repo yet. When Shannon adds them: every claim passes `clinical-science-gate` BEFORE use. Not worthless — but nothing enters without the gate. |

## 4. Working with Shannon (owner of all of this)

Lead with the outcome. One clarifying question maximum. One primary
action per screen; five major choices or fewer. Honesty over polish —
no "enterprise-grade", no "proven" without a study, no inflated safety
claims. He does daily check-ins (sleep, food, hydration, per the
agreement) — respect the cadence. His standing rule is ADDITIVE:
improve the work, never tear it down. The acceptance bar for
everything: **would a CS professor bound by a code of ethics sign it?**

## 5. Paperwork duty (after every sprint — not optional)

CHANGELOG → Whitepaper-Notes (1–3 sentences) → Assistant-Notes §5
(mark done, suite count) → README counts → Feature-Catalog /
Database-Schema rows → commit → push → merge to `main` → delete the
session branch → mirror both clones.

*Thank you for picking this up. The pipeline works — eight-plus
features have shipped through it without a regression escaping to
Shannon's machine. Trust the stages, keep the paperwork, and it will
keep working. — the cloud assistant*
