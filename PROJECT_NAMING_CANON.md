# Project Naming Canon

Use this note to keep names separated across parallel builds, published repos, and portfolio paperwork.

## Purpose

This canon is the source of truth for the canonical portfolio artifacts (currently nineteen: seventeen GitHub-published projects, one local-only by design, plus one v0.1.0 sibling demo). It exists to answer four questions before any public-facing naming change is made:

1. What is the canonical public project name?
2. What repo slug currently represents it on GitHub?
3. Which short forms are allowed?
4. Which neighboring names must stay separate?

## Naming Model

Use five levels when a system is named in docs:

1. parent network
2. platform
3. project or repo
4. component or subsystem
5. feature or workflow

Every active build must declare:

- `canonical_name`
- `repo_slug`
- `public_display_name`
- `approved_short_names`
- `forbidden_aliases`
- `parent_network`
- `identity_statement`

## Global Rules

- Repo slug may differ from public display name when changing the slug would be disruptive.
- README H1 must match the canonical public display name exactly.
- GitHub descriptions must reinforce the canon and must not introduce new aliases.
- If a repo slug differs from the canonical public display name, the README must explain the difference in the first screenful.
- `Nexus` alone is forbidden as a standalone project name or short form.
- `Sentinel` alone is forbidden unless the exact project or network is already explicit in the same sentence or header.
- `Forge` alone is forbidden unless the exact project is already explicit in the same sentence or header.
- `Sentinel Prime Network` and `Forge-Stack-A1` are related but not equivalent:
  - `Sentinel Prime Network` is the public project identity.
  - `Forge-Stack-A1` is the internal stack/workspace label for that build.

## Canon Registry

### 1. Sentinel-of-sentinel-s-Forge

- `canonical_name`: `Sentinel-of-sentinel-s-Forge`
- `repo_slug`: `Sentinel-of-sentinel-s-Forge`
- `public_display_name`: `Sentinel-of-sentinel-s-Forge`
- `approved_short_names`: `Sentinel-Forge`
- `forbidden_aliases`: `Sentinel Prime Network`, `Sentinel Forge Cognitive AI Orchestrator`, `Sovereign Forge`, `Nexus`
- `parent_network`: none
- `stack_tier`: full-stack (verified: `backend/` + `frontend/` + `frontend-app/` directories present)
- `identity_statement`: A production-oriented neurodivergent-aware AI orchestration platform built on FastAPI, Azure OpenAI, Cosmos DB, billing, and three-zone cognitive memory.
- `must_stay_separate_from`: `Sentinel Prime Network`, `Quantum Nexus Forge`, `Sovereign Forge`, `Sentinel Forge Cognitive AI Orchestrator`

### 2. Sentinel Prime Network

- `canonical_name`: `Sentinel Prime Network`
- `repo_slug`: `sentinel-prime-network`
- `public_display_name`: `Sentinel Prime Network`
- `approved_short_names`: `SPN`
- `forbidden_aliases`: `Forge-Stack-A1` as a public project name, `Quantum Nexus Forge`, `Nexus`, `SentinelForge AI` (separate canonical project)
- `parent_network`: none
- `stack_tier`: full-stack (3-tier: `01_BACK_END/` FastAPI + `02_MIDDLE_LAYER/` protocol/routing + `03_FRONT_END/` React JSX + dashboard spec)
- `identity_statement`: A local-first AI workstation and orchestration scaffold whose current build uses the internal stack/workspace label `Forge-Stack-A1`.
- `must_stay_separate_from`: `Sentinel-of-sentinel-s-Forge`, `Quantum Nexus Forge`, `Sovereign Forge`, `Sentinel Forge Cognitive AI Orchestrator`

### 3. Quantum Nexus Forge

- `canonical_name`: `Quantum Nexus Forge`
- `repo_slug`: `Quantum-Nexus-Forge`
- `public_display_name`: `Quantum Nexus Forge`
- `approved_short_names`: `Quantum Nexus Forge`, `Quantum Nexus` when the platform context is explicit
- `forbidden_aliases`: `Nexus`, `Sentinel`, `Sentinel Prime Network`
- `parent_network`: `Quantum Nexus`
- `stack_tier`: backend-with-html-dashboard (Python cognitive engine + live SVG visualization layer; no dedicated frontend framework)
- `identity_statement`: A standalone multi-agent orchestration MVP with symbolic routing, tri-zone memory, and a live SVG dashboard.
- `must_stay_separate_from`: `Sentinel Prime Network`, `Sentinel-of-sentinel-s-Forge`, `Sovereign Forge`, `Sentinel Forge Cognitive AI Orchestrator`

### 4. Sovereign Forge

- `canonical_name`: `Sovereign Forge`
- `repo_slug`: `Sovereign-Forge`
- `public_display_name`: `Sovereign Forge`
- `approved_short_names`: none
- `forbidden_aliases`: `Sentinel Forge`, `Quantum Nexus Forge`, `sentinel-forge-cognitive-orchestrator`
- `parent_network`: none
- `stack_tier`: backend-only (FastAPI gateway; no dedicated UI by design — UI lives in upstream projects)
- `identity_statement`: The capstone gateway project that fans requests to Quantum Nexus Forge and Sentinel-of-sentinel-s-Forge in parallel and merges the results.
- `must_stay_separate_from`: `Quantum Nexus Forge`, `Sentinel-of-sentinel-s-Forge`, `Sentinel Forge Cognitive AI Orchestrator`

### 5. Enterprise AI Reliability Platform v1

- `canonical_name`: `Enterprise AI Reliability Platform v1`
- `repo_slug`: `enterprise-ai-reliability-platform-v1`
- `public_display_name`: `Enterprise AI Reliability Platform v1`
- `approved_short_names`: `EARP`
- `forbidden_aliases`: `Enterprise readability AI Platform v1 Artificial Intelligence`, `Nexus`, `Sentinel`
- `parent_network`: none
- `stack_tier`: full-stack (FastAPI backend + React 18 + TypeScript + Vite frontend + Docker compose + Azure bicep deployment)
- `identity_statement`: A production-grade AI reliability and compliance platform centered on NIST AI RMF scoring, policy gating, audit history, and full-stack engineering discipline.
- `must_stay_separate_from`: `Sentinel Prime Network`, `Quantum Nexus Forge`, `Sovereign Forge`, `Sentinel Forge Cognitive AI Orchestrator`

### 6. Sentinel Forge Cognitive AI Orchestrator

- `canonical_name`: `Sentinel Forge Cognitive AI Orchestrator`
- `repo_slug`: `sentinel-forge-cognitive-orchestrator`
- `public_display_name`: `Sentinel Forge Cognitive AI Orchestrator`
- `approved_short_names`: `SFCO`
- `forbidden_aliases`: `Sentinel Forge Cognitive AI Orchestration Platform`, `Sovereign Forge`, `Sentinel-of-sentinel-s-Forge`
- `parent_network`: none
- `stack_tier`: backend-only (FastAPI + WebSocket streaming; consumes via API, no dedicated UI bundled)
- `identity_statement`: A neurodivergent-aware FastAPI orchestration system with three-zone memory, symbolic routing, and real-time cognitive-state streaming.
- `must_stay_separate_from`: `Sovereign Forge`, `Sentinel-of-sentinel-s-Forge`, `Sentinel Prime Network`, `Quantum Nexus Forge`

### 7. AI_Memory_Core

- `canonical_name`: `AI_Memory_Core`
- `repo_slug`: `AI_Memory_Core` (local-only; not GitHub-published by design)
- `public_display_name`: `AI_Memory_Core`
- `approved_short_names`: `AMC`, `Memory Core` (only when scope is explicit)
- `forbidden_aliases`: `Memory Core` (alone), `Cognitive Orchestration Kernel` (that is the marketing label; canonical name is `AI_Memory_Core`)
- `parent_network`: none
- `publication_status`: local-only by design (HIPAA-style privacy posture)
- `live_path`: `C:/Users/sbrya/OneDrive/Desktop/Claude AI/AI_Memory_Core/` (active library; written to during sessions)
- `archive_path`: `C:/Users/sbrya/OneDrive/Desktop/Completed projects/AI_Memory_Core/` (snapshot copy archived 2026-05-01 for portfolio parity)
- `archive_date`: 2026-05-01
- `stack_tier`: local-only (Python kernel; no HTTP server, no web UI by design — accessed via Python API and file system)
- `identity_statement`: A local-only Cognitive Orchestration Kernel running a three-tier persistent-memory architecture (Word/Excel/Access), an EBNF Symbolic Workflow DSL parser, a Knowledge Object Repository (39 KOs and growing), a three-tracker observability stack, and a binary steganography codec. Single source of truth for this project's library, archived snapshots, memory rules, and protocol files.
- `must_stay_separate_from`: `Sentinel-of-sentinel-s-Forge`, `Sentinel Prime Network`, `Quantum Nexus Forge`, `Sovereign Forge`, `Enterprise AI Reliability Platform v1`, `Sentinel Forge Cognitive AI Orchestrator`, `earp-prompts`

### 8. earp-prompts

- `canonical_name`: `earp-prompts`
- `repo_slug`: `earp-prompts`
- `public_display_name`: `earp-prompts`
- `approved_short_names`: none (canonical name is already short)
- `forbidden_aliases`: `EARP` alone (that is `Enterprise AI Reliability Platform v1`), `enterprise-ai-reliability-platform-v1`
- `parent_network`: none (sibling pattern-reuse of EARP, not a child or fork)
- `publication_status`: published 2026-04-30 — `https://github.com/coconuthead-Sentinel-core/earp-prompts` (public; 2 git commits, 16 tracked files, 18/18 pytest passing)
- `stack_tier`: backend-only at v0.1.0 (FastAPI + SQLAlchemy + SQLite + OpenAPI docs at `/docs`; React frontend is a v0.2 plan)
- `identity_statement`: An EARP-pattern application to LLM prompt quality scoring with NIST AI RMF MEASURE-function discipline. FastAPI + SQLAlchemy 2.x + SQLite + JWT/bcrypt + Pydantic v2. v0.1.0 ships 18 of 18 pytest tests passing on Windows in-memory SQLite with StaticPool. Sibling project to Enterprise AI Reliability Platform v1; EARP itself is unmodified.
- `must_stay_separate_from`: `Enterprise AI Reliability Platform v1`, `Sentinel-of-sentinel-s-Forge`, `Sentinel Prime Network`, `Quantum Nexus Forge`, `Sovereign Forge`, `Sentinel Forge Cognitive AI Orchestrator`, `AI_Memory_Core`

### 10. Neural Lattice Architecture and Workflow Optimization

- `canonical_name`: `Neural Lattice Architecture and Workflow Optimization`
- `repo_slug`: `Neural-Lattice-Architecture-and-Workflow-Optimization`
- `public_display_name`: `Neural Lattice Architecture and Workflow Optimization`
- `approved_short_names`: `Neural Lattice`, `NLA`
- `forbidden_aliases`: `Neural Lattice` (alone, when scope is ambiguous), `Cognitive Neural Overlay`, `Sentinel`, `Nexus`
- `parent_network`: none
- `publication_status`: published 2026-04-16 — `https://github.com/coconuthead-Sentinel-core/Neural-Lattice-Architecture-and-Workflow-Optimization` (public)
- `stack_tier`: documentation framework (no executable code; structured workflow / methodology repository)
- `identity_statement`: A structured, neurodiversity-aligned workflow framework that explains the Neural Lattice Architecture and its role in optimizing AI-supported project management.
- `must_stay_separate_from`: `Sentinel-of-sentinel-s-Forge`, `Sentinel Prime Network`, `Quantum Nexus Forge`, `Sovereign Forge`, `Enterprise AI Reliability Platform v1`, `Sentinel Forge Cognitive AI Orchestrator`, `AI_Memory_Core`, `earp-prompts`, `SentinelForge AI`

### 9. SentinelForge AI

- `canonical_name`: `SentinelForge AI`
- `repo_slug`: `SentinelForge-AI`
- `public_display_name`: `SentinelForge AI`
- `approved_short_names`: none
- `forbidden_aliases`: `Sentinel Prime Network` (different project; A1 is the local stack), `Sentinel-of-sentinel-s-Forge`, `Sentinel Forge Cognitive AI Orchestrator`
- `parent_network`: none
- `publication_status`: published 2026-05-01 — public GitHub repository (replaces local-only stack going forward)
- `stack_tier`: full-stack AI workstation and orchestration platform (will absorb / supersede the local Sentinel Prime Network stack as development continues)
- `identity_statement`: A full-stack AI workstation and orchestration platform applying enterprise-grade engineering discipline to neurodivergent-aware cognitive architecture.
- `must_stay_separate_from`: `Sentinel Prime Network`, `Sentinel-of-sentinel-s-Forge`, `Sentinel Forge Cognitive AI Orchestrator`, `Sovereign Forge`, `Quantum Nexus Forge`, `Enterprise AI Reliability Platform v1`, `AI_Memory_Core`, `earp-prompts`

### 11. Seven Layer Architecture Template Pack

- `canonical_name`: `Seven Layer Architecture Template Pack`
- `repo_slug`: `seven-layer-architecture-template-pack`
- `public_display_name`: `Seven Layer Architecture Template Pack`
- `approved_short_names`: `7-Layer Pack`
- `forbidden_aliases`: `7 Layer` (alone), `Seven Layer` (alone)
- `parent_network`: none
- `publication_status`: published 2026-05-01 — `https://github.com/coconuthead-Sentinel-core/seven-layer-architecture-template-pack` (public)
- `stack_tier`: methodology framework (twin template packs: 10 phase + 6 A2A/MCP)
- `identity_statement`: Twin governance + protocol template packs for full-stack AI engineering — Phase Pack (10 governance templates: ARC42, ADR/MADR, C4, NIST AI RMF, etc.) plus A2A/MCP Pack (6 protocol templates).
- `must_stay_separate_from`: all other canon entries

### 12. Engineering Project Build and Inventory Template Pack

- `canonical_name`: `Engineering Project Build and Inventory Template Pack`
- `repo_slug`: `engineering-project-build-and-inventory-template-pack`
- `public_display_name`: `Engineering Project Build and Inventory Template Pack`
- `approved_short_names`: `EPB Pack`
- `forbidden_aliases`: `Engineering Pack` (alone)
- `parent_network`: none
- `publication_status`: published 2026-05-01 — `https://github.com/coconuthead-Sentinel-core/engineering-project-build-and-inventory-template-pack` (public)
- `stack_tier`: methodology framework (9 templates for build tracking + signoff)
- `identity_statement`: 9-template methodology pack for tracking engineering project builds end-to-end — checklists, artifact inventories, and signoff scaffolding for production-grade software delivery.
- `must_stay_separate_from`: all other canon entries

### 13. Software Development Lifecycle Framework

- `canonical_name`: `Software Development Lifecycle Framework`
- `repo_slug`: `software-development-lifecycle-framework`
- `public_display_name`: `Software Development Lifecycle Framework`
- `approved_short_names`: `SDLC Framework`
- `forbidden_aliases`: `SDLC` (alone, when scope is ambiguous)
- `parent_network`: none
- `publication_status`: published 2026-05-01 — `https://github.com/coconuthead-Sentinel-core/software-development-lifecycle-framework` (public)
- `stack_tier`: methodology framework (canonical paperwork pack + lifecycle documentation)
- `identity_statement`: SDLC reference framework with canonical paperwork pack and lifecycle documentation for production AI engineering projects.
- `must_stay_separate_from`: all other canon entries

### 14. iOS Compliance Framework

- `canonical_name`: `iOS Compliance Framework`
- `repo_slug`: `ios-compliance-framework`
- `public_display_name`: `iOS Compliance Framework`
- `approved_short_names`: `iOS Compliance`
- `forbidden_aliases`: `Compliance` (alone)
- `parent_network`: none
- `publication_status`: published 2026-05-01 — `https://github.com/coconuthead-Sentinel-core/ios-compliance-framework` (public)
- `stack_tier`: methodology framework (compliance template shelf with checklists and pinned upstream paperwork)
- `identity_statement`: iOS compliance template shelf with blank checklists, reusable templates, and pinned upstream source paperwork for iOS submission and audit readiness.
- `must_stay_separate_from`: all other canon entries

### 16. Glyphic Codex 7system work-flow DSL

- `canonical_name`: `Glyphic Codex 7system work-flow DSL`
- `repo_slug`: `glyphic-codex-7system-work-flow-dsl`
- `public_display_name`: `Glyphic Codex 7system work-flow DSL`
- `approved_short_names`: `Glyphic Codex DSL`, `GC7 DSL`
- `forbidden_aliases`: `Codex` (alone), `Glyphic` (alone), `DSL` (alone)
- `parent_network`: none
- `live_path`: `Completed projects/Glyphic Codex 7system work-flow DSL/`
- `archive_date`: 2026-05-01
- `provenance`: promoted 2026-05-01 from non-aligned working folder `Desktop/backend/` (4 source files: text notes, bitmap, Microsoft Publisher layout, Microsoft Access database)
- `publication_status`: published 2026-05-01 — `https://github.com/coconuthead-Sentinel-core/glyphic-codex-7system-work-flow-dsl` (public, single `main` branch)
- `stack_tier`: methodology / concept package (4 source-artifact surfaces preserved as portfolio reference)
- `replacement_cost`: $3K – $12K (concept package; senior-architect time to recreate the 7-system DSL decomposition + four-surface source artifacts)
- `identity_statement`: Concept package and source artifacts for a 7-system glyph-driven workflow Domain-Specific Language — earlier exploratory work preserved as a verifiable portfolio reference.
- `must_stay_separate_from`: all other canon entries
- `2026-05-02_addition`: `reference/glyph_dsl.py` + `reference/glyph_codex.py` (stub) extracted from AI_Memory_Core — runnable parser, 227 lines, EBNF grammar; plus `INTEGRATION_PLAN.md` and `LICENSE_DECISION_ANALYSIS.md` documenting open items #4 and #5.
- `2026-05-03_addition`: `tests/test_pack_validation.py` — 14 tests passing, validates source artifacts + reference parser + plan docs.

### 19. Ancient Numerics Codex

- `canonical_name`: `Ancient Numerics Codex`
- `repo_slug`: `ancient-numerics-codex`
- `public_display_name`: `Ancient Numerics Codex`
- `approved_short_names`: `ANC`, `Numerics Codex`
- `forbidden_aliases`: `Numerology` (alone), `Numerics` (alone)
- `parent_network`: tooling library
- `live_path`: `Completed projects/Ancient Numerics Codex/`
- `archive_date`: 2026-05-03
- `publication_status`: published 2026-05-03 — `https://github.com/coconuthead-Sentinel-core/ancient-numerics-codex` (public, single `main` branch)
- `stack_tier`: **Python tooling library** (importable; no service)
- `tests`: **64 / 64 passing** in 0.89s
- `replacement_cost`: $4.5K – $14K (5 traditions + 3 primitives + unified codex API + 64 tests + classroom module)
- `identity_statement`: Five primordial mathematical traditions (Hebrew Gematria, Greek Isopsephy/Pythagorean, Arabic Abjad, Indian/Vedic numerology, Mesopotamian sexagesimal) packaged as composable Python primitives for AI-assisted code generation. Provides `glyph_id()` for NLCA-compatible doc_ids, `complexity_score()` for cognitive-load scoring, `encode_now_sexagesimal()` for Babylonian time-rendering. Built during autonomous sprint with full Master Grid annotation.
- `must_stay_separate_from`: all other canon entries
- `master_grid_annotation`: zone=GREEN | load=9 | protocols=P-01+P-02+P-03 | glyphs=📥→🔺→🔷→📤

### 17. Seed Crystal — Input Processing Layer

- `canonical_name`: `Seed Crystal — Input Processing Layer`
- `repo_slug`: `seed-crystal-input-processing-layer`
- `public_display_name`: `Seed Crystal — Input Processing Layer`
- `approved_short_names`: `Seed Crystal`, `Input Processing Layer`, `IPL`
- `forbidden_aliases`: `Crystal` (alone), `Seed` (alone), `Input` (alone)
- `parent_network`: integrated Master Grid platform (root)
- `live_path`: `Completed projects/Seed Crystal Input Processing Layer/`
- `archive_date`: 2026-05-02
- `genesis`: keynote-render image declared seed crystal by proprietor 2026-05-02; visual → code translation per `docs/SEED_GENESIS.md`
- `publication_status`: published 2026-05-02 — `https://github.com/coconuthead-Sentinel-core/seed-crystal-input-processing-layer` (public, single `main` branch)
- `stack_tier`: **backend service** (FastAPI + Pydantic v2; in-memory v0.1.0)
- `tests`: **34 / 34 passing**
- `boot_verified`: yes (uvicorn + curl smoke test confirmed `/healthz`, `/master-grid/contract`, `POST /input/event` end-to-end with 7 audit entries)
- `replacement_cost`: $7K – $20K (backend service with novel governance contract; ~1860 LOC + 34 tests)
- `identity_statement`: Root of the integrated Master Grid platform — first contact surface for every input. Enforces 7-layer execution contract at the boundary; native glyph DSL intake; immutable audit substrate.
- `must_stay_separate_from`: all other canon entries
- `integration_map`: Glyphic Codex DSL (#16), AI_Memory_Core (#7), Neural Lattice (#10), 7 Layer Architecture (#11), iOS Compliance (#14), SDLC Framework (#13), Hub and Spoke (#15)

### 18. Cognitive Neural Overlay (CNO)

- `canonical_name`: `Cognitive Neural Overlay`
- `repo_slug`: `cognitive-neural-overlay`
- `public_display_name`: `Cognitive Neural Overlay (CNO)`
- `approved_short_names`: `CNO`, `Cognitive Overlay`
- `forbidden_aliases`: `Cognitive` (alone), `Overlay` (alone), `Neural` (alone)
- `parent_network`: Sentient Quantum Architecture v8.0 (SQA)
- `sibling_components`: A1 Filing System (graph-based knowledge vault), Nexus Node Stack (layered cognitive task orchestration)
- `live_path`: `Completed projects/Cognitive Neural Overlay/` (TBD this cycle)
- `archive_date`: 2026-05-03
- `provenance`: derived from `a Cognitive neural overlay a1 (1).txt` (85 KB SQA v8.0 design doc) + `(2).txt` (Sentinel Forge System Core Directive with 5-node simulated overlay) + 4 codex.bmp/diag_cno_codex_v1 visual references discovered during full-laptop sweep
- `publication_status`: scaffolded 2026-05-03; pending GitHub push this cycle
- `stack_tier`: backend service / front-end overlay (5 modular nodes: Input, Router, Memory, Persona, OutputSynth)
- `replacement_cost`: $8K – $25K (production-grade cognitive overlay; integrates with Seed Crystal Layer 1 as the cognitive co-processor)
- `identity_statement`: Structured-symbolic processing + emotional appraisal subsystem of the SQA v8.0 architecture. Implements 5 simulated nodes (Input/Router/Memory/Persona/OutputSynth) as the cognitive overlay between Input Processing Layer and downstream services.
- `must_stay_separate_from`: all other canon entries (especially #10 Neural Lattice — different concept; NLCA is zone-based runtime, CNO is symbolic-emotional overlay)
- `integration_map`: Seed Crystal #17 (provides input feed), Neural Lattice #10 (provides zone substrate), Glyphic Codex DSL #16 (provides node-tagging vocabulary), AI_Memory_Core #7 (long-term memory persistence)

### 15. Hub and Spoke AI Chatbot

- `canonical_name`: `Hub and Spoke AI Chatbot`
- `repo_slug`: `hub-and-spoke-ai-chatbot`
- `public_display_name`: `Hub and Spoke AI Chatbot`
- `approved_short_names`: `Hub and Spoke`, `H&S Chatbot`
- `forbidden_aliases`: `Chatbot` (alone), `Hub` (alone), `Spoke` (alone)
- `parent_network`: none
- `live_path`: `Completed projects/Hub and spoke. AI Chatbot/`
- `archive_date`: 2026-05-01
- `publication_status`: published 2026-05-01 — `https://github.com/coconuthead-Sentinel-core/hub-and-spoke-ai-chatbot` (public, single `main` branch)
- `stack_tier`: methodology / concept package (content surfaces: Archive, Build, creative ideas/prompts, Doc, Exports)
- `replacement_cost`: $4.5K – $15K (concept package; senior-architect time to recreate the hub-and-spoke decomposition + content surfaces)
- `identity_statement`: Hub-and-spoke architecture concept package for an AI chatbot — earlier portfolio piece preserving the original working notes and content surfaces as a reference artifact.
- `must_stay_separate_from`: all other canon entries

## Naming Crosswalk

| canonical name | repo slug | README title | approved short names | forbidden aliases | notes |
|---|---|---|---|---|---|
| Sentinel-of-sentinel-s-Forge | `Sentinel-of-sentinel-s-Forge` | `Sentinel-of-sentinel-s-Forge` | `Sentinel-Forge` | `Sentinel Prime Network`, `Sentinel Forge Cognitive AI Orchestrator`, `Nexus` | Repo slug and public display match. |
| Sentinel Prime Network | `sentinel-prime-network` | `Sentinel Prime Network` | `SPN` | `Forge-Stack-A1` as public product name, `Nexus`, `SentinelForge AI` (separate project) | `Forge-Stack-A1` is the internal stack/workspace label. Distinct from `SentinelForge AI` (canon #9). |
| Quantum Nexus Forge | `Quantum-Nexus-Forge` | `Quantum Nexus Forge` | `Quantum Nexus Forge`, `Quantum Nexus` when scoped | `Nexus` | `Quantum Nexus` may appear only when the platform context is explicit. |
| Sovereign Forge | `Sovereign-Forge` | `Sovereign Forge` | none | `Sentinel Forge`, `Quantum Nexus Forge` | Gateway project, not a downstream alias. |
| Enterprise AI Reliability Platform v1 | `enterprise-ai-reliability-platform-v1` | `Enterprise AI Reliability Platform v1` | `EARP` | `Enterprise readability AI Platform v1 Artificial Intelligence` | `EARP` is approved only for this project. |
| Sentinel Forge Cognitive AI Orchestrator | `sentinel-forge-cognitive-orchestrator` | `Sentinel Forge Cognitive AI Orchestrator` | `SFCO` | `Sentinel Forge Cognitive AI Orchestration Platform` | Public display uses `Orchestrator`, not `Orchestration Platform`. |
| AI_Memory_Core | `AI_Memory_Core` (local-only) | `AI_Memory_Core` | `AMC`, `Memory Core` (when scoped) | `Memory Core` (alone), `Cognitive Orchestration Kernel` | Local-only by design; not on GitHub. Single source of truth for library, archives, memory rules. |
| earp-prompts | `earp-prompts` | `earp-prompts` | none | `EARP` (alone), `enterprise-ai-reliability-platform-v1` | EARP-pattern sibling; EARP itself unmodified. v0.1.0 published 2026-04-30 at `https://github.com/coconuthead-Sentinel-core/earp-prompts` (public; 18/18 tests passing). |
| SentinelForge AI | `SentinelForge-AI` | `SentinelForge AI` | none | `Sentinel Prime Network`, `Sentinel-of-sentinel-s-Forge` | Public GitHub repo published 2026-05-01. Separate canonical project from `Sentinel Prime Network` (canon #2). |
| Neural Lattice Architecture and Workflow Optimization | `Neural-Lattice-Architecture-and-Workflow-Optimization` | `Neural Lattice Architecture and Workflow Optimization` | `Neural Lattice`, `NLA` | `Neural Lattice` (alone), `Cognitive Neural Overlay` | Public GitHub repo published 2026-04-16. Documentation/methodology framework, not an executable project. |
| Hub and Spoke AI Chatbot | `hub-and-spoke-ai-chatbot` | `Hub and Spoke AI Chatbot` | `Hub and Spoke`, `H&S Chatbot` | `Chatbot` (alone), `Hub` (alone), `Spoke` (alone) | Public GitHub repo published 2026-05-01 with single `main` branch. Concept package, not executable. |
| Glyphic Codex 7system work-flow DSL | `glyphic-codex-7system-work-flow-dsl` | `Glyphic Codex 7system work-flow DSL` | `Glyphic Codex DSL`, `GC7 DSL` | `Codex` (alone), `Glyphic` (alone), `DSL` (alone) | Public GitHub repo published 2026-05-01 with single `main` branch. Promoted from non-aligned `Desktop/backend/` folder; 4 source-artifact surfaces preserved. |
| Seed Crystal — Input Processing Layer | `seed-crystal-input-processing-layer` | `Seed Crystal — Input Processing Layer` | `Seed Crystal`, `IPL` | `Crystal` (alone), `Seed` (alone), `Input` (alone) | Public GitHub repo published 2026-05-02 with single `main` branch. Root of integrated Master Grid platform; 34/34 tests passing; boot-verified. Generated from a keynote-render image declared seed crystal by the proprietor. |

## Maintenance Rules

- Before publishing a new project, define canonical name, parent network, approved short names, and forbidden aliases here.
- Fix the highest-visibility surfaces first when drift appears: GitHub description, README H1, first-screenful identity text, portfolio brief, and release/polish notes.
- Use neutral fallback wording such as `the project` or the repo slug if a document is in progress and the canon has not been updated yet.
- Do not rename public repo slugs by default. Update the canon and public display surfaces first, then evaluate whether a slug change is still necessary.
- If a document compares projects, it must use the canonical public display name or an approved short name exactly as listed above.
