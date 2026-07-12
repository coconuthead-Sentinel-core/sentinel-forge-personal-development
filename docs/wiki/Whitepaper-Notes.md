# White-Paper Notes — raw material (append-only)

> Working title: **"Neurodivergent-First by a Neurodivergent Architect:
> Designing, Testing, and Shipping a Local-First Personal-Development
> Workstation with AI-Assisted Development."**
> Practice: every README/docs update leaves 1–3 sentences here. When
> enough accumulates, notes feed the skeleton in [Whitepaper-Outline](Whitepaper-Outline.md), which becomes the white paper's outline.
> Framing rules (owner's decision, July 2026): lead with engineering;
> public disclosure stays at the README's existing line
> (ADHD/dyslexia/dysgraphia); one paper anchored here, citing Imprint
> and strata-console as the "one assistant design, three shipped
> dashboards" replication proof.

---

- **2026-07-11 — Review-readiness pass.** Accuracy is the polish that
  matters: the README claimed 34 tests while the suite held 172; a
  top-down review treated every stale claim as a defect. Lesson for the
  paper: documentation drift is a bug class, and single-developer
  projects need scheduled doc audits just like dependency updates.
- **2026-07-11 — "Numbers need a picture."** Dyscalculia turned into a
  design law: every raw figure ships with a gauge, meter, or
  translation (months of survival fuel, hours of life). Accessibility
  requirements stated as engineering laws — not accommodations — is the
  paper's central thesis in miniature.
- **2026-07-11 — Archive, never delete.** A 300-file cleanup froze the
  UI (per-file Recycle-Bin calls on OneDrive-synced files, on the UI
  thread); the fix reframed the operation entirely — "remove" became
  "move to archive," matching the user's trust requirement that files
  never leave the laptop. UX vocabulary is a safety feature.

- **2026-07-11 (evening) — Self-documenting maintenance loop.** The
  project now includes an assistant-maintained operations page
  (Assistant-Notes.md): every README review triggers a read-execute-
  update cycle over the wiki, closing the loop between documentation
  and action. A development methodology detail for the paper: the
  documentation is not just ABOUT the system — it is part of the
  system''s control loop.

- **2026-07-11 (late) — Rebuild blueprint as insurance.** The project
  now carries its own reconstruction plans (Rebuild-Blueprint.md):
  language-portable pseudocode of the foundation, threading circuits,
  data plumbing, and room-by-room build order with acceptance gates —
  written after an earlier project WAS lost. Estimated replacement
  cost drops from months to 8-12 sessions. Documentation as disaster
  insurance is a paper-worthy practice for solo developers.

- **2026-07-11 (late) — Template library discipline.** The owner
  maintains a blank-template source library (the Codex) with a written
  policy: templates stay blank; projects copy and fill their own
  copies. The rebuild pack (docs/rebuild-pack/, 8 filled inventories
  from the engineering template pack) demonstrates the discipline —
  reusable process assets, per-project instances. That separation is
  itself an SDLC maturity marker worth a paragraph in the paper.

- **2026-07-11 (late) — Spreadsheet as floor plan.** The rebuild pack
  gained an Excel floor plan: colored cell blocks draw the rooms, and
  symbol fixtures (🔌 thread seams, 🚿 outputs, 🧊 storage) link to
  tables naming the exact code home of every outlet and pipe. For a
  dyscalculic, spatially-thinking owner, a grid the eye can walk
  through communicates architecture better than prose — accessibility
  applied to the documentation itself.

- **2026-07-12 — The harvest loop closes read→remember.** The Knowledge
  Harvester mines term/definition pairs from any Library book into the
  FSRS deck, with a checkbox preview keeping the human in the loop. It
  shipped in two gated sprints: a pure-logic core practiced against a
  real 1.9M-character corpus until junk hits reached zero, then a thin
  UI. Method note for the paper: the mockup-first protocol (three
  verifiable no-harm proofs before a single project line changed) is
  the AI-era version of a design review.
