# Feature Catalog

*Every user-facing feature mapped to the method that builds it and the table(s)
it persists to. Reviewed 2026-06-27 against `aea48c8`. Search the `open_*` /
`_*` names in
[`sentinel_personal_development.py`](https://github.com/coconuthead-Sentinel-core/sentinel-forge-personal-development/blob/main/sentinel_personal_development.py).*

## A. Reading & accessibility (the core mission)

| Feature | Builder / methods | Persists to |
| --- | --- | --- |
| Open & read `.docx/.pdf/.md/.txt/.rtf/.html` | `open_file`, `_load_book`, `_extract_text`, `_extract_*_with_chapters` | — (files) |
| Chapter / page navigation | `_detect_chapters_from_text`, `_populate_chapter_list`, `_jump_to_selected_chapter` | — |
| Read-aloud (Piper / SAPI5), sentence/word/paragraph highlight | `_init_tts`, `_ftb_read_toggle` (CC 58), `_ftb_paint_read_highlight` | — |
| **Read-aloud text normalization** ($, %, ordinals, abbrevs) | `lyceum/text_norm.py: normalize_for_speech` | — |
| Dockable floating toolbar | `_init_floating_toolbar`, `_floating_toolbar_dock_to`, `_ftb_*` | toolbar state file |
| Text sizing, OpenDyslexic overlay, 8 highlight colors | `bigger_text`, `smaller_text`, `_on_font_change`, `_on_highlight_color_change` | — |
| **Offline Whisper voice dictation** (Fast/Accurate/Best) | dictation worker + `_append_dictation` | `voice_corrections` |
| **Hands-free spoken commands** (punctuation, caps, new line) | `lyceum/dictation_commands.py: apply_dictation_commands` | — |
| Voice Memory correction dictionary | dictation path | `voice_corrections` |
| Saved excerpts (Markdown + YAML front-matter, zone-tagged) | `open_library`, `_set_zone`, `_save_meta` | `*.md` files + `highlights` |
| Zone-tagged Library (GREEN/YELLOW/RED filter) | `open_library`, `_load_meta`, `_doc_id_for` | `*.md.meta.json` |

## B. Onboard AI assistant

| Feature | Builder / methods | Backed by |
| --- | --- | --- |
| Chat assistant (auto-reads replies aloud) | `open_ai_chat`, `_build_tab_ai_chat` | `ai_brain.py` (Ollama) |
| "Explain selection" tutor | `_ai_explain_selection` → `LocalBrain.explain` | grounded prompt, temp 0.3 |
| Web-search context injection | `_ai_web_search_context` | optional |
| Cross-excerpt "Ask Library" search | platform integration (localhost) | external platform |

## C. Study workspace & dashboard

| Feature | Builder | Tables |
| --- | --- | --- |
| Major Definite Purpose marquee | `edit_major_purpose`, `_mdp_*` | (config) |
| Blue-Sky Vision Board + slideshow | `open_vision_board`, `_play_vision` | `vision_images` |
| V2MOM "Why" engine (Why+Obstacles required) | `open_v2mom`, `_v2mom_save` | `v2mom_goals` |
| Daily 10 Goals (rewrite from memory) | `open_ten_goals`, `_ten_goals_streak` | `goal_journal` |
| 💼 Job Readiness audit (six-pillar rubric, next-move engine) | `open_job_readiness`, `_job_ready_last_check`, `lyceum/job_readiness.py` | `job_readiness_checks` |
| Systems & Checklists (A→B→Z) | `open_systems`, `_system_progress`, `_system_next_step` | `systems`, `system_steps` |
| Back-From-The-Future PERT planner | `open_pert`, `_pert_schedule`, `_draw_pert_timeline` | `pert_plans`, `pert_steps` |
| Lead vs. Lag (4DX) | `open_lead_lag` | `lead_measures`, `lag_measures`, `lead_measure_marks` |
| Habit Stacker + 2-Minute Rule | `open_habits`, `_habit_streak` | `habits`, `habit_marks` |
| Never-Miss-Twice streak tracker | `open_streak_tracker`, `_fireworks` | `habit_marks` |
| Eisenhower Matrix + Pomodoro ticker | matrix builders | `eisenhower`, `matrix_pomodoros`, `matrix_task_log` |
| Sunsama-style weekly Planner | planner builders | `planner_tasks`, `day_blocks` |
| Weekly Roles (Covey Q-II) | roles builder | `weekly_roles` |
| Idea Warehouse (ABCDE, Big-Three) | `open_idea_warehouse` (CC 60) | `master_tasks` |
| Not-To-Do list + site blocker | not-to-do builder | `not_to_do` |
| Wheel of Life (7 spokes, roundness trend) | wheel builder + `lyceum/metrics.wheel_progress` | `wheel_of_life` |
| Goals panel (honest baseline→target progress) | `_build_goals_panel` (CC 66) + `lyceum/metrics.goal_progress` | `goals`, `goal_checkins` |
| Winner's Time Log (chime + weekly pie) | `_start_time_auditor`, `_draw_time_pie` | `time_log` |
| After-Action Review (daily reflection) | `open_after_action_review` | `daily_review` |
| 5-4-3-2-1 Momentum → Focus Mode | momentum button | — |
| Session Start / End wizards (handoff) | `open_session_start_wizard`, `open_session_end_wizard` | `HANDOFF_STATE.json` |
| Appointments + Windows reminders (T-60/-30/-15) | appointment builders, `lyceum/reminders.py`, `reminder_flash.py` | `appointments` |

## D. Finance suite (~20 tools)

Each is a behavioral-finance concept turned into a panel. Builders are
`open_*`; see [Database Schema](Database-Schema.md#finance-suite) for tables.

| Tool | Builder | Concept (author) |
| --- | --- | --- |
| Pay Yourself First | `open_pay_yourself_first` | Clason/Bach — save first, lock it |
| Core Four (Defense Mode) | `open_core_four` | survival budget 2×2 |
| Money Hub | `open_money_hub`, `_money_snapshot` | one-glance dashboard |
| Spending ledger | `open_expense_tracker`, `_draw_spending_chart` | Millionaire Next Door |
| Latte Factor | `open_latte_factor` | Bach — small leaks |
| Dream Buckets | `open_dream_buckets`, `_draw_dream_bar` | Ramsey — save for big buys |
| Wishlist (7-day delay) | `open_wishlist` | impulse cooling |
| Run Rate (emergency fund battery) | `open_run_rate`, `_draw_battery` | Tracy Law of Three |
| Time Cost | `open_time_money`, `_time_cost_hours` | price = hours of life |
| Save More Tomorrow | `open_save_more_tomorrow`, `_wedge_split` | Thaler/Benartzi wedge |
| Compound Simulator | `open_compound_simulator`, `_draw_doubling_ladder` | Rule of 72 |
| Expected Net Worth (PAW/UAW) | `open_net_worth`, `_draw_wealth_gauge` | age×income/10 |
| Three-Bucket Allocator | `open_asset_buckets` | Robbins security/growth/dream |
| All Seasons Portfolio | `open_all_seasons`, `_draw_alloc_pie` | Dalio All-Weather |
| Hidden Fee Checker | `open_fee_checker`, `_draw_fee_bars` | expense-ratio drag |
| Critical Mass (decumulation) | `open_critical_mass`, `_years_until_depleted` | safe-withdrawal |
| Zero-Based / KWINK audit | `_run_zero_based_audit`, `open_subscription_audit` | Tracy sunk-cost cure |
| Bill Sentinel | `open_bill_sentinel` + pure kernel `lyceum/bills.py` (`classify`, `next_action`) | prospective-memory scaffold; autopay = goal state (Thaler & Benartzi 2004) |

> **Note for maintainers:** the finance suite is the largest contributor to
> `BookReader`'s method count. If/when the God Object is decomposed, each
> `open_*` family is a natural seam to lift into its own module (mirror the
> `lyceum/` pattern) — the pure math (`_compound_series`, `_critical_mass`,
> `_wedge_split`, `_fee_future_value`) extracts cleanly and is highly testable.
