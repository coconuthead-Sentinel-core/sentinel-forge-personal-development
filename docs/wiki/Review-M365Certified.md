# Clinical Review — *Microsoft 365 Certified* books → Sentinel Forge

> Top-down review of the 4-file M365 certification set — *Fundamentals
> (MS-900)* + *Collaboration Communications Systems Engineer (MS-721)*
> (~759K chars, 30+ chapters) — against one question: **what here is
> canonical, worldwide-taught computer science that adds to Sentinel
> Forge — additively, no teardown, professor-approvable?** Gate honored:
> reviewed and proven in pseudocode before any feature code.
> Reviewed 2026-07-12.

## What the books are

Certification study guides for **administering Microsoft 365**: cloud
computing, deployment models (IaaS/PaaS/SaaS), M365 components,
security/compliance/identity, and (MS-721) Teams — meetings, call flows,
auto attendants, call queues, network QoS. Most of it is Microsoft cloud
administration and exam prep — not transferable computer science.

## Part-by-part verdict

| Area | Verdict | Why |
| --- | --- | --- |
| Cloud models, M365 components, Teams admin, call flows, QoS, licensing, exam-objective walkthroughs | **SKIP** | Product administration + exam prep. A local, offline study app has no place for cloud/tenant config; not CS coursework. |
| Compliance, retention, governance, conditional-access policy | **SKIP-ish** | Policy evaluation overlaps the ECA engine already built (`lyceum/automation.py`); nothing new to add. |
| **Identity & security: password policy, MFA, entropy of secrets** | **BUILD** | The canonical CS foundation under "password strength" is **Shannon entropy** (information theory) — the single most universally-taught algorithm in the field. A strength estimator is a real, bounded, testable kernel, and purely local (fits the local-first ethos). **This is the pick.** |

## The BUILD: `lyceum/password_strength.py` — Shannon-entropy strength

**What it is (the CS, and why every professor recognizes it).** Shannon
entropy (Claude Shannon, 1948) — the number of BITS of information in a
string — is the foundation of information theory, taught in every CS
program worldwide and strictly academic. The module computes two
textbook entropy estimates and takes the attacker-favorable minimum:

```pseudocode
search_space_bits(s) = len(s) * log2(charset_size(s))     # brute-force view
shannon_bits(s)      = ( -Σ p(c)*log2 p(c) ) * len(s)     # information content
                       # penalizes "aaaaaaaa" (low distribution entropy)
strength(s):
    bits = min(search_space_bits, shannon_bits)
    if s is a known-common password: bits = ~8   # effectively free
    band  = Very weak | Weak | Reasonable | Strong | Very strong
    tips  = actionable guidance (length, character classes, uniqueness)
    return {bits, band, crack_time, tips, ...}
```

**Why it's professor-approvable, additive, and safe.**
- **Canonical & academic.** Shannon entropy is *the* information-theory
  algorithm — no university would blink; a senior engineer expects it
  exact, and it is (proofs below match the closed-form values).
- **Book-grounded.** The MS-900 identity/security material (password
  policies, MFA, security defaults) is exactly this topic.
- **Privacy by design.** A pure function: NO storage, NO network, NO
  logging. It analyzes a candidate string locally and returns a score —
  it never authenticates anywhere and never persists the input (the
  standard strength-meter design, e.g. zxcvbn). This matches Sentinel
  Forge's local-first, nothing-leaves-the-laptop ethos.
- **Architecture.** Pure logic, no Tkinter, deterministic → drops into
  `lyceum/` beside `formula.py`, `readability.py`, `prompt_coach.py`,
  `automation.py`. Additive: a NEW file; a small optional utility
  window; zero edits to existing behavior.

## Proof (pseudocode tested BEFORE any real coding — the gate)

Prototype `scratchpad/entropy_proto.py`, three proofs, **20 checks all
pass**:
1. **Entropy math is textbook-exact** — 8 lowercase chars = `8·log2(26)`
   = 37.60 bits; charset detection (26 / 62 / 94); Shannon entropy of
   `"aaaa"` = 0, `"ab"` = 2 bits, `"abcd"` = 8 bits — all matching the
   closed-form values.
2. **Discrimination** — repeated chars ("aaaaaaaa") and short inputs
   score weak; a long mixed passphrase scores Strong (82.7 bits); a
   known-common password ("password") is flagged and pinned to ~8 bits.
3. **Determinism, edges, safety** — deterministic; empty input safe;
   bits ≥ 0 always; longer random input yields more bits; tips are
   actionable; the function returns a plain dict and stores nothing.

## Recommendation & scope

- **Phase 1 (ready to build):** `lyceum/password_strength.py` +
  `tests/test_password_strength.py`, surfaced as a small **🔒 Password
  Strength** utility (live bits + band + one tip as you type; nothing
  stored). Smallest safe surface; explicitly local/private.
- **Out of scope:** cloud/tenant admin, Teams, call flows, exam-prep
  content, and any real credential handling — the tool only *estimates*
  strength of a candidate string locally; it never authenticates or
  stores anything.

Gate satisfied: review complete, pseudocode proven (20/20). Awaiting the
Architect's go to begin Phase 1.
