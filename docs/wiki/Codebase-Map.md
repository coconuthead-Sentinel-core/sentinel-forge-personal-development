# Codebase Map

*Reviewed 2026-06-27 against `aea48c8`. Line numbers are approximate and drift
as the file changes — use them as a starting offset, then search by method name.*

## Top-level layout

```
sentinel-forge-personal-development/
├── sentinel_personal_development.py  ← the entire GUI app (one BookReader class)
├── ai_brain.py                       ← onboard local AI (Ollama wrapper)
├── lyceum/                           ← the pure, tested functional core
│   ├── db/study_db.py                ← SQLite schema + transaction()
│   ├── metrics.py                    ← progress math
│   ├── text_norm.py                  ← read-aloud text normalization
│   ├── dictation_commands.py         ← spoken-punctuation parser
│   ├── reminders.py                  ← Windows scheduled-task reminders
│   └── reminder_flash.py             ← the OpenDyslexic alert window
├── tests/                            ← 34 unit tests (run headless)
│   ├── test_metrics.py
│   ├── test_transactions.py
│   ├── test_text_norm.py
│   └── test_dictation_commands.py
├── docs/
│   ├── SDLC_STATUS.md                ← methodology & life-cycle declaration
│   └── build-inventory/              ← 8 engineering build/inventory templates
├── scripts/                          ← build & install PowerShell + helpers
│   ├── build_exe.ps1                 ← one-command PyInstaller build
│   ├── install_book_reader_shortcut.ps1
│   ├── install_tts.ps1               ← downloads Piper + en_US-amy voice
│   └── make_sentinel_icon.py
├── Sentinel-Forge.spec               ← PyInstaller one-folder build spec
├── requirements.txt                  ← optional-dependency manifest
├── run_sentinel.bat / *_debug.bat    ← no-console / console launchers
└── README.md
```

> **Naming note.** Older docs and the README quick-start refer to
> `book_reader.py` / `run_book_reader.bat`. The live entry point is
> **`sentinel_personal_development.py`** (run via `run_sentinel.bat`). This is a
> documented historical rename; if you see `book_reader.py` in a doc, read it as
> the same app. Reconciling those references is an open doc-cleanup item.

## `sentinel_personal_development.py` — the `BookReader` class

One class, ~590 methods. It is large but it is *organized by feature*: methods
for a feature cluster together, and almost every panel follows the same shape —
a public `open_*()` builder that creates a Toplevel window, with nested
`_close()`, `_render()`, `_save()`, `_recompute()` closures inside it.

### Module-level helpers (before the class)

| Symbol | Role |
| --- | --- |
| `_vlog(msg)` | Lightweight debug logger (writes `voice_debug.log`) |
| `_style_optionmenu(om)` | Consistent dark styling for Tk `OptionMenu` |
| `_phonetic_key(word)` | Soundex-style key for the spelling helper |

### Subsystem map inside `BookReader`

Read this as "where do I go to change X." Each row is a cluster of related
methods.

| Subsystem | Entry points (search these names) | Notes |
| --- | --- | --- |
| **App bootstrap / dashboard** | `__init__`, `_on_dash_*`, `btn`, `section` | Builds the scrolling dashboard; wires every button |
| **Floating read-aloud toolbar** | `_init_floating_toolbar`, `_build_floating_toolbar_widgets`, `_floating_toolbar_dock*`, `_ftb_*` | Dockable TTS toolbar; **`_ftb_read_toggle` is the highest-complexity method (CC 58)** and the continuous-highlight engine |
| **Text sizing / fonts / voices** | `smaller_text`, `bigger_text`, `_on_font_change`, `_on_voice_change`, `_installed_sapi_voice_names` | Accessibility sizing + SAPI5 voice selection |
| **Notes & clipboard** | `_load_notes`, `_save_notes`, `_copy_selection_to_notes`, `_build_notes_context_menu` | Autosaving study notes |
| **TTS engine** | `_init_tts`, `_ftb_read_toggle`, `_ps_single_quote` | Piper/SAPI read-aloud; sentence-by-sentence highlight |
| **File loading & parsing** | `open_file`, `_load_book`, `_extract_text`, `_extract_*_with_chapters`, `_detect_chapters_from_text`, `_chunk_evenly` | docx/pdf/html/txt/md parsing + chapter detection |
| **Library & zones** | `open_library`, `_ensure_book_in_library`, `_meta_path_for`, `_load_meta`, `_set_zone` | GREEN/YELLOW/RED zone-tagged excerpt vault |
| **Session continuity** | `open_session_start_wizard`, `open_session_end_wizard`, `_load_handoff_state`, `_save_handoff_state` | Writes `HANDOFF_STATE.json` |
| **AI assistant** | `open_ai_chat`, `_build_tab_ai_chat`, `_ai_explain_selection`, `_ai_web_search_context` | Talks to `ai_brain.py`; auto-reads replies |
| **Time auditor** | `_start_time_auditor`, `_time_audit_prompt`, `_log_time`, `open_time_log`, `_draw_time_pie` | "Winner's Time Log" chime + weekly pie |
| **Goal & habit system** | `open_ten_goals`, `open_systems`, `open_habits`, `open_streak_tracker`, `open_lead_lag`, `_habit_streak` | Daily goals, A→B→Z systems, streaks, 4DX |
| **Planning** | `open_pert`, `open_v2mom`, `open_vision_board`, `_pert_schedule` | Back-from-the-future PERT, V2MOM, vision board |
| **Finance suite** | `open_pay_yourself_first`, `open_core_four`, `open_money_hub`, `open_compound_simulator`, `open_critical_mass`, `open_net_worth`, … | ~20 financial tools (see [Feature Catalog](Feature-Catalog.md)) |
| **Reflection** | `open_after_action_review`, `_review_load`, `_review_save` | Daily AAR |

### The recurring panel idiom

Almost every `open_*()` follows this template — recognizing it lets you read any
panel in seconds:

```python
def open_thing(self):
    win = tk.Toplevel(self.root); ...           # create window
    def _close(): win.destroy()                 # teardown
    def _render(*_): ...                         # paint current DB state → widgets
    def _save(): db_exec(...); _render()         # persist, then repaint
    def _recompute(*_): ...                       # derived numbers on input change
    _render()                                     # initial paint
```

## `ai_brain.py` — onboard local AI

A single `LocalBrain` class wrapping **Ollama** (default model `llama3.2:3b`).

- `.available` is False if the `ollama` package, daemon, or model is missing →
  `ask()` returns `None`, callers degrade.
- `num_ctx` defaults to **2048** deliberately (the 128K default OOMs small
  machines — the KV cache grows with context length); `keep_alive="10m"` keeps
  the model warm so only the first call pays the cold-load cost.
- `explain()` uses a low temperature (0.3) and a **grounding system prompt**
  ("do NOT add facts beyond the selection") — the anti-hallucination guardrail.
- Shared lazy singleton via `get_brain()` so the whole app uses one warm model.

## `lyceum/` — the functional core

See [Architecture](Architecture.md) and [Database Schema](Database-Schema.md). Each
module is pure (no Tk), defensive (never raises on bad input), and unit-tested:

| Module | Public surface |
| --- | --- |
| `metrics.py` | `progress_pct`, `wheel_progress`, `goal_progress` |
| `text_norm.py` | `normalize_for_speech` |
| `dictation_commands.py` | `apply_dictation_commands` |
| `db/study_db.py` | `init_study_db`, `connect`, `db_query`, `db_exec`, `transaction` |
| `reminders.py` / `reminder_flash.py` | Windows per-user scheduled reminders + alert UI |
