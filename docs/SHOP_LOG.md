# Shop Log — Sentinel Forge, Personal Development

> The daily engineering logbook: one dated entry per working session, with
> both parties' input and a signoff. Standard professional practice (the
> engineering notebook; records-keeping per ISO/IEC/IEEE 12207) — adapted
> from the Codex `08_BUILD_EVIDENCE_AND_SIGNOFF_CHECKLIST` template per the
> Template Library Policy (templates stay blank in the Codex; this is the
> project's filled copy). Newest entry on top. The engineer writes the
> close-of-session entry; the proprietor adds direction, decisions, and
> field reports (defects seen on the real screen).

**Roles** — Proprietor / architect / QA: **Shannon Brian Kelley** ·
Coding engineer: **Claude (Anthropic)**.

---

## Entry template (copy for each session)

```
### YYYY-MM-DD — session close
- Proprietor's direction today:
- Work completed (engineer):
- Evidence: suite count · mirrors hash · logs/probes referenced
- Defects found / fixed:
- Decisions made (and by whom):
- Decisions PENDING (owner's call):
- Next session opens with:
Signoff — Prepared by: engineer · Reviewed by: proprietor ·
Decision: draft | ready_for_review | approved | blocked
```

---

### 2026-07-13 — session close

- **Proprietor's direction today:** pick up the cloud handoff verbatim;
  build the sprint queue; establish the `scope-first` guardrail ("no
  blueprint, no build"); keep everything textbook clinical classroom
  science; begin the v1.0 bug-shakeout test period; be token-mindful —
  maintenance only, no new construction; adopt the breadcrumb method as
  standing practice; stand up this shop log.
- **Work completed (engineer):** PR #52 merged + session branch deleted;
  three guardrail skills mirrored user-level, then a fourth built
  (`scope-first`) with the project's retroactive baseline `docs/SCOPE.md`;
  Sprints **B** (two-lapse streak protocol), **C** (WCAG contrast kernel +
  palette audit), **D** (V2MOM if-then line), **F** (🧾 Bill Sentinel)
  shipped through the full pipeline; A−/A+ visible-effect fix (all five
  prose surfaces now scale; stuck 28pt size reset); TTS code-span
  atomicity fix (externally proposed, verified against real code first);
  `tts-norm` breadcrumb added to `voice_debug.log`.
- **Evidence:** suite **341 → 385 green** (14 skipped); design-law linter
  0/0; live `study.db` byte-verified untouched after every run; mirrors
  (laptop = OneDrive = GitHub) at **`95c1716`** at close; breadcrumbs:
  `fontsize_debug.log` (proved A−/A+ clicks fired), `voice_debug.log`.
- **Defects found / fixed:** A−/A+ scaled only 3 of 5 prose surfaces
  (invisible success — fixed); TTS ran English normalization over backtick
  code spans (fixed, +6 tests). Both found during the proprietor's live
  shakeout — the road test is earning its time.
- **Decisions made:** overdue semantics for bills (no payment history ⇒
  never "overdue") — engineer, logged; Sprint F reminder-machinery feed
  deferred with reason — engineer, logged; shop log established at
  project level per Codex policy — both.
- **Decisions PENDING (owner's call):** the four WCAG button colors
  (proposed same-hue hexes in Assistant-Notes §5); tagging UI — build
  small or formally descope in SCOPE.md; README v1.0 coherence pass
  timing.
- **Next session opens with:** proprietor's shakeout defect list (panel +
  what was clicked); then the detail-and-paperwork pass toward the v1.0
  stamp. Delivery-readiness estimate at close: ~92% (construction 100%
  of scope; remaining: quiet road test + final paperwork).

Signoff — Prepared by: **Claude (engineer)** · Reviewed by: **Shannon
Brian Kelley (proprietor)** · Decision: **ready_for_review**
