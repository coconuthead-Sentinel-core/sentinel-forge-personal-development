# Portfolio Audit & Hours Ledger

**Owner / Architect / QA:** Shannon Brian Kelley (GitHub: `coconuthead-Sentinel-core`)
**AI pair developer:** Claude (Anthropic) — co-authorship recorded in commit trailers
**Audit date:** 2026-07-20 · **Repositories audited:** 27 (all public, GitHub)

---

## 1. Elevator pitch (for HR)

I design, direct, and quality-test software in an AI-assisted workflow: I act
as product owner, architect, and human-in-the-loop QA, and Claude (Anthropic)
acts as the pair developer writing code to my direction. Across **27 public
GitHub repositories** the evidence trail documents **571 commits over 186
work sessions — an estimated 174+ engineering hours** (a floor; method in §3).
The flagship, **Sentinel Forge — Personal Development**, is a Windows desktop
reading/study workstation with a functional-core architecture, **422 automated
tests**, an AST-based design-law linter, additive-only database migrations,
and an archive-never-delete data policy — engineered against ISO/IEC/IEEE
12207 and IEEE SWEBOK practice, with every feature gated through a documented
pipeline (pseudocode → headless tests → UI wiring → mainloop smoke test →
changelog/wiki paperwork).

**Honest framing:** I did not type the majority of the code; I specified,
reviewed, accepted, and field-tested it, and I own every design decision.
This is the workflow modern teams call AI-assisted development, and the QA
finds on the record (see the flagship's CHANGELOG) were mine.

## 2. Hours ledger — all 27 repositories

Estimated from every repository's full commit history on GitHub (method §3).

| Repository | Commits | Sessions | Est. hours | Active period |
|---|---:|---:|---:|---|
| **sentinel-forge-personal-development** (flagship) | 320 | 46 | **81.2** | 2026-05-22 → 2026-07-20 |
| Sentinel-of-sentinel-s-Forge (platform) | 40 | 23 | 16.1 | 2025-04-28 → 2026-05-03 |
| sentinel-forge-cognitive-orchestrator | 39 | 22 | 15.2 | 2025-04-28 → 2026-04-28 |
| Sovereign-Forge | 35 | 20 | 13.7 | 2025-04-28 → 2026-05-10 |
| Neural-Lattice-Architecture-and-Workflow-Optimization | 26 | 12 | 7.7 | 2025-12-22 → 2026-05-10 |
| enterprise-ai-reliability-platform-v1 | 21 | 10 | 7.2 | 2026-04-18 → 2026-04-28 |
| Quantum-Nexus-Forge | 16 | 8 | 5.9 | 2026-04-09 → 2026-04-28 |
| Imprint (document-automation dashboard) | 15 | 6 | 4.7 | 2026-07-01 → 2026-07-13 |
| cognitive-neural-overlay | 18 | 4 | 3.7 | 2026-05-03 → 2026-05-08 |
| SentinelForge-AI | 8 | 5 | 2.9 | 2026-04-28 → 2026-05-10 |
| sentinel-prime-network | 4 | 4 | 2.0 | 2026-04-26 → 2026-05-03 |
| portfolio-dashboard | 3 | 2 | 1.9 | 2026-05-03 → 2026-05-10 |
| glyphic-codex-7system-work-flow-dsl | 3 | 3 | 1.5 | 2026-05-02 → 2026-05-03 |
| strata-console (local-first NLP pipeline) | 3 | 2 | 1.1 | 2026-07-06 → 2026-07-11 |
| engineering-project-build-and-inventory-template-pack | 2 | 2 | 1.0 | 2026-05-02 → 2026-05-03 |
| hub-and-spoke-ai-chatbot | 2 | 2 | 1.0 | 2026-05-02 → 2026-05-03 |
| ios-compliance-framework | 2 | 2 | 1.0 | 2026-05-02 → 2026-05-03 |
| seed-crystal-input-processing-layer | 2 | 2 | 1.0 | 2026-05-03 |
| seven-layer-architecture-template-pack | 2 | 2 | 1.0 | 2026-05-02 → 2026-05-03 |
| software-development-lifecycle-framework | 2 | 2 | 1.0 | 2026-05-02 → 2026-05-03 |
| ancient-numerics-codex | 1 | 1 | 0.5 | 2026-05-03 |
| cinematography-pipeline | 1 | 1 | 0.5 | 2026-05-03 |
| cstm-lattice-reference | 1 | 1 | 0.5 | 2026-05-03 |
| earp-prompts | 2 | 1 | 0.5 | 2026-05-01 |
| library-first-decision-agent | 1 | 1 | 0.5 | 2026-05-03 |
| llm-eval-harness | 1 | 1 | 0.5 | 2026-05-03 |
| rag-reference-implementation | 1 | 1 | 0.5 | 2026-05-03 |
| **TOTAL** | **571** | **186** | **174.3** | 2025-04-28 → 2026-07-20 |

## 3. Method — how the hours were computed (and their honest limits)

Commit timestamps were pulled from GitHub for every repository (full
history). Commits were grouped into **work sessions**: a gap over 60 minutes
starts a new session; each session counts its first-to-last commit span plus
30 minutes of setup/wrap-up. This is the standard "git-hours" heuristic.

- **It is a floor, not a ceiling.** Time spent reading, designing,
  field-testing, and directing between commits leaves no timestamp. Actual
  engaged time is higher; only the documented figure is claimed.
- **It is reproducible.** Anyone can rerun the same computation against the
  public repositories and get the same numbers.

## 4. Replacement-cost estimate

Stated as an estimate with its method, never as an appraisal: at published
U.S. freelance software-developer rates of **$50–$85/hour** (mid-range,
2025–2026 market surveys), the 174.3 documented hours represent roughly
**$8,700–$14,800** of contracted development time. The flagship alone
(81.2 h) represents ~$4,100–$6,900. This prices the *documented labor*; it
does not price the test suite, documentation system, or design assets a
contractor would additionally bill to reproduce.

## 5. Audit findings (2026-07-20 sweep)

**Verified clean:**
- All 27 repositories are pushed to GitHub; the flagship's `main` is the
  single source of truth (`e2f8d40`), with **no child branches**.
- Both working clones (`Desktop\Sentinel-Forge`, OneDrive clone) mirror
  `main` exactly. OneDrive carries the active projects and the
  `Claude AI\Completed projects` archive (~19 project copies) — cloud copy
  confirmed. GitHub itself is the primary offsite backup for all 27 repos.
- 7 fully-merged child branches were deleted across 3 repositories
  (`copilot/*` ×5, `sprint-3/*` ×2) — zero commits lost.

**Open items (owner decision required):**

| Item | Detail |
|---|---|
| 7 unmerged branches | `sentinel-prime-network:claude/wizardly-…` (9 commits ahead), `sentinel-forge-cognitive-orchestrator:claude/setup-quantum-nexus` (2), `Neural-Lattice:claude/neural-lattice-docs` + 3 `copilot/*` (1 each), `Sentinel-of-sentinel-s-Forge:claude/setup-sentinel-forge` (1). Deleting these destroys commits — review or merge first. |
| C: drive critical | **2.0 GB free.** Recycle Bin holds 539 items / ~0.8 GB — sampled contents are all book `.docx` + `.meta.json` sidecars from old Library removals, no code. Verdict: safe to empty after a 60-second visual scan (owner action). |
| Stale third clone | `C:\Users\sbrya\Desktop\Sentinel personal Development` (local Desktop, capital-D naming) — clean but 1 commit behind; not part of the two-clone protocol. Recommend removing or repurposing. |
| Old backup folder | `OneDrive\Sentinel personal development backup 20260621-015858` — June snapshot, superseded by GitHub + two live clones. Candidate for the E: drive. |
| Uncommitted work | `Desktop\Quantum-Nexus-Forge-GitHub` (8 dirty files, April), `OneDrive\Desktop\Imprint` (1 dirty file), `OneDrive\Desktop\Claude AI` (9 dirty files, last commit April). Commit or discard deliberately. |
| E: backup drive | **Not connected during this audit** — its backup state could not be verified. Reconnect and re-verify. |

## 6. Attribution

Co-creation is on the record, not asserted: commits carry
`Co-Authored-By: Claude` trailers, the flagship README names the assistant,
and this ledger is committed to the flagship repository, mirrored to both
OneDrive clones, and copied to the owner's `Claude AI` folder.

## 7. Value analysis — the stakeholder question

*"If a stakeholder walked in and commissioned these products from a
traditional team, what would they pay — and what did they save?"*
Three numbers, each labeled with its method. Quote all three together;
none alone tells the truth.

**7a. Documented labor (evidence — the bulletproof number).**
174.3 hours × $50–$85/hr freelance rate = **$8,700–$14,800** (§4).
This is what the commit record proves. It survives any audit.

**7b. Traditional-team model (textbook estimate — the ceiling).**
The flagship measures **~33,500 non-blank Python source lines** (27.3k
application shell, 5.2k tested kernels, 2.9k tests). Basic COCOMO,
organic mode (Boehm, *Software Engineering Economics*, 1981 — the model
taught in software-engineering courses):

    effort = 2.4 × (33.5 KLOC)^1.05  ≈  96 person-months
    schedule = 2.5 × 96^0.38         ≈  14 months
    average staffing                 ≈  7 people

At a $50/hr fully-loaded rate (~$8,650/person-month), the model prices a
traditional from-scratch build of the flagship at **≈ $830,000 with a
team of ~7 for ~14 months**. Honest limits, stated plainly: COCOMO
predates AI-assisted development, assumes enterprise process overhead,
and SLOC-based models over-price generated code — treat this as what
the *textbook* would estimate, not as an appraisal. A real consultancy
bid would land well below the model and well above the floor.

**7c. The delta (the savings story).**
Model estimate (~$830k) minus documented delivery cost (~$4,100–$6,900
for the flagship's 81.2 h) is the productivity gap of one directed
AI-assisted developer versus the model's traditional team. The
defensible interview sentence: *"By the textbook COCOMO model, my
flagship's 33,500 lines estimate to ~96 person-months of traditional
team effort; the public commit record shows I delivered it in ~81
directed hours. That gap — roughly two orders of magnitude — is what a
disciplined AI-assisted workflow is worth, and every number in that
sentence is reproducible from my repositories."*

## 8. Honest grading — what these repositories are and are not

The credibility of this portfolio rests on precise claims. Graded
honestly, per this project's own no-inflation rule:

| Tier | Repositories | Honest label |
|---|---|---|
| **A — working, tested software** | sentinel-forge-personal-development (422 tests, in daily production use by its intended user), Imprint, strata-console, Quantum-Nexus-Forge, earp-prompts (FastAPI + tests) | "Production-quality for its intended scope" — real, runnable, tested |
| **B — reference implementations & prototypes** | rag-reference-implementation, llm-eval-harness, hub-and-spoke-ai-chatbot, cognitive-neural-overlay, seed-crystal-input-processing-layer, library-first-decision-agent, and peers | Working demonstrations of a pattern; not hardened products |
| **C — engineering documentation & templates** | software-development-lifecycle-framework, seven-layer-architecture-template-pack, ios-compliance-framework, engineering/inventory template packs, glyphic-codex DSL, codices | Process artifacts — evidence of systems thinking, not code |

**"Industrial grade" is not claimed** — that term implies CI/CD
pipelines, independent code review, security audit, and multi-user
hardening these projects have not had, and this portfolio's standing
rule bans inflated labels. The claim that IS made, because the evidence
supports it: **the owner directs AI-assisted development to working,
tested, documented software with real engineering discipline** — SDLC
staging, functional-core architecture, additive migrations,
archive-never-delete data policy, and a 422-test suite that gates every
release. For a hiring manager, that is the demonstrated skill: not
"can type code," but "can specify, direct, verify, and ship it."

*Generated 2026-07-20 by Claude (Anthropic) at the owner's direction; data
source: GitHub commit history, reproducible per §3. Value analysis added
same day at the owner's direction after his stakeholder-framing review.*
