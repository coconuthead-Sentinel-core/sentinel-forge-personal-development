# Post-v0.9 Voice I/O Feature Track (PARKED — behind the freeze)

> **STATUS: BACKLOG. Do not start until v0.9 is signed off** (`docs/ACCEPTANCE_CRITERIA.md`).
> Everything here is a *new feature*, not v0.9 hardening. Logged so the research
> isn't lost. Reviewed 2026-06-27 against `main`.

## Provenance & integrity note

These five recipes came from an external research assistant (Gemini) and were
**generated from model training, not live web research** (the reply stated *"No
external web-queries executed"*) — so they carry **no citations**. Every recipe
below was vetted by Claude Code against the actual libraries and our codebase;
the **fixes and license flags are the result of that review**, not the original
reply. Re-verify the NVDA license and any pinned versions before implementing.

## License hygiene rule (applies to everything here)

- **Embed as source only if permissive** (MIT/BSD/Apache/PSF/public-domain).
- **Copyleft (GPL/LGPL) tools** — e.g. NVDA's controller DLL, eSpeak-NG — are used
  **only as a separate process / load-if-present system DLL**, never vendored into
  our MIT source. We already follow this for Piper/eSpeak.

---

## Recipe 1 — Low-latency command-and-control (Vosk)

- **Benchmark:** Dragon NaturallySpeaking command mode.
- **License:** Vosk **Apache-2.0** — embed-safe.
- **Net-new?** Yes — a *second* STT engine + a second model download (~50 MB)
  alongside faster-whisper. Biggest commitment in this track.
- **Correct integration (revised):** the mic-streaming loop is **I/O = imperative
  shell**, NOT pure — it does **not** belong in `lyceum/`. Split it:
  - pure, testable **command/grammar matcher** → `lyceum/stt_command.py`
  - mic loop + Vosk recognizer → the GUI shell (next to the Whisper path).
- **Risk:** strict grammar fails silently on out-of-vocabulary words; small models
  struggle with accents. Pin to our existing `sounddevice>=0.5.0` (the reply's
  `0.4.6` is older than ours).
- **Priority:** 3 (only if push-to-talk Whisper proves too slow for commands).

## Recipe 2 — Windows-native TTS for the onboard assistant (SAPI5 via pywin32)

- **Benchmark:** Windows Narrator / Voice Access TTS.
- **License:** pywin32 PSF; SAPI5 is OS infrastructure — license-clean.
- **Net-new?** Partly redundant — we already drive SAPI, currently via a
  **PowerShell subprocess** (`_sapi_select_voice_ps`). This is a *cleaner* direct-COM
  re-implementation, and it **adds a pywin32 dependency** we currently avoid.
- **⚠ Bug to fix before use:** the reply's "optional dependency guard" is wrong —
  `win32com.client.Dispatch(...)` raises `pywintypes.com_error`, **not
  `ImportError`**, and a missing pywin32 fails at the top-level `import` first.
  Correct pattern: guard the **import** with `try/except ImportError`, and catch
  `Exception` around `Dispatch`.
- **Correct integration:** `lyceum/sapi_tts.py` (a small, guarded wrapper); decide
  whether it **replaces** the PowerShell-SAPI path or we simply keep using Piper.
- **Priority:** 1 (smallest; lets the onboard AI speak).

## Recipe 3 — Screen-reader announcement (NVDA controller via ctypes)

- **Benchmark:** JAWS/NVDA dynamic announcement.
- **License:** ⚠️ **GPL / uncertain — VERIFY NV Access's terms first.** Safe pattern:
  `ctypes.LoadLibrary` the `nvdaControllerClient*.dll` **only if already present on
  the user's machine**; **never bundle/ship it.** Then we ship zero GPL code and
  just talk to the user's installed screen reader by IPC.
- **APIs:** `nvdaController_testIfRunning` / `nvdaController_speakText` are real.
  Minor: set `ctypes` argtypes for the wide-string text rather than relying on
  implicit conversion.
- **Net-new?** Yes — but only benefits users running NVDA.
- **Correct integration:** `lyceum/accessibility_bridge.py` (guarded, load-if-present).
- **Priority:** 2 (small, but license-gated).

## Recipe 4 — Synchronized read-aloud highlighting

- **Verdict: ❌ SKIP — already shipped, and ours is better.** We already do
  sentence/word follow-along highlighting (`_ftb_paint_read_highlight` + the
  floating-toolbar read engine). The reply's version re-`tag_configure`s every call
  and clears `1.0→END` per word, and its `gui/reader_pane.py` path doesn't match our
  single-file structure. Nothing to do.

## Recipe 5 — Duplex voice loop (STT → local LLM → TTS)

- **Benchmark:** conversational voice assistant.
- **License:** MIT (our orchestration).
- **⚠ Won't run as-is:** it calls `self.llm.generate(text, stream=True)`, which our
  `ai_brain.LocalBrain` **does not have** — `ask()`/`explain()` return a full string
  with no streaming. **Prerequisite:** add a real streaming method to `LocalBrain`
  (Ollama supports `stream=True`). It also names a non-existent `ai_brain/duplex_loop.py`
  package path (our `ai_brain.py` is a single module). Good architecture sketch;
  not drop-in. Implement the thread `Event` locks it admits it needs.
- **Correct integration:** extend `ai_brain.py` (add `LocalBrain.stream(...)`),
  then a shell-side orchestrator.
- **Priority:** 4 (last; depends on the streaming method existing first).

---

## Recommended sequence (when the freeze lifts)

1. **Recipe 2** — SAPI5 onboard-assistant speech (smallest; fix the import guard).
2. **Recipe 3** — NVDA announce (small; verify the license first, never bundle the DLL).
3. **Recipe 1** — Vosk command mode (split pure matcher from the mic loop).
4. **Recipe 5** — Duplex loop (after `LocalBrain.stream()` exists).
5. **Recipe 4** — dropped (already implemented, better).

## Definition of "ready to start this track"

- [ ] v0.9 acceptance signed off (`docs/ACCEPTANCE_CRITERIA.md`).
- [ ] NVDA controller-client license verified (for Recipe 3).
- [ ] Each new capability lands as an **optional dependency** (guarded import) and,
      where possible, with its decision logic as a **pure, tested** `lyceum/` module.
