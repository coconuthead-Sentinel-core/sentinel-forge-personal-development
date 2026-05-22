"""
book_reader.py — Memory Cube Book Reader
=========================================

A real native Windows desktop application. No browser, no web server,
no API, no internet. One window, big buttons, big readable text,
and a Save-for-Claude button that writes excerpts to disk for the
next Claude session to read.

Run:
    py book_reader.py
or after PyInstaller build:
    BookReader.exe
"""
from __future__ import annotations
import json
import os
import queue
import re
import shutil
import sqlite3
import sys
import subprocess
import tempfile
import threading

# Optional: send2trash sends deleted files to the Windows Recycle Bin
# instead of permanently unlinking them. The Library 🗑 Remove button
# uses this when available so accidental deletes are recoverable.
try:
    from send2trash import send2trash  # type: ignore
    HAS_SEND2TRASH = True
except ImportError:
    HAS_SEND2TRASH = False

# Optional: tkinterdnd2 lets the Library window accept drag-and-drop
# files from Explorer. Falls back gracefully to the dialog-only path
# if not installed.
try:
    from tkinterdnd2 import TkinterDnD, DND_FILES  # type: ignore
    HAS_DND = True
except ImportError:
    HAS_DND = False
    DND_FILES = None  # for the bind() reference site
from datetime import datetime, date, timedelta
from pathlib import Path

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from tkinter import font as tkfont

# ---- File parsers --------------------------------------------------------
try:
    from docx import Document
    HAS_DOCX = True
except Exception:
    HAS_DOCX = False

try:
    import pypdf
    HAS_PDF = True
except Exception:
    HAS_PDF = False

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except Exception:
    HAS_BS4 = False

# ---- Text-to-speech ------------------------------------------------------
try:
    import pyttsx3
    HAS_TTS = True
except Exception:
    HAS_TTS = False


# ---- Where excerpts go ---------------------------------------------------
EXCERPTS_DIR_CANDIDATES = [
    r"C:\Users\sbrya\OneDrive\Desktop\Claude AI\AI_Memory_Core\excerpts",
    r"C:\Users\sbrya\OneDrive\Desktop\Claude AI\Completed projects\AI_Memory_Core\excerpts",
]
EXCERPTS_DIR = next(
    (p for p in EXCERPTS_DIR_CANDIDATES if os.path.isdir(os.path.dirname(p))),
    EXCERPTS_DIR_CANDIDATES[1],
)
# Notes file lives next to the excerpts folder
NOTES_FILE = os.path.join(os.path.dirname(EXCERPTS_DIR), "notes.md")

# ---- Where books live by default ----------------------------------------
DEFAULT_BOOKS_DIR = r"C:\Users\sbrya\OneDrive\Desktop\Books"

# The "library" is just this folder, scanned recursively. Files live on
# disk under your normal Books folder so OneDrive backs them up
# automatically and you can also drop files in via Explorer.
# Storage limit = whatever your OneDrive plan and local disk allow.
# We don't impose any artificial cap (no max-file-size, no max-count).
LIBRARY_DIR = DEFAULT_BOOKS_DIR

# Commentaries live in a SEPARATE subfolder so they don't mix with
# regular books. e-Sword's design lesson: typed content (Bible vs.
# Commentary vs. Dictionary) lives in different files. The Library
# scan below explicitly prunes this subfolder, and the Commentary
# picker only ever looks here.
COMMENTARIES_DIR = os.path.join(DEFAULT_BOOKS_DIR, "Commentaries")

# Extensions the reader knows how to extract text from. Keep this in
# sync with `_extract_text`. Anything outside this set is ignored when
# the library is scanned. .docx covers Microsoft Word AND Google Docs
# exported as Word; .pdf covers Google Docs exported as PDF.
SUPPORTED_EXTS = (".txt", ".md", ".docx", ".pdf", ".rtf", ".html", ".htm")

# ---- Three-Zone Library metadata ---------------------------------------
# Borrowed wholesale from the Sentinel Prime Network spec
# (snapshots/Forge-Stack-A1/01_BACK_END/zone_rules.md.txt).
# Every file in LIBRARY_DIR gets a sidecar `<file>.meta.json` carrying its
# zone (GREEN=active, YELLOW=reference, RED=archive) and a cognitive_load
# (1–10). The sidecar is lazy-created on first scan so existing libraries
# don't need manual migration. Excerpts saved by 💾 Save are ALSO stamped
# with a YAML front-matter block inside the .md file so the saved content
# is self-describing when read in any plain-text viewer.
META_SUFFIX       = ".meta.json"
LIBRARY_ZONES     = ("GREEN", "YELLOW", "RED")
LIBRARY_ZONE_DEFAULT = "GREEN"
LIBRARY_ZONE_EMOJI = {"GREEN": "🟢", "YELLOW": "🟡", "RED": "🔴"}
LIBRARY_ZONE_COLOR = {"GREEN": "#2ecc71", "YELLOW": "#f1c40f", "RED": "#e74c3c"}
# Recommended cognitive-load defaults per zone (spec quote: GREEN 7–10,
# YELLOW 4–6, RED 1–3).
LIBRARY_ZONE_LOAD_DEFAULT = {"GREEN": 8, "YELLOW": 5, "RED": 2}
LIBRARY_ZONE_LOAD_RANGE   = {"GREEN": (7, 10), "YELLOW": (4, 6), "RED": (1, 3)}

# ---- Study workspace storage --------------------------------------------
# Design borrowed from e-Sword: source content (books) lives separately
# from user content (highlights/bookmarks/topics/glossary/journal). Here
# everything that's "yours" goes into a single SQLite database that
# OneDrive backs up automatically. Highlights and bookmarks are anchored
# to a (book_key, char_offset) pair, so they survive re-opens.
STUDY_DIR = os.path.expanduser(r"~\OneDrive\Documents\BookReader")
STUDY_DB  = os.path.join(STUDY_DIR, "study.db")
# Session Header state: cognitive load (1–10), derived zone, last-seen
# timestamp. Persisted to JSON so the topbar slider remembers across
# launches. Spec source: snapshots/Forge-Stack-A1/03_FRONT_END/
# session_start_template.md.txt.
SESSION_STATE_PATH = os.path.join(STUDY_DIR, "session.json")
# Cross-session handoff (Sentinel Prime spec: session_end_template.md.txt
# + AGENTS.md model). Every Session End wizard writes this; every
# Session Start wizard reads it and shows last session's handoff message.
HANDOFF_STATE_PATH = os.path.join(STUDY_DIR, "HANDOFF_STATE.json")
# Piper neural TTS — much higher quality than SAPI; runs as a subprocess
# (so a native crash there doesn't take the app down) and ships as a tiny
# binary + one voice model under book-reader/tts/.
_BR_BASE      = os.path.dirname(os.path.abspath(__file__))
PIPER_EXE     = os.path.join(_BR_BASE, "tts", "piper.exe")
PIPER_VOICE   = os.path.join(_BR_BASE, "tts", "voices", "en_US-amy-medium.onnx")
HAS_PIPER     = os.path.exists(PIPER_EXE) and os.path.exists(PIPER_VOICE)
# Audit rubric grade vocabulary (Walkenbach / A1 course pattern).
AUDIT_GRADES = ("A+", "A", "A−", "B+", "B", "B−",
                "C+", "C", "C−", "D", "F", "n/a", "")

# Workflow folders — each row in the `workflow_folders` table maps 1:1
# to a real directory under WORKFLOW_DIR. Files uploaded via "+ Add
# files…" get copied into the folder on disk so they're easy to back up
# (OneDrive is already syncing this path) and easy to open in their
# native apps.
WORKFLOW_DIR = os.path.join(STUDY_DIR, "Workflow")
WORKFLOW_COLOR_EMOJI = {"green": "🟢", "yellow": "🟡", "red": "🔴"}
# Office formats the file-picker recommends by default. The picker
# still offers an "All files" option, so this is just an opinionated
# default, not a hard restriction.
WORKFLOW_OFFICE_GLOB = ("*.docx *.doc *.docm *.xlsx *.xls *.xlsm "
                        "*.pptx *.ppt *.pptm *.one *.vsdx *.mpp "
                        "*.pub *.accdb *.mdb")
# Extensions that get auto-imported when the user picks a folder via
# "+ Add folder…". Top-level files only — subfolders are skipped to
# avoid surprise recursive imports.
WORKFLOW_IMPORT_EXTS = (
    ".docx", ".doc", ".docm", ".dotx",
    ".xlsx", ".xls", ".xlsm", ".xlsb",
    ".pptx", ".ppt", ".pptm",
    ".one", ".onetoc2",
    ".vsdx", ".vsd",
    ".mpp",
    ".pub",
    ".accdb", ".mdb",
    ".pdf", ".txt", ".md", ".rtf",
    ".csv", ".tsv",
    ".html", ".htm",
    ".png", ".jpg", ".jpeg", ".gif", ".bmp",
)


# ---- Color palette (matches the dashboard) ------------------------------
BG_DARK    = "#0f172a"
BG_PANEL   = "#1e293b"
BG_INPUT   = "#0b1220"
FG_TEXT    = "#f1f5f9"
FG_MUTED   = "#94a3b8"
ACCENT_CYAN   = "#0891b2"
ACCENT_GREEN  = "#16a34a"
ACCENT_PURPLE = "#7c3aed"
ACCENT_RED    = "#dc2626"
ACCENT_SLATE  = "#475569"
ACCENT_MIC    = "#0ea5e9"   # mic button idle (sky-blue); turns red while recording
ACCENT_AMBER  = "#d97706"   # paste-from-clipboard button
ACCENT_PINK   = "#db2777"   # save-for-Claude button


def _style_optionmenu(om: tk.OptionMenu) -> None:
    """Force an OptionMenu to honor the dark palette. The default ttk
    styling on Windows renders comboboxes nearly invisible against the
    dark panel — that's why the highlight controls "disappear"."""
    om.configure(
        bg=BG_INPUT, fg=FG_TEXT,
        activebackground=ACCENT_SLATE, activeforeground="white",
        font=("Segoe UI", 11, "bold"),
        highlightthickness=1, highlightbackground=ACCENT_SLATE,
        bd=0, anchor="w", relief=tk.FLAT,
    )
    om["menu"].configure(
        bg=BG_INPUT, fg=FG_TEXT,
        activebackground=ACCENT_SLATE, activeforeground="white",
    )


class BookReader:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title("Sentinel Forge")
        root.geometry("1100x780")
        root.configure(bg=BG_DARK)
        # Try to give the window a sensible minimum size
        root.minsize(720, 480)

        # ---- New-feature state (Three-Zone Library, Session Header,
        # Start/End wizards, Audit tab, Prompts tab) ------------------
        # These must be initialized BEFORE the dashboard widgets are
        # built, because the Session Header UI reads self._cognitive_load
        # during construction. Keeping them all together at the top
        # avoids the "attribute X doesn't exist" class of bug when
        # widgets fire callbacks mid-construction.
        # Three-Zone Library
        self._library_zone_filter: str | None = None   # None = "All"
        self._library_zone_filter_btns: dict[str, tk.Button] = {}
        # Session Header (cognitive load + protocol indicators)
        self._cognitive_load: int = 7
        self._cognitive_load_var: tk.IntVar | None = None
        self._cognitive_load_label: tk.Label | None = None
        self._cognitive_zone_chip: tk.Label | None = None
        self._protocol_labels: dict[str, tk.Label] = {}
        self._load_session_state()
        # Session Start / End wizards (Toplevel singletons)
        self._session_start_win: tk.Toplevel | None = None
        self._session_end_win:   tk.Toplevel | None = None
        # Audit tab
        self._audit_listbox: tk.Listbox | None = None
        self._audit_items: list[tuple[int, str]] = []
        self._audit_current_id: int | None = None
        self._audit_title_var: tk.StringVar | None = None
        self._audit_subject_var: tk.StringVar | None = None
        self._audit_overall_var: tk.StringVar | None = None
        self._audit_mentors_widget: tk.Text | None = None
        self._audit_findings_frame: tk.Frame | None = None
        self._audit_finding_widgets: list[dict] = []
        self._audit_save_after_id: str | None = None
        # Prompt journal tab
        self._prompts_listbox: tk.Listbox | None = None
        self._prompts_items: list[tuple[int, str, str]] = []
        self._prompts_current_id: int | None = None
        self._prompts_fields: dict[str, tk.Widget] = {}
        self._prompts_save_after_id: str | None = None

        # ---- Scrollable dashboard container ----------------------------
        # When the user bumps system font size for readability, the
        # toolbar + controls + status + body + hint stack can grow
        # taller than the screen. That used to push the Notes panel
        # off the bottom with no way to reach it. Wrapping everything
        # in a Canvas + vertical Scrollbar gives a visible "drag bar"
        # on the right edge so the whole dashboard can be panned up
        # and down. Mouse-wheel scrolls the dashboard too, except when
        # the cursor is hovering over an inner scrollable widget (the
        # reader text, notes, commentary, listboxes) — those keep
        # their normal wheel behavior.
        dash_holder = tk.Frame(root, bg=BG_DARK)
        dash_holder.pack(fill=tk.BOTH, expand=True)
        dash_canvas = tk.Canvas(
            dash_holder, bg=BG_DARK, highlightthickness=0, bd=0,
        )
        dash_vsb = tk.Scrollbar(
            dash_holder, orient=tk.VERTICAL,
            command=dash_canvas.yview,
        )
        dash_canvas.configure(yscrollcommand=dash_vsb.set)
        dash_vsb.pack(side=tk.RIGHT, fill=tk.Y)
        dash_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        dash = tk.Frame(dash_canvas, bg=BG_DARK)
        dash_window_id = dash_canvas.create_window(
            (0, 0), window=dash, anchor="nw",
        )

        def _on_dash_inner_configure(_event):
            # Whenever the inner frame's natural size changes, refresh
            # the scrollable region so the scrollbar can reach the bottom.
            dash_canvas.configure(scrollregion=dash_canvas.bbox("all"))

        def _on_dash_canvas_configure(event):
            # Match inner-frame width to the canvas so widgets resize
            # horizontally as the window stretches. If the canvas is
            # taller than the inner frame's natural height, stretch the
            # inner frame to fill — that preserves the body's
            # expand=True behavior on big windows.
            dash_canvas.itemconfig(dash_window_id, width=event.width)
            try:
                natural_h = dash.winfo_reqheight()
            except tk.TclError:
                natural_h = 0
            if event.height > natural_h:
                dash_canvas.itemconfig(dash_window_id, height=event.height)
            else:
                # Let the inner frame keep its natural size — scrollbar engages.
                dash_canvas.itemconfig(dash_window_id, height=natural_h)

        dash.bind("<Configure>", _on_dash_inner_configure)
        dash_canvas.bind("<Configure>", _on_dash_canvas_configure)

        # Mouse-wheel handler. Walks up the widget tree under the
        # cursor and:
        #   - skips wheel events that belong to a Toplevel window
        #     (Library, Study workspace, modal dialogs) so scrolling
        #     in those doesn't accidentally pan the main dashboard,
        #   - skips wheel events when the cursor is over an inner
        #     scrollable widget (Reader, Notes, Commentary, listboxes)
        #     so those keep their native wheel behavior,
        #   - otherwise scrolls the dashboard canvas.
        def _on_dash_mousewheel(event):
            try:
                w = root.winfo_containing(event.x_root, event.y_root)
            except tk.TclError:
                return
            if w is None:
                return
            cur = w
            saw_inner_scrollable = False
            while cur is not None:
                if isinstance(cur, (tk.Text, tk.Listbox)):
                    saw_inner_scrollable = True
                if cur is root:
                    break
                if isinstance(cur, tk.Toplevel) and cur is not root:
                    return  # event belongs to another window
                try:
                    cur = cur.master
                except Exception:
                    return
            else:
                return  # walked off the top without finding root
            if saw_inner_scrollable:
                return  # let the Text/Listbox handle it natively
            dash_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        root.bind_all("<MouseWheel>", _on_dash_mousewheel)

        # ---- Session Header --------------------------------------------
        # Persistent strip above the action topbar. Cognitive load (1–10)
        # is the master control — it drives the zone indicator and the
        # Joy Protocol chip, and is read by the Library on open to set
        # its default zone filter. Spec: snapshots/Forge-Stack-A1/
        # 03_FRONT_END/session_start_template.md.txt + dashboard_spec.md.
        session_bar = tk.Frame(dash, bg=BG_PANEL, padx=12, pady=8,
                                highlightbackground=BG_DARK,
                                highlightthickness=0)
        session_bar.pack(fill=tk.X)

        tk.Label(session_bar, text="Energy:", bg=BG_PANEL, fg=FG_MUTED,
                 font=("Segoe UI", 10, "bold")
                 ).pack(side=tk.LEFT, padx=(0, 6))
        self._cognitive_load_var = tk.IntVar(value=self._cognitive_load)
        load_slider = tk.Scale(
            session_bar, from_=1, to=10, orient=tk.HORIZONTAL,
            showvalue=False, length=180, sliderlength=18,
            variable=self._cognitive_load_var,
            bg=BG_PANEL, fg=FG_TEXT,
            troughcolor=BG_INPUT, activebackground=ACCENT_CYAN,
            highlightthickness=0, borderwidth=0,
            command=lambda v: self._set_cognitive_load(int(float(v))),
        )
        load_slider.pack(side=tk.LEFT)
        self._cognitive_load_label = tk.Label(
            session_bar, text=f"{self._cognitive_load}/10",
            bg=BG_PANEL, fg=FG_TEXT,
            font=("Segoe UI", 11, "bold"), width=5,
        )
        self._cognitive_load_label.pack(side=tk.LEFT, padx=(6, 14))

        # Zone chip — color and label derived from the current load.
        _initial_zone = self._zone_for_load(self._cognitive_load)
        self._cognitive_zone_chip = tk.Label(
            session_bar,
            text=f"{LIBRARY_ZONE_EMOJI[_initial_zone]} {_initial_zone} ZONE",
            bg=LIBRARY_ZONE_COLOR[_initial_zone], fg="white",
            font=("Segoe UI", 10, "bold"), padx=10, pady=3,
        )
        self._cognitive_zone_chip.pack(side=tk.LEFT, padx=(0, 16))

        # Protocol indicators (Onset Omega 1 + Joy + Coconut Head).
        # Joy lights up at load ≥ 7; the other two are always on per
        # protocol_activation.md.
        self._protocol_labels = {}
        def proto_chip(key: str, text_on: str, text_off: str, active: bool):
            lbl = tk.Label(
                session_bar,
                text=text_on if active else text_off,
                bg=ACCENT_GREEN if active else ACCENT_SLATE, fg="white",
                font=("Segoe UI", 9, "bold"), padx=8, pady=2,
            )
            lbl.pack(side=tk.LEFT, padx=2)
            self._protocol_labels[key] = lbl
        proto_chip("omega",   "Ω1 ✓",          "Ω1",          True)
        proto_chip("joy",     "🥥 Joy ✓",      "🥥 Joy",
                    self._cognitive_load >= 7)
        proto_chip("coconut", "🧠 Coconut ✓",  "🧠 Coconut",  True)

        # Right side: date stamp + Session Start / End wizard launchers.
        tk.Label(
            session_bar,
            text=date.today().strftime("%a · %Y-%m-%d"),
            bg=BG_PANEL, fg=FG_MUTED, font=("Segoe UI", 10),
        ).pack(side=tk.RIGHT, padx=(8, 0))
        tk.Button(
            session_bar, text="⏹ End",
            command=self.open_session_end_wizard,
            bg=ACCENT_SLATE, fg="white",
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT, padx=10, pady=4,
            cursor="hand2", borderwidth=0,
        ).pack(side=tk.RIGHT, padx=2)
        tk.Button(
            session_bar, text="▶ Start",
            command=self.open_session_start_wizard,
            bg=ACCENT_GREEN, fg="white",
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT, padx=10, pady=4,
            cursor="hand2", borderwidth=0,
        ).pack(side=tk.RIGHT, padx=2)

        # ---- Top action bar --------------------------------------------
        topbar = tk.Frame(dash, bg=BG_PANEL, padx=12, pady=12)
        topbar.pack(fill=tk.X)

        def btn(parent, text, cmd, color, w=None):
            b = tk.Button(
                parent, text=text, command=cmd,
                font=("Segoe UI", 13, "bold"),
                bg=color, fg="white", activebackground=color,
                relief=tk.FLAT, padx=18, pady=10, cursor="hand2",
                borderwidth=0,
            )
            if w: b.configure(width=w)
            b.pack(side=tk.LEFT, padx=4)
            return b

        btn(topbar, "📂  Open",              self.open_file,            ACCENT_CYAN)
        btn(topbar, "📚  Library",           self.open_library,         ACCENT_PURPLE)
        btn(topbar, "📋  Paste",             self.paste_text,           ACCENT_AMBER)
        btn(topbar, "🔊  Read aloud",        self.read_aloud,           ACCENT_GREEN)
        btn(topbar, "■  Stop",               self.stop_reading,         ACCENT_SLATE)
        self.mic_btn = btn(topbar, "🎤  Voice note", self.toggle_mic,   ACCENT_MIC)
        btn(topbar, "💾  Save",              self.save_excerpt,         ACCENT_PINK)
        btn(topbar, "📓  Study",             self.open_study_workspace, ACCENT_RED)

        # Right side: font picker + text-size buttons
        right_frame = tk.Frame(topbar, bg=BG_PANEL)
        right_frame.pack(side=tk.RIGHT)

        # Dyslexia-friendly font picker
        installed = set(tkfont.families())
        # Preference order: OpenDyslexic if present, then research-backed fallbacks
        # (Comic Sans MS and Verdana are repeatedly cited in dyslexia research)
        preferred = [
            "OpenDyslexic",
            "OpenDyslexic3",
            "Atkinson Hyperlegible",
            "Comic Sans MS",
            "Verdana",
            "Tahoma",
            "Arial",
            "Segoe UI",
        ]
        self.available_fonts = [f for f in preferred if f in installed]
        if not self.available_fonts:
            self.available_fonts = ["Segoe UI"]
        self.font_family = self.available_fonts[0]   # first available = best for dyslexia

        tk.Label(right_frame, text="Font:", bg=BG_PANEL, fg=FG_MUTED,
                 font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=(0, 4))
        self.font_var = tk.StringVar(value=self.font_family)
        font_menu = tk.OptionMenu(
            right_frame, self.font_var, *self.available_fonts,
            command=self._on_font_change,
        )
        _style_optionmenu(font_menu)
        font_menu.configure(width=18)
        font_menu.pack(side=tk.LEFT, padx=(0, 12))

        tk.Label(right_frame, text="Text:", bg=BG_PANEL, fg=FG_MUTED,
                 font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=(0, 4))
        btn(right_frame, "A−", self.smaller_text, ACCENT_SLATE)
        btn(right_frame, "A+", self.bigger_text, ACCENT_SLATE)

        # ---- Highlight controls (color + unit) -------------------------
        # Three reading-friendly highlight colors. Indigo is muted so the
        # text underneath stays readable on the dark theme.
        self.HIGHLIGHT_COLORS = {
            "Yellow": "#fde047",
            "Teal":   "#5eead4",
            "Indigo": "#a5b4fc",
        }
        self.HIGHLIGHT_UNITS = ["Word", "Sentence", "Paragraph"]

        controls_row = tk.Frame(dash, bg=BG_PANEL, padx=12, pady=8)
        controls_row.pack(fill=tk.X)

        tk.Label(controls_row, text="Highlight by:", bg=BG_PANEL, fg=FG_TEXT,
                 font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT, padx=(0, 6))
        self.highlight_unit_var = tk.StringVar(value="Sentence")
        unit_menu = tk.OptionMenu(
            controls_row, self.highlight_unit_var, *self.HIGHLIGHT_UNITS,
        )
        _style_optionmenu(unit_menu)
        unit_menu.configure(width=11)
        unit_menu.pack(side=tk.LEFT, padx=(0, 18))

        tk.Label(controls_row, text="Color:", bg=BG_PANEL, fg=FG_TEXT,
                 font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT, padx=(0, 6))
        self.highlight_color_var = tk.StringVar(value="Yellow")
        color_menu = tk.OptionMenu(
            controls_row, self.highlight_color_var, *list(self.HIGHLIGHT_COLORS.keys()),
            command=self._on_highlight_color_change,
        )
        _style_optionmenu(color_menu)
        color_menu.configure(width=8)
        color_menu.pack(side=tk.LEFT)

        # Quick action — highlight current selection in the picked color.
        # Persistent (saved across sessions) for any book loaded from disk.
        tk.Button(
            controls_row, text="🖍  Highlight selection",
            command=lambda: self.highlight_selection(),
            font=("Segoe UI", 11, "bold"),
            bg=ACCENT_AMBER, fg="white", activebackground=ACCENT_AMBER,
            relief=tk.FLAT, padx=12, pady=6, cursor="hand2", borderwidth=0,
        ).pack(side=tk.LEFT, padx=(14, 0))

        # ---- Reading timer (Pomodoro-style, 5 / 10 / 15 / 20 / 25 min)
        # Lives on the right side of the controls row. Visual order is
        # "⏱ Timer:  [preset ▾]  [Start]   MM:SS" — we pack right-to-left
        # so the countdown sits on the far right and stays in view.
        self._timer_presets: dict[str, int] = {
            "5 min":  5, "10 min": 10, "15 min": 15,
            "20 min": 20, "25 min": 25,
        }
        self.timer_display_var = tk.StringVar(value="00:00")
        tk.Label(
            controls_row, textvariable=self.timer_display_var,
            bg=BG_PANEL, fg=FG_TEXT, font=("Consolas", 13, "bold"),
            padx=8,
        ).pack(side=tk.RIGHT)
        self.timer_button = tk.Button(
            controls_row, text="Start", command=self.toggle_timer,
            font=("Segoe UI", 11, "bold"),
            bg=ACCENT_GREEN, fg="white", activebackground=ACCENT_GREEN,
            relief=tk.FLAT, padx=12, pady=6, cursor="hand2", borderwidth=0,
        )
        self.timer_button.pack(side=tk.RIGHT, padx=(6, 8))
        self.timer_preset_var = tk.StringVar(value="10 min")
        preset_menu = tk.OptionMenu(
            controls_row, self.timer_preset_var, *self._timer_presets.keys(),
        )
        _style_optionmenu(preset_menu)
        preset_menu.configure(width=8)
        preset_menu.pack(side=tk.RIGHT, padx=(0, 6))
        tk.Label(
            controls_row, text="⏱  Timer:", bg=BG_PANEL, fg=FG_TEXT,
            font=("Segoe UI", 11, "bold"),
        ).pack(side=tk.RIGHT, padx=(20, 6))

        # ---- Status line -----------------------------------------------
        self.status_var = tk.StringVar(value="Click 📂  Open a book to begin.")
        self.status = tk.Label(
            dash, textvariable=self.status_var, anchor=tk.W,
            font=("Segoe UI", 11), padx=12, pady=8,
            bg=BG_DARK, fg=FG_MUTED,
        )
        self.status.pack(fill=tk.X)

        # ---- Main split: book text on the left, notes on the right ----
        self.font_size = 16
        body = tk.PanedWindow(
            dash, orient=tk.HORIZONTAL, sashwidth=6,
            bg=BG_DARK, bd=0, sashrelief=tk.FLAT,
            # Default vertical size keeps the body usable even inside the
            # scrollable container; expand=True still lets it grow when
            # the window is taller than the natural stack.
            height=580,
        )
        body.pack(fill=tk.BOTH, expand=True, padx=10, pady=4)

        # Left side — book text
        text_frame = tk.Frame(body, bg=BG_DARK)
        self.text_area = scrolledtext.ScrolledText(
            text_frame, wrap=tk.WORD,
            font=(self.font_family, self.font_size),
            bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT,
            padx=20, pady=20, relief=tk.FLAT,
            selectbackground="#1d4ed8", selectforeground="white",
            undo=True, autoseparators=True, maxundo=-1,
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)
        # Make it clear the user can select text
        self.text_area.bind("<Control-a>", self._select_all)
        # Right-click context menu — gives Cut/Copy/Paste an obvious affordance.
        self._build_text_context_menu()
        # Reading guide — highlights the chunk currently being spoken.
        # Color and chunk size are user-selectable via the topbar controls.
        self.text_area.tag_configure(
            "reading",
            background=self.HIGHLIGHT_COLORS[self.highlight_color_var.get()],
            foreground="#0f172a",
        )
        # Make the reading tag win over the built-in selection highlight so
        # the yellow line stays visible when reading selected text.
        self.text_area.tag_raise("reading", "sel")

        # ---- Right column: chapter navigator on top, Notes underneath
        # The chapter navigator is the e-Sword-inspired addition — its
        # header shows the current book's title (rather than a static
        # "Bible Books" label) and clicking a chapter scrolls the reader
        # to that offset. The list is rebuilt whenever a new book loads.
        right_pane = tk.PanedWindow(
            body, orient=tk.VERTICAL, sashwidth=6,
            bg=BG_DARK, bd=0, sashrelief=tk.FLAT,
        )

        # Chapter navigator
        chapters_frame = tk.Frame(right_pane, bg=BG_DARK)
        chapter_header = tk.Frame(chapters_frame, bg=BG_PANEL, padx=8, pady=6)
        chapter_header.pack(fill=tk.X)
        self.chapter_title_var = tk.StringVar(value="📖  No book open")
        tk.Label(
            chapter_header, textvariable=self.chapter_title_var,
            bg=BG_PANEL, fg=FG_TEXT, font=("Segoe UI", 11, "bold"),
            anchor=tk.W,
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        cl_frame = tk.Frame(chapters_frame, bg=BG_DARK)
        cl_frame.pack(fill=tk.BOTH, expand=True)
        self.chapter_listbox = tk.Listbox(
            cl_frame, bg=BG_INPUT, fg=FG_TEXT,
            selectbackground=ACCENT_CYAN, selectforeground="white",
            font=("Segoe UI", 11), relief=tk.FLAT, bd=0,
            highlightthickness=0, activestyle="none",
        )
        cl_sb = tk.Scrollbar(cl_frame, command=self.chapter_listbox.yview)
        self.chapter_listbox.configure(yscrollcommand=cl_sb.set)
        cl_sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.chapter_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # Single-click jumps; double-click and Enter also jump for keyboard nav.
        self.chapter_listbox.bind("<<ListboxSelect>>", self._jump_to_selected_chapter)
        self.chapter_listbox.bind("<Double-Button-1>", self._jump_to_selected_chapter)
        self.chapter_listbox.bind("<Return>",          self._jump_to_selected_chapter)

        # Notes panel (unchanged, just re-parented to right_pane)
        notes_frame = tk.Frame(right_pane, bg=BG_DARK)
        notes_header = tk.Frame(notes_frame, bg=BG_PANEL, padx=8, pady=6)
        notes_header.pack(fill=tk.X)
        tk.Label(notes_header, text="📝 Notes", bg=BG_PANEL, fg=FG_TEXT,
                 font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT)
        # "← From Reader" — pulls the current selection FROM the reader
        # INTO Notes. Renamed from "Add selection →" because the old
        # arrow direction confused users (it looked like it would push
        # Notes somewhere). The left-pointing arrow + "From" makes the
        # source explicit.
        tk.Button(
            notes_header, text="←  From Reader",
            command=self._copy_selection_to_notes,
            font=("Segoe UI", 10), bg=ACCENT_SLATE, fg="white", relief=tk.FLAT,
            padx=10, pady=4, cursor="hand2", borderwidth=0,
        ).pack(side=tk.RIGHT, padx=4)
        # Save button — stores a reference so the manual-save handler
        # can flash it green ("✓ Saved") after a successful write,
        # giving visible feedback the user was missing.
        self._notes_save_btn = tk.Button(
            notes_header, text="💾  Save", command=self._save_notes_manually,
            font=("Segoe UI", 10, "bold"),
            bg=ACCENT_GREEN, fg="white", relief=tk.FLAT,
            padx=10, pady=4, cursor="hand2", borderwidth=0,
        )
        self._notes_save_btn.pack(side=tk.RIGHT, padx=4)
        # One-click send to the Eisenhower Matrix. Opens a tiny menu so
        # the user picks which quadrant the note belongs in.
        self._notes_to_matrix_btn = tk.Button(
            notes_header, text="🎯  →  Matrix  ▾",
            command=self._show_notes_to_matrix_menu,
            font=("Segoe UI", 10, "bold"), bg=ACCENT_RED, fg="white",
            activebackground=ACCENT_RED, relief=tk.FLAT,
            padx=10, pady=4, cursor="hand2", borderwidth=0,
        )
        self._notes_to_matrix_btn.pack(side=tk.RIGHT, padx=4)
        # Second "→ Study" button — destinations OUTSIDE the Matrix.
        # Sister to the Matrix button. Together they cover every Study-
        # workspace destination the note can go to. Same MOVE behavior:
        # text gets cleared from Notes after a successful save so the
        # panel feels like a real conveyor belt to the Study workspace,
        # not a sticky scratch pad.
        self._notes_to_study_btn = tk.Button(
            notes_header, text="📓  →  Study  ▾",
            command=self._show_notes_to_study_menu,
            font=("Segoe UI", 10, "bold"), bg=ACCENT_PURPLE, fg="white",
            activebackground=ACCENT_PURPLE, relief=tk.FLAT,
            padx=10, pady=4, cursor="hand2", borderwidth=0,
        )
        self._notes_to_study_btn.pack(side=tk.RIGHT, padx=4)
        self.notes_area = scrolledtext.ScrolledText(
            notes_frame, wrap=tk.WORD,
            font=(self.font_family, 13),
            bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT,
            padx=14, pady=14, relief=tk.FLAT,
            selectbackground="#1d4ed8", selectforeground="white",
            undo=True, autoseparators=True, maxundo=-1,
        )
        self.notes_area.pack(fill=tk.BOTH, expand=True)
        # Auto-save notes whenever the user edits — debounced
        self._notes_save_after_id: str | None = None
        self.notes_area.bind("<<Modified>>", self._on_notes_modified)
        self.notes_area.bind("<Control-a>", self._select_all_notes)
        # Same right-click affordances the reader has — Cut/Copy/Paste/etc.
        self._build_notes_context_menu()
        # Focus tracking so the microphone can dictate into whichever
        # text widget you last clicked into (reader OR notes).
        self._mic_target: scrolledtext.ScrolledText = self.notes_area
        self.text_area.bind(
            "<FocusIn>", lambda _e: self._set_mic_target(self.text_area), add="+")
        self.notes_area.bind(
            "<FocusIn>", lambda _e: self._set_mic_target(self.notes_area), add="+")
        self._load_notes()

        # ---- Commentary pane (middle of the right column) ------------
        # Studies a *secondary* document alongside the primary book —
        # e-Sword's commentary module concept applied to any subject.
        # Source files live in COMMENTARIES_DIR so they stay separate
        # from regular books in the Library.
        commentary_frame = tk.Frame(right_pane, bg=BG_DARK)
        commentary_header = tk.Frame(commentary_frame, bg=BG_PANEL, padx=8, pady=6)
        commentary_header.pack(fill=tk.X)
        self.commentary_title_var = tk.StringVar(value="📑  Commentary")
        tk.Label(
            commentary_header, textvariable=self.commentary_title_var,
            bg=BG_PANEL, fg=FG_TEXT, font=("Segoe UI", 11, "bold"),
            anchor=tk.W,
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(
            commentary_header, text="Clear", command=self._clear_commentary,
            font=("Segoe UI", 10), bg=ACCENT_SLATE, fg="white",
            relief=tk.FLAT, padx=10, pady=4, cursor="hand2", borderwidth=0,
        ).pack(side=tk.RIGHT, padx=4)
        tk.Button(
            commentary_header, text="📂 Open commentary…",
            command=self.open_commentary_picker,
            font=("Segoe UI", 10), bg=ACCENT_CYAN, fg="white",
            relief=tk.FLAT, padx=10, pady=4, cursor="hand2", borderwidth=0,
        ).pack(side=tk.RIGHT, padx=4)
        self.commentary_area = scrolledtext.ScrolledText(
            commentary_frame, wrap=tk.WORD,
            font=(self.font_family, 12),
            bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT,
            padx=14, pady=10, relief=tk.FLAT,
            selectbackground="#1d4ed8", selectforeground="white",
        )
        self.commentary_area.pack(fill=tk.BOTH, expand=True)
        # Start read-only — DISABLED still allows mouse selection + Ctrl+C
        # so users can copy commentary excerpts into the Notes panel.
        self.commentary_area.configure(state=tk.DISABLED)

        right_pane.add(chapters_frame,   minsize=120, stretch="never")
        right_pane.add(commentary_frame, minsize=140, stretch="always")
        right_pane.add(notes_frame,      minsize=140, stretch="always")

        body.add(text_frame, minsize=320, stretch="always")
        body.add(right_pane, minsize=260, stretch="never")
        # Default split: text gets ~60% of the window. The right column
        # stacks chapters (~22%) / commentary (~40%) / notes (~38%).
        root.after(50, lambda: (
            body.sash_place(0, int(root.winfo_width() * 0.60), 0),
            right_pane.sash_place(0, 0, max(150, int(root.winfo_height() * 0.22))),
            right_pane.sash_place(1, 0, max(380, int(root.winfo_height() * 0.62))),
        ))

        # ---- Bottom hint line ------------------------------------------
        hint = tk.Label(
            dash,
            text=("Tip: select a paragraph and click 💾 to save just that part to your 📚 Library. "
                  "Otherwise the whole reader is saved. (Nothing gets lost — saved files appear in the Library.)  "
                  "Use the scrollbar on the right (or PgUp/PgDn) to pan the dashboard if your screen is short."),
            anchor=tk.W, font=("Segoe UI", 10), padx=12, pady=6,
            bg=BG_DARK, fg=FG_MUTED,
        )
        hint.pack(fill=tk.X)

        # ---- State -----------------------------------------------------
        self.current_file: str | None = None
        self.tts_engine = None
        self.tts_mode: str = "none"          # "pyttsx3" | "powershell" | "none"
        self.is_reading = False
        self._ps_proc: subprocess.Popen | None = None  # PowerShell-fallback process
        self._ps_tmpfile: str | None = None
        self._tts_thread: threading.Thread | None = None
        # Highlight-while-reading state
        self._highlight_queue: queue.Queue | None = None
        self._pump_after_id: str | None = None
        self._tts_iter_after_id: str | None = None
        self._tts_word_token = None
        self._tts_end_token = None
        # Pre-computed spans for live highlighting at each granularity.
        # Each tuple is (char_start, char_end, tk_start, tk_end).
        self._word_spans: list[tuple[int, int, str, str]] = []
        self._sentence_spans: list[tuple[int, int, str, str]] = []
        self._paragraph_spans: list[tuple[int, int, str, str]] = []
        # Cached text + anchor for the current read so spans can be
        # re-computed on demand when the user changes highlight unit
        # mid-read (lazy precompute saves seconds of UI freeze on
        # full-book reads).
        self._tts_speech_text: str = ""
        self._tts_speech_start_idx: str = "1.0"
        # Microphone / dictation state
        self.is_listening: bool = False
        self._mic_proc: subprocess.Popen | None = None
        self._mic_queue: queue.Queue | None = None
        self._mic_thread: threading.Thread | None = None
        self._mic_poll_after_id: str | None = None
        # Library window state (only one open at a time)
        self._library_win: tk.Toplevel | None = None
        self._library_tree: ttk.Treeview | None = None
        self._library_chapter_tree: ttk.Treeview | None = None
        self._library_items: list[tuple[str, str, int, float]] = []
        self._library_item_metas: list[dict] = []
        self._library_chapters: list[tuple[str, int]] = []
        self._library_current_book_idx: int | None = None
        self._library_stats_var: tk.StringVar | None = None
        self._library_search_var: tk.StringVar | None = None
        # (State-init for the new feature blocks was moved to the top of
        # __init__ above the dashboard build so widgets that read them
        # during construction see real values, not AttributeError.)
        # Chapter navigator state — populated whenever a book loads.
        # Each entry is (label, char_offset_in_widget_text).
        self._chapters: list[tuple[str, int]] = []
        # Commentary pane — separate from books; loaded from Commentaries/
        self._commentary_file: str | None = None
        # Reading timer (Pomodoro-style countdown)
        self._timer_after_id: str | None = None
        self._timer_remaining_seconds: int = 0
        self._timer_running: bool = False
        # Study workspace state
        self._study_win: tk.Toplevel | None = None
        self._study_tab_frames: dict[str, tk.Frame] = {}
        self._study_tab_buttons: dict[str, tk.Button] = {}
        self._highlights_records: list = []
        self._topics_records: list = []
        self._topic_entries_records: list = []
        self._bookmarks_records: list = []
        self._glossary_records: list = []
        self._journal_records: list = []
        self._journal_current_id: int | None = None
        # Eisenhower matrix — one autosaving editor per quadrant. With
        # the calendar redesign only the bottom two (delegate, eliminate)
        # remain as text editors; "do" and "schedule" are now driven by
        # the day_blocks table.
        self._eisenhower_widgets: dict = {}
        self._eisenhower_save_after_ids: dict = {}
        # Matrix-calendar state — day picker, block list, do-now panel
        self._selected_block_date: date = date.today()
        self._day_picker_buttons: list = []
        self._day_picker_date_var: tk.StringVar | None = None
        self._block_listbox = None
        self._block_records: list = []
        self._do_now_title_var: tk.StringVar | None = None
        self._do_now_duration_var: tk.StringVar | None = None
        self._do_now_status_var: tk.StringVar | None = None
        self._do_now_block_id: int | None = None
        # Study Notes (Study-workspace-scoped freeform notepad)
        self._study_notes_widget = None
        self._study_notes_save_after_id: str | None = None
        # Workflow tab state
        self._workflow_folders_listbox = None
        self._workflow_files_listbox = None
        self._workflow_records: list = []
        self._workflow_files: list = []
        self._workflow_stats_var: tk.StringVar | None = None
        self._workflow_files_label_var: tk.StringVar | None = None
        # Current color filter: None = show all, otherwise 'green'/'yellow'/'red'.
        # Persists across Study-workspace open/close so the user's last
        # filter sticks until they change it.
        self._workflow_filter_color: str | None = None
        self._workflow_filter_buttons: dict = {}
        self._init_study_db()

        # Initialize TTS on the MAIN thread.
        # Windows SAPI uses COM, and pyttsx3.init() can fail when called from
        # a non-main thread because the COM apartment isn't set up correctly.
        # Running this synchronously on the main thread fixes that.
        self._init_tts()

    # ---- Helpers --------------------------------------------------------
    def set_status(self, msg: str) -> None:
        self.status_var.set(msg)

    def _select_all(self, event=None):
        self.text_area.tag_add(tk.SEL, "1.0", tk.END)
        return "break"

    def smaller_text(self) -> None:
        self.font_size = max(10, self.font_size - 2)
        self.text_area.configure(font=(self.font_family, self.font_size))

    def bigger_text(self) -> None:
        self.font_size = min(36, self.font_size + 2)
        self.text_area.configure(font=(self.font_family, self.font_size))

    def _on_font_change(self, value=None) -> None:
        self.font_family = self.font_var.get()
        self.text_area.configure(font=(self.font_family, self.font_size))
        # Apply to notes too so the whole window reads consistently
        try: self.notes_area.configure(font=(self.font_family, 13))
        except Exception: pass

    def _on_highlight_color_change(self, value=None) -> None:
        color = self.HIGHLIGHT_COLORS.get(self.highlight_color_var.get(), "#fde047")
        try:
            self.text_area.tag_configure("reading", background=color)
        except tk.TclError:
            pass

    # ---- Notes -----------------------------------------------------------
    def _load_notes(self) -> None:
        """Read notes.md off disk on launch so previous notes stay visible."""
        try:
            if os.path.isfile(NOTES_FILE):
                with open(NOTES_FILE, "r", encoding="utf-8") as f:
                    content = f.read()
                self.notes_area.insert("1.0", content)
            self.notes_area.edit_modified(False)
        except Exception as e:
            self.set_status(f"Could not load notes: {e}")

    def _save_notes(self) -> bool:
        """Silent save (used by autosave). Returns True on success so
        the manual handler knows whether to flash the button."""
        try:
            os.makedirs(os.path.dirname(NOTES_FILE), exist_ok=True)
            content = self.notes_area.get("1.0", tk.END).rstrip() + "\n"
            with open(NOTES_FILE, "w", encoding="utf-8") as f:
                f.write(content)
            self.notes_area.edit_modified(False)
            self.set_status(f"Notes saved to {NOTES_FILE}")
            return True
        except Exception as e:
            messagebox.showerror("Could not save notes", str(e))
            return False

    def _save_notes_manually(self) -> None:
        """Click handler for the 💾 Save button. Same save logic as
        autosave, but flashes the button green with a ✓ Saved label
        for ~1.2 s so the user can see something actually happened."""
        if not self._save_notes():
            return
        btn = getattr(self, "_notes_save_btn", None)
        if btn is None:
            return
        try:
            original_text = btn.cget("text")
            original_bg = btn.cget("bg")
        except tk.TclError:
            return
        try:
            btn.configure(text="✓  Saved", bg="#22c55e",
                           activebackground="#22c55e")
        except tk.TclError:
            return

        def _restore():
            try:
                btn.configure(text=original_text, bg=original_bg,
                               activebackground=original_bg)
            except tk.TclError:
                pass
        self.root.after(1200, _restore)

    def _on_notes_modified(self, event=None) -> None:
        # Tkinter <<Modified>> fires once per change-set; reset the flag.
        try:
            if not self.notes_area.edit_modified():
                return
            self.notes_area.edit_modified(False)
        except Exception:
            return
        # Debounce: save 1.5 s after the last keystroke
        if self._notes_save_after_id is not None:
            try: self.root.after_cancel(self._notes_save_after_id)
            except Exception: pass
        self._notes_save_after_id = self.root.after(1500, self._save_notes)

    def _copy_selection_to_notes(self) -> None:
        """← From Reader button: pulls whatever's selected in the
        Reader on the left and appends it to Notes on the right (with
        a small "From: <book> — <timestamp>" header). If you typed in
        Notes and were hoping this button would send the note
        somewhere, you probably want the 🎯 → Matrix ▾ button next to
        Save instead."""
        try:
            sel = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST).strip()
        except tk.TclError:
            sel = ""
        if not sel:
            messagebox.showinfo(
                "Nothing selected in the Reader",
                "This button pulls a selection FROM the Reader (left "
                "side) INTO Notes.\n\n"
                "Highlight a paragraph in the book first, then click "
                "← From Reader.\n\n"
                "(To send what's already in Notes somewhere, use the "
                "🎯 → Matrix button next to Save.)",
            )
            return
        source = Path(self.current_file).name if self.current_file else "unknown source"
        header = f"\n\n---\nFrom: {source} — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        self.notes_area.insert(tk.END, header + sel)
        self.notes_area.see(tk.END)
        self._save_notes()

    def _init_tts(self) -> None:
        """Initialize speech on the main thread.

        Preference order: Piper > PowerShell > pyttsx3. Piper is the
        neural-voice option; PowerShell is the SAPI subprocess path
        (crash-isolated from the app); pyttsx3 is the in-process
        Windows-SAPI fallback. All three are out-of-process or stdlib
        so the chunked-highlight worker pattern stays identical.

        Override with env var BOOK_READER_TTS=piper|powershell|pyttsx3.
        """
        force = os.environ.get("BOOK_READER_TTS", "").strip().lower()

        if force in ("", "piper") and HAS_PIPER:
            self.tts_mode = "piper"
            self.set_status("Ready (Piper neural voice). "
                             "Click 📂 Open a book to begin.")
            return

        if force in ("", "powershell"):
            try:
                subprocess.run(
                    ["powershell", "-NoProfile", "-Command", "exit 0"],
                    check=True, timeout=5,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                )
                self.tts_mode = "powershell"
                self.set_status("Ready (PowerShell System.Speech). "
                                 "Click 📂 Open a book to begin.")
                return
            except Exception as e:
                print(f"[book_reader] PowerShell speech check failed, "
                      f"trying pyttsx3: {e}", file=sys.stderr)

        if HAS_TTS:
            try:
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty("rate", 175)
                self.tts_mode = "pyttsx3"
                self.set_status("Ready (in-process pyttsx3 — "
                                 "set BOOK_READER_TTS=piper for neural voice).")
                return
            except Exception as e:
                print(f"[book_reader] pyttsx3.init() failed: {e}",
                      file=sys.stderr)

        self.tts_mode = "none"
        self.set_status("No speech engine available.")

    # ---- File operations ------------------------------------------------
    def open_file(self) -> None:
        # Default to the Books folder if it exists
        initial = DEFAULT_BOOKS_DIR if os.path.isdir(DEFAULT_BOOKS_DIR) else os.path.expanduser("~")
        path = filedialog.askopenfilename(
            title="Open a book or document",
            initialdir=initial,
            filetypes=[
                ("All supported", "*.txt *.md *.docx *.pdf *.rtf *.html *.htm"),
                ("Text",          "*.txt *.md"),
                ("Word",          "*.docx"),
                ("PDF",           "*.pdf"),
                ("RTF",           "*.rtf"),
                ("HTML",          "*.html *.htm"),
                ("All files",     "*.*"),
            ],
        )
        if not path:
            return
        self._load_book(path)

    def _load_book(self, path: str) -> None:
        """Extract text from `path` and place it in the reading area.
        Shared by the file-picker (Open), the Library window, and any
        other future loader."""
        self.set_status(f"Loading {os.path.basename(path)}…")
        self.root.update_idletasks()
        try:
            text, chapters = self._extract_text_with_chapters(path)
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert("1.0", text)
            self.text_area.see("1.0")
            self.current_file = path
            # Re-apply any persisted study highlights for this book so they
            # survive across sessions, like e-Sword's markup overlay.
            self._render_persisted_highlights()
            self._populate_chapter_list(path, chapters)
            words = len(text.split())
            self.set_status(f"Loaded: {os.path.basename(path)} — {words:,} words. "
                            "Click 🔊 Read aloud or select text and 💾 Save.")
        except Exception as e:
            messagebox.showerror("Could not read file", f"{e}\n\nFile: {path}")
            self.set_status("Error loading file.")

    # ---- Paste text from clipboard --------------------------------------
    def paste_text(self) -> None:
        """Drop the system clipboard's contents into the reading area as if
        it were a freshly opened book. Handy for reading back a Claude reply
        or any other text you've copied from somewhere else."""
        try:
            text = self.root.clipboard_get()
        except tk.TclError:
            messagebox.showinfo(
                "Nothing to paste",
                "Your clipboard is empty. Copy some text (Ctrl+C) first, "
                "then click 📋 Paste text.",
            )
            return
        if not text.strip():
            messagebox.showinfo("Nothing to paste", "Your clipboard is empty.")
            return

        existing = self.text_area.get("1.0", tk.END).strip()
        if existing:
            choice = messagebox.askyesnocancel(
                "Reader already has text",
                "There's already content in the reader.\n\n"
                "  • Yes — replace it with what's on your clipboard.\n"
                "  • No — append the clipboard text to the end.\n"
                "  • Cancel — do nothing.",
            )
            if choice is None:
                return
            if choice:
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert("1.0", text)
                anchor = "1.0"
            else:
                self.text_area.insert(tk.END, "\n\n" + text)
                anchor = tk.END
        else:
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert("1.0", text)
            anchor = "1.0"

        self.text_area.see(anchor)
        # Pasted content isn't tied to a file on disk.
        self.current_file = None
        self._refresh_chapters_for_current_text("<pasted text>")
        pasted_words = len(text.split())
        total_words  = len(self.text_area.get("1.0", tk.END).split())
        self.set_status(
            f"📋 Pasted {pasted_words:,} words (reader now has {total_words:,}). "
            "Click 🔊 Read aloud."
        )

    # ---- Notes context menu + helpers ----------------------------------
    def _build_notes_context_menu(self) -> None:
        """Right-click menu on the Notes area — mirrors the reader's
        Cut/Copy/Paste/Select-all affordances plus a couple of study
        actions that make sense for selections of arbitrary text."""
        m = tk.Menu(
            self.notes_area, tearoff=0,
            bg=BG_PANEL, fg=FG_TEXT,
            activebackground=ACCENT_SLATE, activeforeground="white",
        )
        m.add_command(label="Cut",
                      command=lambda: self.notes_area.event_generate("<<Cut>>"))
        m.add_command(label="Copy",
                      command=lambda: self.notes_area.event_generate("<<Copy>>"))
        m.add_command(label="Paste",
                      command=lambda: self.notes_area.event_generate("<<Paste>>"))
        m.add_separator()
        m.add_command(label="Select all", command=self._select_all_notes)
        m.add_separator()
        m.add_command(label="📌  Add selection to topic…",
                      command=lambda: self.add_selection_to_topic(
                          source_widget=self.notes_area))
        m.add_command(label="📝  Add selection to Study Notes",
                      command=lambda: self.add_selection_to_study_notes(
                          source_widget=self.notes_area))
        # 🎯 Add to Matrix → quadrant submenu
        matrix_menu = tk.Menu(m, tearoff=0,
                               bg=BG_PANEL, fg=FG_TEXT,
                               activebackground=ACCENT_SLATE,
                               activeforeground="white")
        matrix_menu.add_command(label="🔥  Do  (Urgent & Important)",
            command=lambda: self.add_selection_to_matrix_quadrant(
                "do", source_widget=self.notes_area))
        matrix_menu.add_command(label="🗓  Schedule  (Important, Not Urgent)",
            command=lambda: self.add_selection_to_matrix_quadrant(
                "schedule", source_widget=self.notes_area))
        matrix_menu.add_command(label="👥  Delegate  (Urgent, Not Important)",
            command=lambda: self.add_selection_to_matrix_quadrant(
                "delegate", source_widget=self.notes_area))
        matrix_menu.add_command(label="🗑  Eliminate  (Neither)",
            command=lambda: self.add_selection_to_matrix_quadrant(
                "eliminate", source_widget=self.notes_area))
        m.add_cascade(label="🎯  Add to Matrix", menu=matrix_menu)
        m.add_command(label="📒  Look up in glossary",
                      command=lambda: self.lookup_selected_in_glossary(
                          source_widget=self.notes_area))
        m.add_separator()
        m.add_command(label="💾  Save notes now", command=self._save_notes)
        m.add_command(label="Clear notes…",        command=self._clear_notes)
        self._notes_menu = m
        self.notes_area.bind("<Button-3>", self._show_notes_context_menu)

    def _show_notes_context_menu(self, event) -> None:
        try:
            self._notes_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self._notes_menu.grab_release()

    def _select_all_notes(self, event=None):
        self.notes_area.tag_add(tk.SEL, "1.0", tk.END)
        self.notes_area.mark_set(tk.INSERT, "1.0")
        self.notes_area.see(tk.INSERT)
        return "break"

    def _clear_notes(self) -> None:
        if not self.notes_area.get("1.0", tk.END).strip():
            return
        if messagebox.askyesno(
            "Clear notes?",
            "Erase all your notes? (Ctrl+Z to undo if you change your mind.)",
        ):
            self.notes_area.delete("1.0", tk.END)
            self._save_notes()
            self.set_status("Notes cleared.")

    def _set_mic_target(self, widget) -> None:
        """Remember which text widget last had focus, so the mic
        dictates into whichever section the user was working in."""
        self._mic_target = widget

    def _show_notes_to_study_menu(self) -> None:
        """Drop a picker under the Notes header's '📓 → Study' button.
        Lists every non-Matrix Study destination the current Notes
        selection (or whole buffer) can be sent to. All options MOVE —
        Notes clears on success so the next note starts clean."""
        m = tk.Menu(self.notes_area, tearoff=0,
                    bg=BG_PANEL, fg=FG_TEXT,
                    activebackground=ACCENT_SLATE, activeforeground="white")
        m.add_command(
            label="📝  Study Notes",
            command=lambda: self.add_selection_to_study_notes(
                source_widget=self.notes_area))
        m.add_command(
            label="📌  Topic…  (pick or create one)",
            command=lambda: self.add_selection_to_topic(
                source_widget=self.notes_area))
        m.add_command(
            label="📅  Today's Journal",
            command=lambda: self.add_selection_to_journal_today(
                source_widget=self.notes_area))
        m.add_command(
            label="📒  Glossary entry…",
            command=lambda: self.add_selection_as_glossary_term(
                source_widget=self.notes_area))
        try:
            x = self._notes_to_study_btn.winfo_rootx()
            y = (self._notes_to_study_btn.winfo_rooty()
                 + self._notes_to_study_btn.winfo_height())
        except Exception:
            x, y = 0, 0
        try:
            m.tk_popup(x, y)
        finally:
            m.grab_release()

    def _show_notes_to_matrix_menu(self) -> None:
        """Drop a small picker under the Notes header's '🎯 → Matrix'
        button. Each option sends the current Notes selection (or the
        whole note if nothing is selected) straight into the chosen
        Eisenhower quadrant."""
        m = tk.Menu(self.notes_area, tearoff=0,
                    bg=BG_PANEL, fg=FG_TEXT,
                    activebackground=ACCENT_SLATE, activeforeground="white")
        m.add_command(
            label="🔥  Do  (Urgent & Important)",
            command=lambda: self.add_selection_to_matrix_quadrant(
                "do", source_widget=self.notes_area))
        m.add_command(
            label="🗓  Schedule  (Important, Not Urgent)",
            command=lambda: self.add_selection_to_matrix_quadrant(
                "schedule", source_widget=self.notes_area))
        m.add_command(
            label="👥  Delegate  (Urgent, Not Important)",
            command=lambda: self.add_selection_to_matrix_quadrant(
                "delegate", source_widget=self.notes_area))
        m.add_command(
            label="🗑  Eliminate  (Neither)",
            command=lambda: self.add_selection_to_matrix_quadrant(
                "eliminate", source_widget=self.notes_area))
        # Drop the menu just under the button so it feels attached to it.
        try:
            x = self._notes_to_matrix_btn.winfo_rootx()
            y = (self._notes_to_matrix_btn.winfo_rooty()
                 + self._notes_to_matrix_btn.winfo_height())
        except Exception:
            x, y = 0, 0
        try:
            m.tk_popup(x, y)
        finally:
            m.grab_release()

    def _select_all_in(self, widget) -> str:
        """Select-all helper that works on any Text widget. Bound to
        Ctrl+A on the Notes and Matrix editors."""
        try:
            widget.tag_add(tk.SEL, "1.0", tk.END)
            widget.mark_set(tk.INSERT, "1.0")
            widget.see(tk.INSERT)
        except tk.TclError:
            pass
        return "break"

    def _attach_clipboard_menu(self, widget,
                                clear_cmd=None, clear_label: str = "Clear",
                                track_for_mic: bool = True) -> tk.Menu:
        """Attach a right-click Cut/Copy/Paste/Select-all menu (plus an
        optional Clear command) to ``widget``. Also wires Ctrl+A for
        select-all and, when ``track_for_mic`` is set, a <FocusIn> hook
        so the mic dictates into whichever pane was clicked last.

        Used by every editable Text widget in the app — Notes, the four
        Eisenhower quadrants, and anywhere else this menu makes sense."""
        m = tk.Menu(widget, tearoff=0,
                    bg=BG_PANEL, fg=FG_TEXT,
                    activebackground=ACCENT_SLATE, activeforeground="white")
        m.add_command(label="Cut",
                      command=lambda w=widget: w.event_generate("<<Cut>>"))
        m.add_command(label="Copy",
                      command=lambda w=widget: w.event_generate("<<Copy>>"))
        m.add_command(label="Paste",
                      command=lambda w=widget: w.event_generate("<<Paste>>"))
        m.add_separator()
        m.add_command(label="Select all",
                      command=lambda w=widget: self._select_all_in(w))
        if clear_cmd is not None:
            m.add_separator()
            m.add_command(label=clear_label, command=clear_cmd)

        def _popup(event, _m=m):
            try:
                _m.tk_popup(event.x_root, event.y_root)
            finally:
                _m.grab_release()
        widget.bind("<Button-3>", _popup, add="+")
        widget.bind("<Control-a>",
                    lambda _e, w=widget: self._select_all_in(w), add="+")
        if track_for_mic:
            widget.bind("<FocusIn>",
                        lambda _e, w=widget: self._set_mic_target(w),
                        add="+")
        return m

    def _mic_target_label(self, widget) -> str:
        """Friendly name for the status bar — used when the mic starts
        listening so the user knows where dictation will land."""
        if widget is self.text_area:
            return "Reader"
        if widget is self.notes_area:
            return "Notes"
        if widget is getattr(self, "_journal_body", None):
            return "Journal"
        if widget is getattr(self, "_study_notes_widget", None):
            return "Study Notes"
        eis = getattr(self, "_eisenhower_widgets", {}) or {}
        for key, w in eis.items():
            if w is widget:
                label = next(
                    (lbl for k, lbl, *_ in self._EISENHOWER_QUADRANTS if k == key),
                    key,
                )
                return f"Matrix → {label}"
        return "Notes"

    def _build_text_context_menu(self) -> None:
        """Right-click menu on the reading area: Cut / Copy / Paste / Select
        all / Replace-with-clipboard / Clear. Gives clipboard operations an
        obvious affordance for people who don't know the Ctrl+ shortcuts."""
        m = tk.Menu(
            self.text_area, tearoff=0,
            bg=BG_PANEL, fg=FG_TEXT,
            activebackground=ACCENT_SLATE, activeforeground="white",
        )
        m.add_command(label="Cut",        command=lambda: self.text_area.event_generate("<<Cut>>"))
        m.add_command(label="Copy",       command=lambda: self.text_area.event_generate("<<Copy>>"))
        m.add_command(label="Paste",      command=lambda: self.text_area.event_generate("<<Paste>>"))
        m.add_separator()
        m.add_command(label="Select all", command=self._select_all)
        m.add_separator()
        m.add_command(label="📋  Replace with clipboard", command=self.paste_text)
        m.add_command(label="Clear reader",               command=self._clear_text_area)
        # ---- Study-mode actions (e-Sword-inspired companions) ---------
        m.add_separator()
        hl = tk.Menu(m, tearoff=0,
                     bg=BG_PANEL, fg=FG_TEXT,
                     activebackground=ACCENT_SLATE, activeforeground="white")
        hl.add_command(label="Yellow",
                       command=lambda: self.highlight_selection("Yellow"))
        hl.add_command(label="Teal",
                       command=lambda: self.highlight_selection("Teal"))
        hl.add_command(label="Indigo",
                       command=lambda: self.highlight_selection("Indigo"))
        hl.add_separator()
        hl.add_command(label="Remove highlight",
                       command=self.remove_highlights_in_selection)
        m.add_cascade(label="🖍  Highlight selection", menu=hl)
        m.add_command(label="📌  Add to topic…",        command=self.add_selection_to_topic)
        m.add_command(label="📝  Add to Study Notes",   command=self.add_selection_to_study_notes)
        # 🎯 Send the reader selection straight to a Matrix quadrant.
        matrix_menu_r = tk.Menu(m, tearoff=0,
                                 bg=BG_PANEL, fg=FG_TEXT,
                                 activebackground=ACCENT_SLATE,
                                 activeforeground="white")
        matrix_menu_r.add_command(label="🔥  Do  (Urgent & Important)",
            command=lambda: self.add_selection_to_matrix_quadrant(
                "do", source_widget=self.text_area))
        matrix_menu_r.add_command(label="🗓  Schedule  (Important, Not Urgent)",
            command=lambda: self.add_selection_to_matrix_quadrant(
                "schedule", source_widget=self.text_area))
        matrix_menu_r.add_command(label="👥  Delegate  (Urgent, Not Important)",
            command=lambda: self.add_selection_to_matrix_quadrant(
                "delegate", source_widget=self.text_area))
        matrix_menu_r.add_command(label="🗑  Eliminate  (Neither)",
            command=lambda: self.add_selection_to_matrix_quadrant(
                "eliminate", source_widget=self.text_area))
        m.add_cascade(label="🎯  Add to Matrix", menu=matrix_menu_r)
        m.add_command(label="🔖  Bookmark this spot",   command=self.bookmark_here)
        m.add_command(label="📒  Look up in glossary",  command=self.lookup_selected_in_glossary)
        m.add_separator()
        m.add_command(label="📓  Open Study workspace", command=self.open_study_workspace)
        self._text_menu = m
        # Button-3 is right-click on Windows.
        self.text_area.bind("<Button-3>", self._show_text_context_menu)

    def _show_text_context_menu(self, event) -> None:
        try:
            self._text_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self._text_menu.grab_release()

    def _clear_text_area(self) -> None:
        if not self.text_area.get("1.0", tk.END).strip():
            return
        if messagebox.askyesno("Clear reader?",
                               "Erase all the text currently in the reader?"):
            self.text_area.delete("1.0", tk.END)
            self.current_file = None
            self._clear_chapters()
            self.set_status("Reader cleared.")

    def _extract_text(self, path: str) -> str:
        """Backward-compatible single-return wrapper around the
        chapter-aware extractor. Kept so callers that only want the text
        don't have to know about chapter detection."""
        text, _chapters = self._extract_text_with_chapters(path)
        return text

    def _extract_text_with_chapters(self, path: str
                                     ) -> tuple[str, list[tuple[str, int]]]:
        """Extract plain text AND a list of (chapter_label, char_offset)
        pairs from the file at `path`. Per-format extractors get a chance
        to find authoritative chapters (docx headings, pdf outline, page
        boundaries); a text-pattern detector and an even-chunk fallback
        guarantee the chapter list always has something."""
        ext = Path(path).suffix.lower()
        if ext == ".docx":
            return self._extract_docx_with_chapters(path)
        if ext == ".pdf":
            return self._extract_pdf_with_chapters(path)
        # Plain-ish formats
        with open(path, encoding="utf-8", errors="replace") as f:
            raw = f.read()
        if ext == ".rtf":
            text = re.sub(r"\\[a-z]+-?\d*\s?|[{}]", "", raw)
        elif ext in (".html", ".htm") and HAS_BS4:
            text = BeautifulSoup(raw, "html.parser").get_text(" ", strip=True)
        else:
            text = raw
        chapters = self._detect_chapters_from_text(text, ext)
        if not chapters:
            chapters = self._chunk_evenly(text)
        return text, chapters

    def _extract_docx_with_chapters(self, path: str
                                     ) -> tuple[str, list[tuple[str, int]]]:
        if not HAS_DOCX:
            raise RuntimeError("python-docx not installed; cannot read .docx files.")
        doc = Document(path)
        paragraphs = [p for p in doc.paragraphs if p.text]
        parts: list[str] = []
        chapters: list[tuple[str, int]] = []
        running_offset = 0
        sep_len = 2  # the "\n\n" join separator
        for p in paragraphs:
            style_name = (p.style.name if p.style else "") or ""
            # Word's built-in heading styles + the "Title" style become
            # the authoritative chapter list when the doc has them.
            is_heading = style_name.startswith("Heading") or style_name == "Title"
            if is_heading and p.text.strip():
                chapters.append((p.text.strip()[:80], running_offset))
            parts.append(p.text)
            running_offset += len(p.text) + sep_len
        text = "\n\n".join(parts)
        if not chapters:
            chapters = self._detect_chapters_from_text(text, ".docx")
        if not chapters:
            chapters = self._chunk_evenly(text)
        return text, chapters

    def _extract_pdf_with_chapters(self, path: str
                                    ) -> tuple[str, list[tuple[str, int]]]:
        if not HAS_PDF:
            raise RuntimeError("pypdf not installed; cannot read .pdf files.")
        reader = pypdf.PdfReader(path)
        parts: list[str] = []
        page_offsets: list[tuple[int, int]] = []   # (page_number_1based, char_offset)
        running_offset = 0
        sep_len = 2
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            page_offsets.append((i + 1, running_offset))
            parts.append(page_text)
            running_offset += len(page_text) + sep_len
        text = "\n\n".join(parts)

        # Prefer the PDF's own outline (table of contents) if present.
        chapters: list[tuple[str, int]] = []
        try:
            outline = reader.outline  # may raise on some PDFs
            chapters = self._flatten_pdf_outline(outline, reader, page_offsets)
        except Exception:
            pass

        # Fall back to text-pattern detection (Chapter N etc.).
        if not chapters:
            chapters = self._detect_chapters_from_text(text, ".pdf")

        # Last resort: list pages (or page ranges for very long PDFs).
        if not chapters and page_offsets:
            n_pages = len(page_offsets)
            if n_pages <= 80:
                chapters = [(f"Page {p}", off) for p, off in page_offsets]
            else:
                step = max(1, n_pages // 40)
                chapters = []
                for i in range(0, n_pages, step):
                    p_start, off = page_offsets[i]
                    p_end = min(p_start + step - 1, n_pages)
                    label = f"Page {p_start}" if step == 1 else f"Pages {p_start}–{p_end}"
                    chapters.append((label, off))
        return text, chapters

    def _flatten_pdf_outline(self, outline, reader, page_offsets
                              ) -> list[tuple[str, int]]:
        """Recursively walk a pypdf outline (which is a nested list of
        Destination objects). Indent nested entries with spaces so the
        hierarchy is visible in a flat listbox."""
        chapters: list[tuple[str, int]] = []
        def walk(items, depth: int = 0) -> None:
            if items is None:
                return
            for item in items:
                if isinstance(item, list):
                    walk(item, depth + 1)
                    continue
                try:
                    title = getattr(item, "title", None)
                    if title is None:
                        continue
                    page_idx = reader.get_destination_page_number(item)
                    if page_idx is None or page_idx < 0 or page_idx >= len(page_offsets):
                        continue
                    offset = page_offsets[page_idx][1]
                    indent = "  " * depth
                    chapters.append((f"{indent}{str(title).strip()[:78]}", offset))
                except Exception:
                    continue
        try:
            walk(outline)
        except Exception:
            return []
        return chapters

    # Common chapter-heading regex. Matches lines like "Chapter 1",
    # "CHAPTER ONE", "Part III", "BOOK 4", "Section 12" with an optional
    # trailing title. Case-insensitive so the same pattern catches both.
    _CHAPTER_HEADING_RE = re.compile(
        r"^[ \t]*"
        r"(?:chapter|ch\.?|part|book|section)"
        r"[ \t]+"
        r"(?:[ivxlcdm]+|\d+|"
        r"one|two|three|four|five|six|seven|eight|nine|ten|"
        r"eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|"
        r"eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|"
        r"eighty|ninety|hundred)"
        r"(?:[ \t.:—–-][^\n]{0,80})?"
        r"$",
        re.MULTILINE | re.IGNORECASE,
    )
    _MD_HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.+)$", re.MULTILINE)

    def _detect_chapters_from_text(self, text: str, ext: str
                                    ) -> list[tuple[str, int]]:
        """Heuristic chapter detector that works on any plain text.
        Tries markdown ATX headings first (for .md), then the
        Chapter/Part/Book/Section pattern."""
        found: list[tuple[str, int]] = []

        if ext == ".md":
            for m in self._MD_HEADING_RE.finditer(text):
                level = len(m.group(1))
                label = ("  " * (level - 1)) + m.group(2).strip()[:80]
                found.append((label, m.start()))

        if not found:
            for m in self._CHAPTER_HEADING_RE.finditer(text):
                label = " ".join(m.group(0).split())[:80]
                found.append((label, m.start()))

        # Dedupe by offset, sort by offset.
        seen = set()
        deduped: list[tuple[str, int]] = []
        for label, off in found:
            if off in seen:
                continue
            seen.add(off)
            deduped.append((label, off))
        deduped.sort(key=lambda x: x[1])

        # Too many → probably false positives (every other line matched).
        if len(deduped) > 500:
            return []
        return deduped

    def _chunk_evenly(self, text: str) -> list[tuple[str, int]]:
        """Fallback chunker — splits text into evenly-sized sections at
        paragraph boundaries so the navigator always has something."""
        if not text or len(text.strip()) < 500:
            return [("(Beginning)", 0)]
        target_chars = 2500
        n = max(4, min(30, len(text) // target_chars))
        if n <= 1:
            return [("(Beginning)", 0)]
        chunk_size = len(text) // n
        chapters: list[tuple[str, int]] = []
        for i in range(n):
            offset = i * chunk_size
            # Snap forward to the next paragraph break if it's nearby.
            next_para = text.find("\n\n", offset)
            if 0 <= next_para - offset < chunk_size // 2:
                offset = next_para + 2
            window = text[offset:offset + 200]
            first_line = next((ln.strip() for ln in window.splitlines()
                                if ln.strip()), "")
            first_line = " ".join(first_line.split())[:50]
            label = f"Section {i + 1}"
            if first_line:
                label += f" — {first_line}"
            chapters.append((label, offset))
        return chapters

    # ---- Chapter navigator UI hooks -------------------------------------
    def _populate_chapter_list(self, label_or_path: str,
                                chapters: list[tuple[str, int]]) -> None:
        """Fill the chapter listbox and update its header title."""
        self._chapters = chapters
        self.chapter_listbox.delete(0, tk.END)
        if label_or_path.startswith("<"):
            # Synthetic source (pasted text etc.)
            self.chapter_title_var.set(f"📋  {label_or_path}")
        else:
            book_name = Path(label_or_path).stem
            self.chapter_title_var.set(f"📖  {book_name}")
        if not chapters:
            self.chapter_listbox.insert(tk.END, "  (no chapters detected)")
            return
        for label, _offset in chapters:
            self.chapter_listbox.insert(tk.END, f"  {label}")

    def _clear_chapters(self) -> None:
        """Reset the chapter navigator (called when the reader is wiped)."""
        self._chapters = []
        try:
            self.chapter_listbox.delete(0, tk.END)
            self.chapter_title_var.set("📖  No book open")
        except (tk.TclError, AttributeError):
            pass

    def _refresh_chapters_for_current_text(self, label: str) -> None:
        """Re-detect chapters from whatever's in the reader right now.
        Used after Paste so the navigator stays in sync."""
        text = self.text_area.get("1.0", tk.END)
        chapters = self._detect_chapters_from_text(text, ".txt")
        if not chapters:
            chapters = self._chunk_evenly(text)
        self._populate_chapter_list(label, chapters)

    def _jump_to_selected_chapter(self, _event=None) -> None:
        """Scroll the reader to the offset of the selected chapter."""
        sel = self.chapter_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        if idx >= len(self._chapters):
            return
        _label, offset = self._chapters[idx]
        try:
            tk_idx = self._tk_index_for_offset(offset)
            self.text_area.mark_set(tk.INSERT, tk_idx)
            self.text_area.see(tk_idx)
            # A small focus shift to the reader so PgUp/PgDn keep working
            # after the jump.
            self.text_area.focus_set()
        except tk.TclError:
            pass

    # ---- Session Header helpers ----------------------------------------
    # Cognitive load (1–10) → zone (GREEN/YELLOW/RED) → protocol gating.
    # The Library, Joy Protocol indicator, and zone chip all read from
    # self._cognitive_load. State is persisted to STUDY_DIR/session.json.
    @staticmethod
    def _zone_for_load(load: int) -> str:
        if load >= 7:
            return "GREEN"
        if load >= 4:
            return "YELLOW"
        return "RED"

    def _load_session_state(self) -> None:
        """Populate self._cognitive_load from the session JSON. Default 7
        (start of the GREEN zone) if no file exists or it's malformed."""
        self._cognitive_load = 7
        try:
            with open(SESSION_STATE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            load = int(data.get("cognitive_load", 7))
            if 1 <= load <= 10:
                self._cognitive_load = load
        except (OSError, json.JSONDecodeError, ValueError, TypeError):
            pass

    def _save_session_state(self) -> None:
        """Best-effort write of the cognitive load + derived zone.
        Non-fatal: a failure here just means the next launch starts at
        the default 7."""
        try:
            os.makedirs(os.path.dirname(SESSION_STATE_PATH), exist_ok=True)
            with open(SESSION_STATE_PATH, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "cognitive_load": self._cognitive_load,
                        "zone":           self._zone_for_load(self._cognitive_load),
                        "last_updated":   datetime.now().isoformat(timespec="seconds"),
                    },
                    f, indent=2,
                )
        except OSError:
            pass

    def _set_cognitive_load(self, load: int) -> None:
        """Authoritative setter — updates internal state, the three
        Session Header widgets, and persists. Called from the slider
        command callback every time the user drags."""
        try:
            load = max(1, min(10, int(load)))
        except (TypeError, ValueError):
            return
        if load == self._cognitive_load and self._cognitive_load_label is not None:
            # Slider drag fires on every pixel even if the integer value
            # didn't change; bail early to avoid pointless redraws.
            return
        self._cognitive_load = load
        zone = self._zone_for_load(load)
        # Numeric readout
        if self._cognitive_load_label is not None:
            try:
                self._cognitive_load_label.configure(text=f"{load}/10")
            except tk.TclError:
                pass
        # Zone chip
        if self._cognitive_zone_chip is not None:
            try:
                self._cognitive_zone_chip.configure(
                    text=f"{LIBRARY_ZONE_EMOJI[zone]} {zone} ZONE",
                    bg=LIBRARY_ZONE_COLOR[zone],
                )
            except tk.TclError:
                pass
        # Joy Protocol activates at load ≥ 7 (per protocol_activation spec)
        joy = self._protocol_labels.get("joy")
        if joy is not None:
            try:
                active = load >= 7
                joy.configure(
                    bg=ACCENT_GREEN if active else ACCENT_SLATE,
                    text="🥥 Joy ✓" if active else "🥥 Joy",
                )
            except tk.TclError:
                pass
        self._save_session_state()

    # ---- Handoff state helpers ------------------------------------------
    # The handoff file is the cross-session memory: every session-end
    # writes it, every session-start reads it. Keeps the "AI co-worker"
    # personality coherent across launches — Sentinel Forge remembers
    # what you were doing.
    def _load_handoff_state(self) -> dict | None:
        try:
            with open(HANDOFF_STATE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return None

    def _save_handoff_state(self, data: dict) -> None:
        try:
            os.makedirs(os.path.dirname(HANDOFF_STATE_PATH), exist_ok=True)
            with open(HANDOFF_STATE_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except OSError:
            pass

    @staticmethod
    def _format_handoff_message(data: dict) -> str:
        """Render the spec's one-liner handoff format:
        'Last session: X. Next task: Y. Blocker: Z.'"""
        last = (data.get("tasks_completed") or "").strip() or "(no notes)"
        nxt  = (data.get("next_session_primary_task") or "").strip() or "(none specified)"
        blk  = (data.get("blockers") or "").strip() or "no"
        return f"Last session: {last}\nNext task: {nxt}\nBlocker: {blk}"

    def _maybe_auto_start_wizard(self) -> None:
        """Auto-launch the Session Start wizard on the first launch of
        the day. Determines "first launch" by comparing the handoff's
        recorded session_start_date to today."""
        state = self._load_handoff_state()
        if state:
            start_date = state.get("session_start_date") or (state.get("date") or "")
            if start_date == date.today().isoformat():
                return  # already started today
        try:
            self.open_session_start_wizard()
        except tk.TclError:
            pass

    # ---- Session Start wizard ------------------------------------------
    def open_session_start_wizard(self) -> None:
        """One-screen modal: shows last session's handoff message,
        prefills the primary-task field from last session's "next task",
        captures current energy. On Begin, applies the energy to the
        topbar slider and records the session start in HANDOFF_STATE."""
        if self._session_start_win is not None:
            try:
                if self._session_start_win.winfo_exists():
                    self._session_start_win.lift()
                    self._session_start_win.focus_force()
                    return
            except tk.TclError:
                pass
            self._session_start_win = None

        state = self._load_handoff_state()
        win = tk.Toplevel(self.root)
        self._session_start_win = win
        win.title("🎯  Session Start")
        win.geometry("580x560")
        win.minsize(480, 460)
        win.configure(bg=BG_DARK)
        win.transient(self.root)
        try:
            win.grab_set()  # modal
        except tk.TclError:
            pass

        header = tk.Frame(win, bg=BG_PANEL, padx=14, pady=12)
        header.pack(fill=tk.X)
        tk.Label(header, text="🎯  Session Start", bg=BG_PANEL, fg=FG_TEXT,
                 font=("Segoe UI", 14, "bold")).pack(side=tk.LEFT)
        tk.Label(header, text=date.today().strftime("%A · %B %d, %Y"),
                 bg=BG_PANEL, fg=FG_MUTED, font=("Segoe UI", 10)
                 ).pack(side=tk.RIGHT)

        body = tk.Frame(win, bg=BG_DARK, padx=18, pady=12)
        body.pack(fill=tk.BOTH, expand=True)

        # ---- Last session summary -----
        if state:
            tk.Label(body, text="Last session", bg=BG_DARK, fg=FG_MUTED,
                     font=("Segoe UI", 9, "bold")
                     ).pack(anchor=tk.W, pady=(0, 4))
            tk.Label(body, text=self._format_handoff_message(state),
                     bg=BG_INPUT, fg=FG_TEXT, font=("Segoe UI", 10),
                     padx=10, pady=8, wraplength=500,
                     justify=tk.LEFT, anchor=tk.W
                     ).pack(fill=tk.X, pady=(0, 14))
        else:
            tk.Label(body,
                     text="No previous session on record — welcome to Sentinel Forge.",
                     bg=BG_DARK, fg=FG_MUTED,
                     font=("Segoe UI", 10, "italic")
                     ).pack(anchor=tk.W, pady=(0, 14))

        # ---- Energy slider -----
        tk.Label(body, text="How's your energy right now? (1–10)",
                 bg=BG_DARK, fg=FG_TEXT, font=("Segoe UI", 11, "bold")
                 ).pack(anchor=tk.W)
        energy_var = tk.IntVar(value=self._cognitive_load)
        energy_row = tk.Frame(body, bg=BG_DARK)
        energy_row.pack(fill=tk.X, pady=(4, 14))
        tk.Scale(
            energy_row, from_=1, to=10, orient=tk.HORIZONTAL, showvalue=True,
            variable=energy_var, length=320, sliderlength=18,
            bg=BG_DARK, fg=FG_TEXT, troughcolor=BG_INPUT,
            activebackground=ACCENT_CYAN, highlightthickness=0, borderwidth=0,
        ).pack(side=tk.LEFT)
        tk.Label(energy_row,
                 text="(7–10 → 🟢 GREEN · 4–6 → 🟡 YELLOW · 1–3 → 🔴 RED)",
                 bg=BG_DARK, fg=FG_MUTED, font=("Segoe UI", 9)
                 ).pack(side=tk.LEFT, padx=10)

        # ---- Primary task -----
        tk.Label(body, text="One primary task for this session",
                 bg=BG_DARK, fg=FG_TEXT, font=("Segoe UI", 11, "bold")
                 ).pack(anchor=tk.W)
        tk.Label(body,
                 text="(The Sentinel spec is strict — pick ONE focus.)",
                 bg=BG_DARK, fg=FG_MUTED, font=("Segoe UI", 9, "italic")
                 ).pack(anchor=tk.W)
        primary_task_var = tk.StringVar()
        if state and state.get("next_session_primary_task"):
            primary_task_var.set(state["next_session_primary_task"])
        task_entry = tk.Entry(
            body, textvariable=primary_task_var,
            bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT,
            font=("Segoe UI", 11), relief=tk.FLAT, bd=0,
        )
        task_entry.pack(fill=tk.X, ipady=6, pady=(4, 14))

        # ---- Protocols (informational) -----
        proto_row = tk.Frame(body, bg=BG_DARK)
        proto_row.pack(fill=tk.X, pady=(0, 12))
        tk.Label(proto_row, text="Active protocols:",
                 bg=BG_DARK, fg=FG_MUTED, font=("Segoe UI", 10)
                 ).pack(side=tk.LEFT, padx=(0, 8))
        for txt in ("Ω1 always on", "🥥 Joy at load ≥ 7", "🧠 Coconut always on"):
            tk.Label(proto_row, text=txt, bg=ACCENT_SLATE, fg="white",
                     font=("Segoe UI", 9), padx=6, pady=2
                     ).pack(side=tk.LEFT, padx=2)

        # ---- Buttons -----
        btn_row = tk.Frame(body, bg=BG_DARK)
        btn_row.pack(fill=tk.X, pady=(12, 0))

        def _close():
            self._session_start_win = None
            try:
                win.destroy()
            except tk.TclError:
                pass

        def _begin():
            energy = int(energy_var.get())
            # Push the energy through the same setter the topbar uses so
            # the slider, zone chip, and Joy chip all update in lockstep.
            if self._cognitive_load_var is not None:
                try:
                    self._cognitive_load_var.set(energy)
                except tk.TclError:
                    pass
            self._set_cognitive_load(energy)
            cur = self._load_handoff_state() or {}
            cur["session_start_iso"]   = datetime.now().isoformat(timespec="seconds")
            cur["session_start_date"]  = date.today().isoformat()
            cur["session_primary_task"] = primary_task_var.get().strip()
            cur["session_start_energy"] = energy
            self._save_handoff_state(cur)
            task = primary_task_var.get().strip() or "(none)"
            self.set_status(f"🎯 Session started — primary task: {task}")
            _close()

        tk.Button(btn_row, text="Begin Session  ▶", command=_begin,
                  bg=ACCENT_GREEN, fg="white",
                  font=("Segoe UI", 11, "bold"),
                  relief=tk.FLAT, padx=18, pady=8,
                  cursor="hand2", borderwidth=0
                  ).pack(side=tk.LEFT, padx=(0, 8))
        tk.Button(btn_row, text="Skip for now", command=_close,
                  bg=ACCENT_SLATE, fg="white",
                  font=("Segoe UI", 10),
                  relief=tk.FLAT, padx=12, pady=6,
                  cursor="hand2", borderwidth=0
                  ).pack(side=tk.LEFT)

        win.protocol("WM_DELETE_WINDOW", _close)
        task_entry.focus_set()

    # ---- Session End wizard --------------------------------------------
    def open_session_end_wizard(self) -> None:
        """Capture tasks completed/remaining/blockers + next session's
        primary task + end energy, write HANDOFF_STATE.json so the next
        Session Start wizard can pick up where this one left off."""
        if self._session_end_win is not None:
            try:
                if self._session_end_win.winfo_exists():
                    self._session_end_win.lift()
                    self._session_end_win.focus_force()
                    return
            except tk.TclError:
                pass
            self._session_end_win = None

        state = self._load_handoff_state() or {}
        win = tk.Toplevel(self.root)
        self._session_end_win = win
        win.title("⏹  Session End")
        win.geometry("620x680")
        win.minsize(520, 560)
        win.configure(bg=BG_DARK)
        win.transient(self.root)
        try:
            win.grab_set()
        except tk.TclError:
            pass

        header = tk.Frame(win, bg=BG_PANEL, padx=14, pady=12)
        header.pack(fill=tk.X)
        tk.Label(header, text="⏹  Session End", bg=BG_PANEL, fg=FG_TEXT,
                 font=("Segoe UI", 14, "bold")).pack(side=tk.LEFT)
        tk.Label(header, text=date.today().strftime("%A · %B %d, %Y"),
                 bg=BG_PANEL, fg=FG_MUTED, font=("Segoe UI", 10)
                 ).pack(side=tk.RIGHT)

        body = tk.Frame(win, bg=BG_DARK, padx=18, pady=12)
        body.pack(fill=tk.BOTH, expand=True)

        primary_task = (state.get("session_primary_task") or "").strip()
        if primary_task:
            tk.Label(body, text=f"Today's primary task: {primary_task}",
                     bg=BG_DARK, fg=FG_MUTED,
                     font=("Segoe UI", 10, "italic"),
                     wraplength=540, justify=tk.LEFT, anchor=tk.W
                     ).pack(fill=tk.X, pady=(0, 8))

        def _text_block(label: str, height: int = 4) -> tk.Text:
            tk.Label(body, text=label, bg=BG_DARK, fg=FG_TEXT,
                     font=("Segoe UI", 10, "bold")
                     ).pack(anchor=tk.W, pady=(8, 2))
            t = tk.Text(body, height=height,
                        bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT,
                        font=("Segoe UI", 10), relief=tk.FLAT, bd=0,
                        wrap=tk.WORD)
            t.pack(fill=tk.X)
            return t

        completed = _text_block("Tasks completed this session", 4)
        remaining = _text_block("Tasks remaining / unfinished", 3)
        blockers  = _text_block("Blockers (be specific)",        2)

        tk.Label(body, text="Next session's primary task",
                 bg=BG_DARK, fg=FG_TEXT, font=("Segoe UI", 10, "bold")
                 ).pack(anchor=tk.W, pady=(10, 2))
        next_task_var = tk.StringVar()
        tk.Entry(body, textvariable=next_task_var,
                 bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT,
                 font=("Segoe UI", 11), relief=tk.FLAT, bd=0
                 ).pack(fill=tk.X, ipady=6)

        tk.Label(body, text="End energy (1–10)",
                 bg=BG_DARK, fg=FG_TEXT, font=("Segoe UI", 10, "bold")
                 ).pack(anchor=tk.W, pady=(10, 2))
        end_energy_var = tk.IntVar(value=self._cognitive_load)
        tk.Scale(body, from_=1, to=10, orient=tk.HORIZONTAL, showvalue=True,
                 variable=end_energy_var, length=320, sliderlength=18,
                 bg=BG_DARK, fg=FG_TEXT, troughcolor=BG_INPUT,
                 activebackground=ACCENT_CYAN, highlightthickness=0,
                 borderwidth=0
                 ).pack(anchor=tk.W)

        btn_row = tk.Frame(body, bg=BG_DARK)
        btn_row.pack(fill=tk.X, pady=(14, 0))

        def _close():
            self._session_end_win = None
            try:
                win.destroy()
            except tk.TclError:
                pass

        def _save():
            now = datetime.now().isoformat(timespec="seconds")
            data = {
                "date":                       date.today().isoformat(),
                "session_start_iso":          state.get("session_start_iso"),
                "session_start_date":         state.get("session_start_date"),
                "session_end_iso":            now,
                "session_primary_task":       primary_task,
                "tasks_completed":            completed.get("1.0", tk.END).strip(),
                "tasks_remaining":            remaining.get("1.0", tk.END).strip(),
                "blockers":                   blockers.get("1.0", tk.END).strip(),
                "next_session_primary_task":  next_task_var.get().strip(),
                "start_energy":               state.get("session_start_energy"),
                "end_energy":                 int(end_energy_var.get()),
            }
            data["handoff_message"] = self._format_handoff_message(data)
            self._save_handoff_state(data)
            # Mirror end energy into the topbar slider too.
            if self._cognitive_load_var is not None:
                try:
                    self._cognitive_load_var.set(int(end_energy_var.get()))
                except tk.TclError:
                    pass
            self._set_cognitive_load(int(end_energy_var.get()))
            nxt = next_task_var.get().strip() or "(none)"
            self.set_status(f"⏹ Handoff saved — next task: {nxt}")
            _close()

        tk.Button(btn_row, text="Save Handoff  ✓", command=_save,
                  bg=ACCENT_GREEN, fg="white",
                  font=("Segoe UI", 11, "bold"),
                  relief=tk.FLAT, padx=18, pady=8,
                  cursor="hand2", borderwidth=0
                  ).pack(side=tk.LEFT, padx=(0, 8))
        tk.Button(btn_row, text="Cancel", command=_close,
                  bg=ACCENT_SLATE, fg="white",
                  font=("Segoe UI", 10),
                  relief=tk.FLAT, padx=12, pady=6,
                  cursor="hand2", borderwidth=0
                  ).pack(side=tk.LEFT)

        win.protocol("WM_DELETE_WINDOW", _close)
        completed.focus_set()

    # ---- Three-Zone Library metadata helpers ----------------------------
    # Each library file `foo.docx` gets a sidecar `foo.docx.meta.json`
    # carrying its zone + cognitive_load + breadcrumbs. The Sentinel Prime
    # Network spec defines the schema; see the Forge-Stack-A1 snapshot for
    # the source of truth.
    def _meta_path_for(self, file_path: str) -> str:
        return file_path + META_SUFFIX

    def _doc_id_for(self, file_path: str, area: str = "LIBRARY") -> str:
        """Apply the Sentinel naming standard:
        BOOKREADER-<AREA>-<slug>_<YYYY-MM-DD>_v001."""
        stem = Path(file_path).stem
        slug = re.sub(r"[^a-z0-9]+", "_", stem.lower()).strip("_") or "item"
        return f"BOOKREADER-{area}-{slug}_{date.today().isoformat()}_v001"

    def _load_meta(self, file_path: str) -> dict:
        """Read the sidecar; lazy-create a default if missing so the file
        immediately participates in zone filtering."""
        p = self._meta_path_for(file_path)
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if data.get("zone") not in LIBRARY_ZONES:
                    data["zone"] = LIBRARY_ZONE_DEFAULT
                if not isinstance(data.get("cognitive_load"), int):
                    data["cognitive_load"] = LIBRARY_ZONE_LOAD_DEFAULT[data["zone"]]
                return data
            except (OSError, json.JSONDecodeError):
                pass
        meta = {
            "doc_id":         self._doc_id_for(file_path),
            "zone":           LIBRARY_ZONE_DEFAULT,
            "cognitive_load": LIBRARY_ZONE_LOAD_DEFAULT[LIBRARY_ZONE_DEFAULT],
            "source_book":    None,
            "timestamp":      datetime.now().isoformat(timespec="seconds"),
            "tags":           [],
        }
        self._save_meta(file_path, meta)
        return meta

    def _save_meta(self, file_path: str, meta: dict) -> None:
        try:
            with open(self._meta_path_for(file_path), "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=2, ensure_ascii=False)
        except OSError:
            pass  # Non-fatal: zone filtering will fall back to defaults

    def _set_zone(self, file_path: str, zone: str) -> None:
        """Migrate a library file to a new zone. Snaps cognitive_load into
        the destination zone's range if it currently falls outside it
        (e.g., moving an active load=9 book to RED resets it to load=2)."""
        if zone not in LIBRARY_ZONES:
            return
        meta = self._load_meta(file_path)
        meta["zone"] = zone
        current = int(meta.get("cognitive_load") or 0)
        lo, hi = LIBRARY_ZONE_LOAD_RANGE[zone]
        if not (lo <= current <= hi):
            meta["cognitive_load"] = LIBRARY_ZONE_LOAD_DEFAULT[zone]
        self._save_meta(file_path, meta)

    # ---- Library --------------------------------------------------------
    # The library is just LIBRARY_DIR on disk, scanned recursively for files
    # whose extension is in SUPPORTED_EXTS. Persistence is automatic (it's
    # a folder), and there's no artificial limit on count or size — it'll
    # hold as much as your disk and OneDrive plan can take.
    def open_library(self) -> None:
        """Open (or focus) the Library window."""
        if self._library_win is not None:
            try:
                if self._library_win.winfo_exists():
                    self._library_win.lift()
                    self._library_win.focus_force()
                    return
            except Exception:
                pass
            self._library_win = None

        try:
            os.makedirs(LIBRARY_DIR, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Library folder unavailable",
                                 f"Could not create {LIBRARY_DIR}:\n{e}")
            return

        win = tk.Toplevel(self.root)
        self._library_win = win
        win.title("📚 Library")
        win.geometry("820x600")
        win.minsize(540, 360)
        win.configure(bg=BG_DARK)
        win.transient(self.root)

        # Drag-and-drop: drop files from Explorer onto the Library
        # window to add them. tkinterdnd2 hands us a single string with
        # paths possibly braced and space-separated — `tk.splitlist`
        # untangles that.
        if HAS_DND:
            try:
                win.drop_target_register(DND_FILES)
                def _on_drop(event):
                    raw = event.data
                    try:
                        paths = list(self.root.tk.splitlist(raw))
                    except tk.TclError:
                        paths = [raw]
                    paths = [p for p in paths if p]
                    if paths:
                        self._library_import_paths(paths)
                win.dnd_bind("<<Drop>>", _on_drop)
            except (tk.TclError, AttributeError):
                pass  # DnD unavailable; user still has the + Add files… button

        def _on_close():
            self._library_win = None
            win.destroy()
        win.protocol("WM_DELETE_WINDOW", _on_close)

        # Header
        header = tk.Frame(win, bg=BG_PANEL, padx=14, pady=12)
        header.pack(fill=tk.X)
        tk.Label(header, text="📚 Library", bg=BG_PANEL, fg=FG_TEXT,
                 font=("Segoe UI", 14, "bold")).pack(side=tk.LEFT)
        self._library_stats_var = tk.StringVar(value="")
        tk.Label(header, textvariable=self._library_stats_var, bg=BG_PANEL,
                 fg=FG_MUTED, font=("Segoe UI", 10)).pack(side=tk.RIGHT)

        # Path hint
        path_hint = tk.Label(
            win,
            text=(f"Folder: {LIBRARY_DIR}    "
                  "(Word, Google Docs exported as Word/PDF, PDF, RTF, HTML, TXT, MD) "
                  + ("· Drop files here to add them" if HAS_DND else "")),
            anchor=tk.W, bg=BG_DARK, fg=FG_MUTED,
            font=("Segoe UI", 9), padx=14, pady=4,
        )
        path_hint.pack(fill=tk.X)

        # Zone filter — Three-Zone Library (Sentinel Prime spec). Buttons
        # double as the legend for the zone-emoji prefix on each row.
        zone_row = tk.Frame(win, bg=BG_DARK, padx=14, pady=(8, 0))
        zone_row.pack(fill=tk.X)
        tk.Label(zone_row, text="Zone:", bg=BG_DARK, fg=FG_MUTED,
                 font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(0, 8))
        self._library_zone_filter_btns = {}
        def zbtn(label: str, zone_val: str | None, color: str) -> None:
            b = tk.Button(
                zone_row, text=label,
                command=lambda z=zone_val: self._library_set_zone_filter(z),
                font=("Segoe UI", 10, "bold"),
                bg=color, fg="white", activebackground=color,
                relief=tk.FLAT, padx=10, pady=3, cursor="hand2", borderwidth=0,
            )
            b.pack(side=tk.LEFT, padx=2)
            self._library_zone_filter_btns[zone_val or "__ALL__"] = b
        zbtn("All",        None,     ACCENT_SLATE)
        zbtn("🟢 GREEN",   "GREEN",  LIBRARY_ZONE_COLOR["GREEN"])
        zbtn("🟡 YELLOW",  "YELLOW", LIBRARY_ZONE_COLOR["YELLOW"])
        zbtn("🔴 RED",     "RED",    LIBRARY_ZONE_COLOR["RED"])

        # Search
        search_row = tk.Frame(win, bg=BG_DARK, padx=14, pady=8)
        search_row.pack(fill=tk.X)
        tk.Label(search_row, text="Search:", bg=BG_DARK, fg=FG_MUTED,
                 font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=(0, 6))
        self._library_search_var = tk.StringVar()
        search_entry = tk.Entry(
            search_row, textvariable=self._library_search_var,
            bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT,
            font=("Segoe UI", 11), relief=tk.FLAT, bd=0,
        )
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        self._library_search_var.trace_add(
            "write", lambda *_: self._refresh_library_list()
        )

        # Two-pane list, e-Sword style: Book Name on the left, Chapter on
        # the right. Click a book → chapters populate. Double-click a
        # chapter (or hit "Open in reader") to open the book at that
        # chapter. Both panes are ttk.Treeviews themed for the dark
        # palette.
        list_frame = tk.Frame(win, bg=BG_DARK, padx=14, pady=4)
        list_frame.pack(fill=tk.BOTH, expand=True)

        style = ttk.Style(win)
        try:
            style.theme_use(style.theme_use())  # keep current theme
        except Exception:
            pass
        style.configure(
            "Library.Treeview",
            background=BG_INPUT, fieldbackground=BG_INPUT, foreground=FG_TEXT,
            rowheight=24, borderwidth=0, font=("Segoe UI", 11),
        )
        style.configure(
            "Library.Treeview.Heading",
            background=BG_PANEL, foreground=FG_TEXT,
            font=("Segoe UI", 10, "bold"), relief=tk.FLAT, borderwidth=0,
        )
        style.map(
            "Library.Treeview",
            background=[("selected", ACCENT_CYAN)],
            foreground=[("selected", "white")],
        )
        style.map(
            "Library.Treeview.Heading",
            background=[("active", BG_PANEL)],
        )

        panes = tk.PanedWindow(
            list_frame, orient=tk.HORIZONTAL, bg=BG_DARK,
            sashrelief=tk.FLAT, sashwidth=4, borderwidth=0,
        )
        panes.pack(fill=tk.BOTH, expand=True)

        # ---- Left pane: book list ---------------------------------------
        books_frame = tk.Frame(panes, bg=BG_DARK)
        self._library_tree = ttk.Treeview(
            books_frame,
            columns=("name",),
            show="headings",
            style="Library.Treeview",
            selectmode="browse",
        )
        self._library_tree.heading("name", text="Book Name", anchor=tk.W)
        self._library_tree.column("name", anchor=tk.W, width=320, stretch=True)
        books_sb = tk.Scrollbar(books_frame, command=self._library_tree.yview)
        self._library_tree.configure(yscrollcommand=books_sb.set)
        books_sb.pack(side=tk.RIGHT, fill=tk.Y)
        self._library_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # ---- Right pane: chapter list -----------------------------------
        chapters_frame = tk.Frame(panes, bg=BG_DARK)
        self._library_chapter_tree = ttk.Treeview(
            chapters_frame,
            columns=("chapter",),
            show="headings",
            style="Library.Treeview",
            selectmode="browse",
        )
        self._library_chapter_tree.heading("chapter", text="Chapter", anchor=tk.W)
        self._library_chapter_tree.column("chapter", anchor=tk.W, width=200, stretch=True)
        ch_sb = tk.Scrollbar(chapters_frame, command=self._library_chapter_tree.yview)
        self._library_chapter_tree.configure(yscrollcommand=ch_sb.set)
        ch_sb.pack(side=tk.RIGHT, fill=tk.Y)
        self._library_chapter_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        panes.add(books_frame,    minsize=220, stretch="always")
        panes.add(chapters_frame, minsize=140, stretch="always")

        # Book pane bindings: selecting populates the chapter pane;
        # double-click / Enter opens the book.
        self._library_tree.bind(
            "<<TreeviewSelect>>",
            lambda _e: self._library_load_chapters_for_selection(),
        )
        self._library_tree.bind(
            "<Double-Button-1>", lambda _e: self._open_selected_library_book()
        )
        self._library_tree.bind(
            "<Return>", lambda _e: self._open_selected_library_book()
        )
        # Chapter pane bindings: double-click / Enter opens the book at
        # the selected chapter.
        self._library_chapter_tree.bind(
            "<Double-Button-1>", lambda _e: self._open_selected_library_book()
        )
        self._library_chapter_tree.bind(
            "<Return>", lambda _e: self._open_selected_library_book()
        )

        # Action row
        btn_row = tk.Frame(win, bg=BG_DARK, padx=14, pady=12)
        btn_row.pack(fill=tk.X)

        def lbtn(parent, text, cmd, color):
            return tk.Button(
                parent, text=text, command=cmd,
                font=("Segoe UI", 11, "bold"),
                bg=color, fg="white", activebackground=color,
                relief=tk.FLAT, padx=14, pady=8, cursor="hand2", borderwidth=0,
            )

        lbtn(btn_row, "+  Add files…",  self._library_add_files,
             ACCENT_GREEN).pack(side=tk.LEFT, padx=(0, 6))
        lbtn(btn_row, "🗑  Remove",      self._library_remove_selected,
             ACCENT_RED).pack(side=tk.LEFT, padx=6)
        lbtn(btn_row, "📂  Open folder", self._library_open_folder,
             ACCENT_SLATE).pack(side=tk.LEFT, padx=6)
        lbtn(btn_row, "🔄  Refresh",     self._refresh_library_list,
             ACCENT_SLATE).pack(side=tk.LEFT, padx=6)
        # Ask Library — cross-excerpt AI search via the Sentinel Forge
        # platform (http://127.0.0.1:8000/api/library/ask). Requires the
        # dashboard service to be running; degrades gracefully with a
        # helpful prompt if it isn't.
        lbtn(btn_row, "✨  Ask Library", self._library_ask_platform,
             ACCENT_PURPLE).pack(side=tk.LEFT, padx=(12, 6))
        # Zone migration — moves the selected book to GREEN/YELLOW/RED.
        # Cognitive load auto-snaps into the destination zone's range.
        lbtn(btn_row, "→ 🟢",  lambda: self._library_migrate_selected("GREEN"),
             LIBRARY_ZONE_COLOR["GREEN"]).pack(side=tk.LEFT, padx=(12, 2))
        lbtn(btn_row, "→ 🟡",  lambda: self._library_migrate_selected("YELLOW"),
             LIBRARY_ZONE_COLOR["YELLOW"]).pack(side=tk.LEFT, padx=2)
        lbtn(btn_row, "→ 🔴",  lambda: self._library_migrate_selected("RED"),
             LIBRARY_ZONE_COLOR["RED"]).pack(side=tk.LEFT, padx=2)
        lbtn(btn_row, "Open in reader", self._open_selected_library_book,
             ACCENT_CYAN).pack(side=tk.RIGHT, padx=(6, 0))
        lbtn(btn_row, "Close", _on_close,
             ACCENT_SLATE).pack(side=tk.RIGHT, padx=6)

        # Library opens with its filter defaulted to the active
        # cognitive zone (Sentinel Forge behavior: high load → GREEN
        # books, low load → RED archive). User can click "All" or
        # another zone to override.
        self._library_set_zone_filter(self._zone_for_load(self._cognitive_load))
        search_entry.focus_set()

    # ---- Ask Library (cross-excerpt AI search via the platform) --------
    # Calls the Sentinel Forge FastAPI service at
    # http://127.0.0.1:8000/api/library/ask. The service scans every
    # saved excerpt's body + metadata and returns the top matches with
    # snippets, scores, and matched terms. This is a feature the
    # standalone book reader can't provide on its own — single-file
    # search is local; cross-library search needs the platform.

    PLATFORM_ASK_URL = "http://127.0.0.1:8000/api/library/ask"

    def _library_ask_platform(self) -> None:
        """Send the current search box (or a prompt) to /api/library/ask."""
        # Use whatever's typed in the search box; if empty, ask for it.
        question = ""
        if self._library_search_var is not None:
            question = (self._library_search_var.get() or "").strip()
        if len(question) < 2:
            from tkinter import simpledialog
            question = simpledialog.askstring(
                "✨ Ask Your Library",
                "Search across every saved excerpt at once.\n\n"
                "Examples:\n"
                "  • wisdom honor\n"
                "  • bushido\n"
                "  • cognitive architecture\n"
                "  • Mycenaean Sea Peoples\n\n"
                "What are you looking for?",
                parent=self._library_win,
            )
            if not question:
                return
            question = question.strip()
            if len(question) < 2:
                return

        if self._library_stats_var is not None:
            self._library_stats_var.set("✨ Asking your library…")

        def _worker() -> None:
            result: dict | None = None
            err: tuple[str, str] | None = None
            try:
                import urllib.request
                import urllib.error
                payload = json.dumps({"question": question, "top_k": 10}).encode("utf-8")
                req = urllib.request.Request(
                    self.PLATFORM_ASK_URL,
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    result = json.loads(resp.read().decode("utf-8"))
            except urllib.error.URLError as e:
                err = ("connection", str(e))
            except Exception as e:                          # pragma: no cover
                err = ("other", str(e))
            self.root.after(0, lambda: self._library_ask_done(question, result, err))

        threading.Thread(target=_worker, daemon=True).start()

    def _library_ask_done(self, question: str,
                          result: dict | None,
                          err: tuple[str, str] | None) -> None:
        """Tk-thread callback: render Ask Library results or show error."""
        if self._library_stats_var is not None:
            self._library_stats_var.set("")
        if err is not None:
            kind, msg = err
            if kind == "connection":
                messagebox.showinfo(
                    "Sentinel Forge Dashboard not running",
                    "✨ Ask Library uses the Sentinel Forge platform service to\n"
                    "search across every excerpt you've ever saved.\n\n"
                    "Double-click the “Sentinel Forge Dashboard” icon on your\n"
                    "Desktop to start the service, then click Ask Library again.",
                    parent=self._library_win,
                )
            else:
                messagebox.showerror(
                    "Ask Library failed",
                    f"Unexpected error from the platform:\n\n{msg}",
                    parent=self._library_win,
                )
            return
        if not result:
            return
        self._show_ask_results(question, result)

    def _show_ask_results(self, question: str, result: dict) -> None:
        """Open a Toplevel showing the top matches as scrollable cards."""
        parent = self._library_win or self.root
        rw = tk.Toplevel(parent)
        rw.title(f"✨ Ask Library — {question[:60]}")
        rw.geometry("780x600")
        rw.minsize(520, 360)
        rw.configure(bg=BG_DARK)
        rw.transient(parent)

        # Header
        hdr = tk.Frame(rw, bg=BG_PANEL, padx=14, pady=10)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text=f"✨  {question}", bg=BG_PANEL, fg=FG_TEXT,
                 font=("Segoe UI", 13, "bold")).pack(side=tk.LEFT)
        tk.Label(
            hdr,
            text=f"{result.get('matched', 0)} match(es) / {result.get('total_searched', 0)} searched",
            bg=BG_PANEL, fg=FG_MUTED, font=("Segoe UI", 10),
        ).pack(side=tk.RIGHT)

        # Synthesis
        synth = result.get("answer_synthesis", "") or ""
        if synth:
            tk.Label(
                rw, text=synth, bg=BG_DARK, fg=ACCENT_CYAN,
                font=("Segoe UI", 10, "italic"),
                wraplength=720, justify=tk.LEFT,
                padx=14, pady=8, anchor="w",
            ).pack(fill=tk.X)

        # Scrollable list of match cards
        body = tk.Frame(rw, bg=BG_DARK)
        body.pack(fill=tk.BOTH, expand=True, padx=14, pady=4)
        canvas = tk.Canvas(body, bg=BG_DARK, highlightthickness=0)
        vscroll = ttk.Scrollbar(body, orient=tk.VERTICAL, command=canvas.yview)
        inner = tk.Frame(canvas, bg=BG_DARK)
        canvas.configure(yscrollcommand=vscroll.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        canvas_window = canvas.create_window((0, 0), window=inner, anchor="nw")
        def _on_inner_config(_e: tk.Event) -> None:
            canvas.configure(scrollregion=canvas.bbox("all"))
        def _on_canvas_config(e: tk.Event) -> None:
            canvas.itemconfigure(canvas_window, width=e.width)
        inner.bind("<Configure>", _on_inner_config)
        canvas.bind("<Configure>", _on_canvas_config)

        matches = result.get("matches", []) or []
        if not matches:
            tk.Label(
                inner,
                text="No matches yet. Try broader terms, or save more excerpts.",
                bg=BG_DARK, fg=FG_MUTED, font=("Segoe UI", 11),
                pady=24,
            ).pack()
        else:
            for m in matches:
                self._render_ask_match(inner, m, rw)

        # Footer
        ftr = tk.Frame(rw, bg=BG_DARK)
        ftr.pack(fill=tk.X, padx=14, pady=10)
        tk.Button(
            ftr, text="Close", command=rw.destroy,
            font=("Segoe UI", 10, "bold"),
            bg=ACCENT_SLATE, fg="white", activebackground=ACCENT_SLATE,
            relief=tk.FLAT, padx=14, pady=6, cursor="hand2", borderwidth=0,
        ).pack(side=tk.RIGHT)

    def _render_ask_match(self, parent: tk.Widget, m: dict, owner_win: tk.Toplevel) -> None:
        """Render one Ask Library match as a clickable card."""
        zone = (m.get("zone") or "GREEN").upper()
        zone_color = LIBRARY_ZONE_COLOR.get(zone, ACCENT_SLATE)
        src_full = m.get("source_book") or ""
        src_label = os.path.basename(src_full) if src_full else (m.get("doc_id") or "unknown")
        score = m.get("score", 0)
        hits = m.get("hits", []) or []
        snippet = (m.get("snippet") or "").strip()
        filename = m.get("filename", "")

        card = tk.Frame(parent, bg=BG_PANEL, padx=10, pady=8,
                        highlightthickness=1, highlightbackground="#334155")
        card.pack(fill=tk.X, pady=4)

        head = tk.Frame(card, bg=BG_PANEL)
        head.pack(fill=tk.X)
        tk.Label(
            head, text=src_label, bg=BG_PANEL, fg=FG_TEXT,
            font=("Segoe UI", 11, "bold"), anchor="w",
        ).pack(side=tk.LEFT)
        tk.Label(
            head, text=f"{zone}  ·  score {score}",
            bg=BG_PANEL, fg=zone_color, font=("Segoe UI", 9, "bold"),
        ).pack(side=tk.RIGHT)

        if snippet:
            tk.Label(
                card, text=snippet, bg=BG_PANEL, fg=FG_MUTED,
                font=("Segoe UI", 10), justify=tk.LEFT,
                wraplength=700, anchor="w",
            ).pack(fill=tk.X, pady=(4, 2))

        meta = tk.Frame(card, bg=BG_PANEL)
        meta.pack(fill=tk.X, pady=(2, 0))
        if hits:
            tk.Label(
                meta, text="matched: " + ", ".join(hits),
                bg=BG_PANEL, fg=ACCENT_CYAN,
                font=("Segoe UI", 9, "italic"), anchor="w",
            ).pack(side=tk.LEFT)
        if filename:
            tk.Label(
                meta, text=filename, bg=BG_PANEL, fg=FG_MUTED,
                font=("Segoe UI", 8), anchor="e",
            ).pack(side=tk.RIGHT)

    def _scan_library(self) -> list[tuple[str, str, int, float]]:
        """Walk LIBRARY_DIR recursively, skipping the Commentaries
        subfolder so commentaries never show up in the regular library
        list. Returns [(relative_path, absolute_path, size, mtime), ...]
        sorted by path."""
        found: list[tuple[str, str, int, float]] = []
        if not os.path.isdir(LIBRARY_DIR):
            return found
        commentaries_abs = os.path.abspath(COMMENTARIES_DIR).lower()
        for root_dir, dirs, files in os.walk(LIBRARY_DIR):
            # Mutating `dirs` in-place tells os.walk not to recurse into
            # them — this is the canonical way to skip a subtree.
            dirs[:] = [
                d for d in dirs
                if os.path.abspath(os.path.join(root_dir, d)).lower()
                   != commentaries_abs
            ]
            for name in files:
                if not name.lower().endswith(SUPPORTED_EXTS):
                    continue
                full = os.path.join(root_dir, name)
                try:
                    st = os.stat(full)
                except OSError:
                    continue
                rel = os.path.relpath(full, LIBRARY_DIR)
                found.append((rel, full, st.st_size, st.st_mtime))
        found.sort(key=lambda r: r[0].lower())
        return found

    def _refresh_library_list(self) -> None:
        if self._library_tree is None or self._library_stats_var is None:
            return
        tree = self._library_tree
        tree.delete(*tree.get_children())
        # Wrap the whole scan/render in try/except so a single bad
        # sidecar or unicode hiccup doesn't leave the user staring at
        # an empty-looking window with no explanation.
        try:
            scanned = self._scan_library()
        except Exception as e:                              # pragma: no cover
            self._library_stats_var.set(f"⚠ Scan failed: {e}")
            tree.insert("", tk.END, iid="err",
                        values=(f"⚠  Library scan failed: {e}",))
            return
        items = list(scanned)
        scanned_count = len(items)
        q = (self._library_search_var.get() if self._library_search_var else "").strip().lower()
        if q:
            items = [it for it in items if q in it[0].lower()]
        # Attach metadata (creates default sidecars on first scan) and
        # apply the zone filter if one is active.
        try:
            metas = [self._load_meta(full) for _rel, full, _s, _m in items]
        except Exception as e:                              # pragma: no cover
            metas = [{} for _ in items]
            self._library_stats_var.set(f"⚠ Some metadata could not be read: {e}")
        zone_filter = self._library_zone_filter
        if zone_filter:
            paired = [(it, m) for it, m in zip(items, metas)
                       if m.get("zone") == zone_filter]
            items = [it for it, _ in paired]
            metas = [m  for _,  m in paired]
        # If everything was filtered out but the folder has files,
        # tell the user instead of showing a void.
        if not items and scanned_count > 0:
            hint = (
                f"  📋  {scanned_count} file(s) in folder — "
                f"none match the current "
                + ("zone filter '" + zone_filter + "'" if zone_filter else "search")
                + ". Click 'All' to clear the filter."
            )
            tree.insert("", tk.END, iid="hint", values=(hint,))
            if self._library_stats_var is not None:
                self._library_stats_var.set(
                    f"0 of {scanned_count} shown — filter: "
                    + (zone_filter or "search:'" + q + "'")
                )
            return
        if not items and scanned_count == 0:
            tree.insert("", tk.END, iid="empty",
                        values=("  📂  Folder is empty. Drop books here or use + Add files…",))
            if self._library_stats_var is not None:
                self._library_stats_var.set("0 books in folder")
            return
        self._library_items = items
        self._library_item_metas = metas
        total_bytes = sum(it[2] for it in items)
        for idx, ((rel, _full, _size, _mtime), meta) in enumerate(zip(items, metas)):
            emoji = LIBRARY_ZONE_EMOJI.get(meta.get("zone", LIBRARY_ZONE_DEFAULT), "")
            stem = Path(rel).stem
            # Friendly labels for saved excerpts: instead of the long
            # technical filename "BOOKREADER-EXCERPT-a2_..._v001", show
            # "📝 from a2 · 18:48" so the user can recognize their save.
            # Source book and timestamp come from the sidecar metadata.
            if stem.startswith("BOOKREADER-EXCERPT-") and meta.get("source_book"):
                src_stem = Path(meta["source_book"]).stem
                ts = meta.get("timestamp", "")
                # Show HH:MM if we can parse the ISO timestamp
                short_ts = ""
                try:
                    short_ts = datetime.fromisoformat(ts).strftime("%Y-%m-%d %H:%M")
                except (ValueError, TypeError):
                    short_ts = ts[:16].replace("T", " ")
                display = f"{emoji}  📝 from {src_stem} · {short_ts}"
            else:
                display = f"{emoji}  {stem}"
            tree.insert("", tk.END, iid=str(idx), values=(display,))
        # Clear the chapter pane since the book selection is gone.
        if self._library_chapter_tree is not None:
            self._library_chapter_tree.delete(*self._library_chapter_tree.get_children())
        self._library_chapters = []
        self._library_current_book_idx = None
        n = len(items)
        filter_note = f" — filtered: {zone_filter}" if zone_filter else ""
        self._library_stats_var.set(
            f"{n} book{'s' if n != 1 else ''} — "
            f"{self._format_size(total_bytes)} total{filter_note}"
        )

    def _library_set_zone_filter(self, zone: str | None) -> None:
        """Apply (or clear) the zone filter and re-render."""
        self._library_zone_filter = zone
        active_key = zone or "__ALL__"
        for key, btn in self._library_zone_filter_btns.items():
            try:
                btn.configure(relief=tk.SUNKEN if key == active_key else tk.FLAT)
            except tk.TclError:
                pass
        self._refresh_library_list()

    def _library_migrate_selected(self, zone: str) -> None:
        """Move the currently selected book to a new zone and refresh."""
        if self._library_tree is None:
            return
        sel = self._library_tree.selection()
        if not sel:
            messagebox.showinfo(
                "Nothing selected",
                "Click a book in the list, then click a zone button "
                "(→ 🟢 / → 🟡 / → 🔴) to migrate it.",
            )
            return
        idx = int(sel[0])
        if idx >= len(self._library_items):
            return
        _rel, full, _s, _m = self._library_items[idx]
        self._set_zone(full, zone)
        self.set_status(
            f"Moved {os.path.basename(full)} → {LIBRARY_ZONE_EMOJI[zone]} {zone}"
        )
        self._refresh_library_list()

    def _library_load_chapters_for_selection(self) -> None:
        """Populate the right (Chapter) pane based on the currently
        selected book in the left pane. Called on every TreeviewSelect.
        Chapter detection re-uses the same `_extract_text_with_chapters`
        path used when opening a book in the reader."""
        if self._library_tree is None or self._library_chapter_tree is None:
            return
        ch_tree = self._library_chapter_tree
        ch_tree.delete(*ch_tree.get_children())
        self._library_chapters = []
        sel = self._library_tree.selection()
        if not sel:
            self._library_current_book_idx = None
            return
        idx = int(sel[0])
        if idx >= len(self._library_items):
            self._library_current_book_idx = None
            return
        # Skip re-extraction if the same book is already loaded — clicking
        # twice on the same row shouldn't re-parse a 500-page PDF.
        if self._library_current_book_idx == idx and self._library_chapters:
            return
        self._library_current_book_idx = idx
        _rel, full, _size, _mtime = self._library_items[idx]
        self.set_status(f"Reading chapters from {os.path.basename(full)}…")
        try:
            self.root.update_idletasks()
        except tk.TclError:
            pass
        try:
            _text, chapters = self._extract_text_with_chapters(full)
        except Exception:
            chapters = []
        self._library_chapters = chapters
        if not chapters:
            ch_tree.insert("", tk.END, iid="none",
                           values=("(no chapters detected)",))
            self.set_status(f"No chapters detected in {os.path.basename(full)}.")
            return
        for c_idx, (label, _offset) in enumerate(chapters):
            ch_tree.insert("", tk.END, iid=str(c_idx), values=(label,))
        self.set_status(
            f"{len(chapters)} chapter{'s' if len(chapters) != 1 else ''} "
            f"in {os.path.basename(full)}"
        )

    @staticmethod
    def _format_size(b: float) -> str:
        for unit in ("B", "KB", "MB", "GB"):
            if b < 1024 or unit == "GB":
                if unit == "B":
                    return f"{int(b):,} B"
                return f"{b:,.1f} {unit}"
            b /= 1024.0
        return f"{b:.1f} GB"

    def _library_add_files(self) -> None:
        """Copy one or more files into LIBRARY_DIR. Auto-renames on
        collision so we never silently overwrite an existing book."""
        paths = filedialog.askopenfilenames(
            title="Add books to your library",
            initialdir=os.path.expanduser("~"),
            filetypes=[
                ("All supported", "*.txt *.md *.docx *.pdf *.rtf *.html *.htm"),
                ("Word",          "*.docx"),
                ("PDF",           "*.pdf"),
                ("Text / Markdown", "*.txt *.md"),
                ("RTF",           "*.rtf"),
                ("HTML",          "*.html *.htm"),
                ("All files",     "*.*"),
            ],
        )
        if not paths:
            return
        self._library_import_paths(paths)

    def _library_import_paths(self, paths: list[str] | tuple[str, ...]) -> None:
        """Shared import path used by both the file dialog and the
        drag-and-drop drop handler. Validates each path, copies into
        LIBRARY_DIR with collision-renaming, and seeds the sidecar."""
        try:
            os.makedirs(LIBRARY_DIR, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Library folder unavailable", str(e))
            return
        added = 0
        skipped: list[str] = []
        lib_abs = os.path.abspath(LIBRARY_DIR).lower()
        for src in paths:
            # Drops sometimes hand us folders. Walk shallow for any
            # supported files inside; deeper recursion would surprise
            # the user.
            if os.path.isdir(src):
                for child in os.listdir(src):
                    childpath = os.path.join(src, child)
                    if (os.path.isfile(childpath)
                            and childpath.lower().endswith(SUPPORTED_EXTS)):
                        paths = list(paths) + [childpath]
                continue
            if not os.path.isfile(src):
                skipped.append(f"{os.path.basename(src)} (not a file)")
                continue
            if not src.lower().endswith(SUPPORTED_EXTS):
                skipped.append(f"{os.path.basename(src)} (unsupported format)")
                continue
            # If the user picks a file already inside the library, don't
            # copy it next to itself — just leave it where it is.
            src_abs = os.path.abspath(src).lower()
            if src_abs.startswith(lib_abs + os.sep) or src_abs == lib_abs:
                skipped.append(f"{os.path.basename(src)} (already in library)")
                continue
            dest = os.path.join(LIBRARY_DIR, os.path.basename(src))
            base, ext = os.path.splitext(dest)
            n = 1
            while os.path.exists(dest):
                dest = f"{base} ({n}){ext}"
                n += 1
            try:
                shutil.copy2(src, dest)
                # Seed default sidecar (zone=GREEN, load=8) so the new
                # book is visible under the active zone immediately.
                self._load_meta(dest)
                added += 1
            except Exception as e:
                skipped.append(f"{os.path.basename(src)} ({e})")
        self._refresh_library_list()
        msg = f"Added {added} file{'s' if added != 1 else ''} to the library."
        if skipped:
            msg += "\n\nSkipped:\n  • " + "\n  • ".join(skipped[:12])
            if len(skipped) > 12:
                msg += f"\n  • …and {len(skipped) - 12} more"
        messagebox.showinfo("Library updated", msg)

    def _library_remove_selected(self) -> None:
        if self._library_tree is None:
            return
        sel = self._library_tree.selection()
        if not sel:
            messagebox.showinfo("Nothing selected",
                                "Click a book in the list, then click Remove.")
            return
        idx = int(sel[0])
        if idx >= len(self._library_items):
            return
        rel, full, _size, _mtime = self._library_items[idx]
        if HAS_SEND2TRASH:
            confirm_msg = (f"Send this file to the Recycle Bin?\n\n{rel}\n\n"
                            "You can restore it from the Recycle Bin if needed.")
        else:
            confirm_msg = (f"Permanently delete this file from disk?\n\n{rel}\n\n"
                            "This cannot be undone. "
                            "(Install send2trash to get Recycle Bin support: "
                            "pip install send2trash)")
        if not messagebox.askyesno("Remove from library?", confirm_msg):
            return
        try:
            if HAS_SEND2TRASH:
                # send2trash needs forward-slashes-resistant absolute paths
                # on Windows; normpath fixes mixed separators in case the
                # path was rebuilt from a saved sidecar.
                send2trash(os.path.normpath(full))
            else:
                os.unlink(full)
        except Exception as e:
            messagebox.showerror("Could not remove", str(e))
            return
        # Sweep the sidecar too — Recycle Bin or unlink, same path.
        meta_p = self._meta_path_for(full)
        if os.path.exists(meta_p):
            try:
                if HAS_SEND2TRASH:
                    send2trash(os.path.normpath(meta_p))
                else:
                    os.unlink(meta_p)
            except (OSError, Exception):
                pass
        self._refresh_library_list()

    def _open_selected_library_book(self) -> None:
        if self._library_tree is None:
            return
        sel = self._library_tree.selection()
        if not sel:
            messagebox.showinfo("Nothing selected",
                                "Click a book in the list, then click Open.")
            return
        idx = int(sel[0])
        if idx >= len(self._library_items):
            return
        _rel, full, _size, _mtime = self._library_items[idx]
        self._load_book(full)
        # If a chapter is selected on the right, jump to its offset after
        # loading. Use the main reader's chapter navigator so its
        # selection stays in sync too.
        if (self._library_chapter_tree is not None
                and self._library_chapters):
            c_sel = self._library_chapter_tree.selection()
            if c_sel and c_sel[0] != "none":
                try:
                    c_idx = int(c_sel[0])
                except ValueError:
                    c_idx = -1
                if 0 <= c_idx < len(self._library_chapters):
                    _label, offset = self._library_chapters[c_idx]
                    try:
                        tk_idx = self._tk_index_for_offset(offset)
                        self.text_area.mark_set(tk.INSERT, tk_idx)
                        self.text_area.see(tk_idx)
                        try:
                            self.chapter_listbox.selection_clear(0, tk.END)
                            self.chapter_listbox.selection_set(c_idx)
                            self.chapter_listbox.see(c_idx)
                        except (tk.TclError, AttributeError):
                            pass
                    except tk.TclError:
                        pass
        try:
            if self._library_win is not None:
                self._library_win.destroy()
        except Exception:
            pass
        self._library_win = None

    def _library_open_folder(self) -> None:
        """Pop the library folder open in Explorer so the user can drag
        files in directly, organize into subfolders, etc."""
        try:
            os.startfile(LIBRARY_DIR)  # type: ignore[attr-defined]
        except Exception as e:
            messagebox.showerror("Could not open folder", str(e))

    # ---- Commentary pane -----------------------------------------------
    # Commentaries are stored separately from regular books (in
    # COMMENTARIES_DIR). The Library scan above prunes that subfolder,
    # so books and commentaries never mix. A loaded commentary is shown
    # in the middle pane of the right column, read-only.

    def open_commentary_picker(self) -> None:
        """Modal picker over the Commentaries/ folder. Add new
        commentaries from disk, remove existing ones, or open one in
        the commentary pane."""
        try:
            os.makedirs(COMMENTARIES_DIR, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Commentary folder unavailable",
                                 f"Could not create {COMMENTARIES_DIR}:\n{e}")
            return

        dlg = tk.Toplevel(self.root)
        dlg.title("📑 Commentaries")
        dlg.geometry("680x500")
        dlg.minsize(440, 320)
        dlg.configure(bg=BG_DARK)
        dlg.transient(self.root)
        dlg.grab_set()

        header = tk.Frame(dlg, bg=BG_PANEL, padx=14, pady=12)
        header.pack(fill=tk.X)
        tk.Label(header, text="📑 Commentaries", bg=BG_PANEL, fg=FG_TEXT,
                 font=("Segoe UI", 14, "bold")).pack(side=tk.LEFT)
        stats_var = tk.StringVar(value="")
        tk.Label(header, textvariable=stats_var, bg=BG_PANEL, fg=FG_MUTED,
                 font=("Segoe UI", 10)).pack(side=tk.RIGHT)

        tk.Label(
            dlg,
            text=f"Folder: {COMMENTARIES_DIR}   "
                 "(kept separate from your regular library — no mixing)",
            anchor=tk.W, bg=BG_DARK, fg=FG_MUTED,
            font=("Segoe UI", 9), padx=14, pady=4,
        ).pack(fill=tk.X)

        list_frame = tk.Frame(dlg, bg=BG_DARK, padx=14, pady=4)
        list_frame.pack(fill=tk.BOTH, expand=True)
        lb = tk.Listbox(
            list_frame, bg=BG_INPUT, fg=FG_TEXT,
            selectbackground=ACCENT_CYAN, selectforeground="white",
            font=("Consolas", 11),
            activestyle="none", relief=tk.FLAT, bd=0,
            highlightthickness=0,
        )
        sb = tk.Scrollbar(list_frame, command=lb.yview)
        lb.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        lb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        items_ref: dict = {"items": []}

        def refresh() -> None:
            lb.delete(0, tk.END)
            items: list[tuple[str, str, int, float]] = []
            try:
                names = sorted(os.listdir(COMMENTARIES_DIR), key=str.lower)
            except OSError:
                names = []
            for name in names:
                full = os.path.join(COMMENTARIES_DIR, name)
                if not os.path.isfile(full):
                    continue
                if not name.lower().endswith(SUPPORTED_EXTS):
                    continue
                try:
                    st = os.stat(full)
                except OSError:
                    continue
                items.append((name, full, st.st_size, st.st_mtime))
            items_ref["items"] = items
            total = sum(it[2] for it in items)
            for name, _f, size, mtime in items:
                size_str = self._format_size(size)
                date_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
                display = name if len(name) <= 48 else name[:45] + "…"
                lb.insert(tk.END,
                          f" {display:<48} {size_str:>10}   {date_str}")
            stats_var.set(
                f"{len(items)} commentar{'ies' if len(items) != 1 else 'y'}"
                f" — {self._format_size(total)} total"
            )

        def open_selected() -> None:
            sel = lb.curselection()
            if not sel:
                messagebox.showinfo("Nothing selected",
                                      "Pick a commentary to open.", parent=dlg)
                return
            _n, full, _s, _m = items_ref["items"][sel[0]]
            self._load_commentary(full)
            dlg.destroy()

        def add_files() -> None:
            paths = filedialog.askopenfilenames(
                title="Add commentaries",
                initialdir=os.path.expanduser("~"),
                filetypes=[
                    ("All supported", "*.txt *.md *.docx *.pdf *.rtf *.html *.htm"),
                    ("Word",          "*.docx"),
                    ("PDF",           "*.pdf"),
                    ("Text / Markdown", "*.txt *.md"),
                    ("RTF",           "*.rtf"),
                    ("HTML",          "*.html *.htm"),
                    ("All files",     "*.*"),
                ],
                parent=dlg,
            )
            if not paths:
                return
            try:
                os.makedirs(COMMENTARIES_DIR, exist_ok=True)
            except Exception as e:
                messagebox.showerror("Commentary folder unavailable",
                                       str(e), parent=dlg)
                return
            added = 0
            skipped: list[str] = []
            lib_abs = os.path.abspath(COMMENTARIES_DIR).lower()
            for src in paths:
                if not src.lower().endswith(SUPPORTED_EXTS):
                    skipped.append(f"{os.path.basename(src)} (unsupported)")
                    continue
                src_abs = os.path.abspath(src).lower()
                if src_abs.startswith(lib_abs + os.sep) or src_abs == lib_abs:
                    skipped.append(
                        f"{os.path.basename(src)} (already in commentaries)")
                    continue
                dest = os.path.join(COMMENTARIES_DIR, os.path.basename(src))
                base, ext = os.path.splitext(dest)
                n = 1
                while os.path.exists(dest):
                    dest = f"{base} ({n}){ext}"
                    n += 1
                try:
                    shutil.copy2(src, dest)
                    added += 1
                except Exception as e:
                    skipped.append(f"{os.path.basename(src)} ({e})")
            refresh()
            msg = f"Added {added} commentar{'ies' if added != 1 else 'y'}."
            if skipped:
                msg += "\n\nSkipped:\n  • " + "\n  • ".join(skipped[:12])
            messagebox.showinfo("Commentaries updated", msg, parent=dlg)

        def remove_selected() -> None:
            sel = lb.curselection()
            if not sel:
                messagebox.showinfo(
                    "Nothing selected",
                    "Pick a commentary to remove.", parent=dlg)
                return
            name, full, _s, _m = items_ref["items"][sel[0]]
            if not messagebox.askyesno(
                "Remove from commentaries?",
                f"Permanently delete this file from disk?\n\n{name}\n\n"
                "This cannot be undone.", parent=dlg):
                return
            try:
                os.unlink(full)
            except Exception as e:
                messagebox.showerror("Could not remove", str(e), parent=dlg)
                return
            # If the deleted file was the one currently loaded, clear the pane.
            if self._commentary_file and \
                    os.path.abspath(self._commentary_file) == os.path.abspath(full):
                self._clear_commentary()
            refresh()

        def open_folder() -> None:
            try:
                os.startfile(COMMENTARIES_DIR)  # type: ignore[attr-defined]
            except Exception as e:
                messagebox.showerror("Could not open folder",
                                       str(e), parent=dlg)

        row = tk.Frame(dlg, bg=BG_DARK, padx=14, pady=12)
        row.pack(fill=tk.X)
        def b(text, cmd, color):
            return tk.Button(row, text=text, command=cmd,
                             font=("Segoe UI", 11, "bold"),
                             bg=color, fg="white", activebackground=color,
                             relief=tk.FLAT, padx=14, pady=8,
                             cursor="hand2", borderwidth=0)
        b("+  Add commentaries…", add_files,       ACCENT_GREEN
          ).pack(side=tk.LEFT, padx=(0, 6))
        b("🗑  Remove",            remove_selected, ACCENT_RED
          ).pack(side=tk.LEFT, padx=6)
        b("📂  Open folder",       open_folder,     ACCENT_SLATE
          ).pack(side=tk.LEFT, padx=6)
        b("🔄  Refresh",           refresh,         ACCENT_SLATE
          ).pack(side=tk.LEFT, padx=6)
        b("Open in pane",          open_selected,   ACCENT_CYAN
          ).pack(side=tk.RIGHT, padx=(6, 0))
        b("Close",                 dlg.destroy,     ACCENT_SLATE
          ).pack(side=tk.RIGHT, padx=6)

        lb.bind("<Double-Button-1>", lambda _e: open_selected())
        lb.bind("<Return>", lambda _e: open_selected())

        refresh()
        # If empty, immediately offer to add files — saves a click on
        # first use.
        if not items_ref["items"]:
            if messagebox.askyesno(
                "Commentary library empty",
                "There are no commentaries yet.\n\nAdd one now?",
                parent=dlg,
            ):
                add_files()
        lb.focus_set()

    def _load_commentary(self, path: str) -> None:
        """Read `path` and display its text in the commentary pane."""
        try:
            text, _chs = self._extract_text_with_chapters(path)
        except Exception as e:
            messagebox.showerror(
                "Could not read commentary", f"{e}\n\nFile: {path}")
            return
        name = Path(path).stem
        self._commentary_file = path
        self.commentary_title_var.set(f"📑  {name}")
        w = self.commentary_area
        w.configure(state=tk.NORMAL)
        w.delete("1.0", tk.END)
        w.insert("1.0", text)
        w.see("1.0")
        w.configure(state=tk.DISABLED)
        self.set_status(f"📑 Loaded commentary: {name}")

    def _clear_commentary(self) -> None:
        """Empty the commentary pane."""
        self._commentary_file = None
        self.commentary_title_var.set("📑  Commentary")
        w = self.commentary_area
        w.configure(state=tk.NORMAL)
        w.delete("1.0", tk.END)
        w.configure(state=tk.DISABLED)
        self.set_status("Commentary cleared.")

    # ---- Read aloud — main-thread pyttsx3 with PowerShell fallback ------
    def read_aloud(self) -> None:
        # Wrap the whole entry point — historically a crash here left
        # is_reading=True and the UI looked frozen. Any uncaught error
        # now resets state and surfaces a status message.
        try:
            self._read_aloud_inner()
        except Exception as e:
            self.is_reading = False
            self.set_status(f"Read aloud failed: {e}")
            try:
                messagebox.showerror(
                    "Read aloud crashed",
                    f"The speech engine raised an exception:\n\n{e}\n\n"
                    "The app is still running — try again, or select a "
                    "smaller passage first.",
                )
            except tk.TclError:
                pass

    def _read_aloud_inner(self) -> None:
        if self.tts_mode == "none":
            messagebox.showerror(
                "Read aloud could not start",
                "Both the Python speech engine and PowerShell speech are "
                "unavailable on this machine. Click OK to dismiss.\n\n"
                "What you can try:\n"
                "  • Open Windows Settings → Time & Language → Speech and "
                "verify a voice is installed.\n"
                "  • Restart the Book Reader app and try again.",
            )
            return
        if self.is_reading:
            return

        # Reading start point — three tiers, in order of priority:
        #   1. If the user highlighted text, read just that selection.
        #   2. Else read from the INSERT cursor (wherever the user
        #      last clicked) to the end. This lets the user click into
        #      the book to set a resume point, take a Note, then click
        #      🔊 Read aloud to pick up where they left off.
        #   3. If the cursor's at the very top (typical right after
        #      opening a book), this naturally reads the whole book.
        # IMPORTANT: do NOT strip the text — chunk offsets are computed
        # relative to `speech_start_idx`, so leading whitespace must be
        # preserved or the yellow highlight lands in the wrong place.
        try:
            text = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
            speech_start_idx = self.text_area.index(tk.SEL_FIRST)
            start_label = "selection"
        except tk.TclError:
            try:
                speech_start_idx = self.text_area.index(tk.INSERT)
            except tk.TclError:
                speech_start_idx = "1.0"
            text = self.text_area.get(speech_start_idx, tk.END)
            start_label = ("top of book" if speech_start_idx == "1.0"
                           else f"cursor (line {speech_start_idx.split('.')[0]})")
        if not text.strip():
            messagebox.showinfo(
                "Nothing to read",
                "Open a book first, or click further up in the text — "
                "the cursor is past the end of the content.",
            )
            return

        # Long-book guard. Passing 100k+ chars to engine.say() in one shot
        # tends to hang SAPI or take 30+ seconds to compute spans before
        # the first word is spoken. Ask the user before we go for it.
        HARD_CAP = 60_000
        if len(text) > HARD_CAP:
            ok = messagebox.askyesno(
                "Read the whole book?",
                f"This is a long passage ({len(text):,} characters). "
                "Reading the whole thing in one go can make the app feel "
                "frozen for a while at the start, and some voices hang on "
                "very long input.\n\n"
                "Recommended: highlight a paragraph or chapter and click "
                "🔊 Read aloud again.\n\n"
                "Continue anyway?",
            )
            if not ok:
                return

        self.is_reading = True
        # Status now shows WHICH engine is active so the user can tell at
        # a glance whether they're getting Piper neural voice or a SAPI
        # fallback. Engine name is upper-cased for visibility.
        engine_label = {
            "piper":      "Piper neural · amy",
            "powershell": "PowerShell SAPI (Windows voice)",
            "pyttsx3":    "pyttsx3 SAPI (Windows voice)",
            "none":       "no engine",
        }.get(self.tts_mode, self.tts_mode)
        self.set_status(
            f"🔊 [{engine_label}] Reading from {start_label} "
            f"({len(text):,} chars)… click ■ Stop to end"
        )

        if self.tts_mode == "piper":
            try:
                self._speak_piper(text, speech_start_idx)
            except Exception as e:
                # Surface why Piper fell back, not just silently log it.
                msg = f"⚠ Piper setup failed: {e} — falling back to Windows voice"
                print(f"[book_reader] {msg}", file=sys.stderr)
                self.set_status(msg)
                self.tts_mode = "powershell"
                self._speak_powershell(text, speech_start_idx)
        elif self.tts_mode == "pyttsx3":
            try:
                self._speak_pyttsx3(text, speech_start_idx)
            except Exception as e:
                # pyttsx3 setup failed — fall through to PowerShell so
                # the user still gets audio.
                print(f"[book_reader] _speak_pyttsx3 failed, "
                      f"falling back to PowerShell: {e}",
                      file=sys.stderr)
                self.tts_mode = "powershell"
                self._speak_powershell(text, speech_start_idx)
        else:
            self._speak_powershell(text, speech_start_idx)

    # ---- pyttsx3 path — main-thread iterate() with started-word ---------
    def _speak_pyttsx3(self, text: str, speech_start_idx: str) -> None:
        """Speak via pyttsx3 entirely on the main thread.

        Uses `engine.startLoop(False)` + `engine.iterate()` driven by Tk's
        `after()` so SAPI events run on the same thread that owns the COM
        engine. Hooks `started-word` to highlight the current word (or its
        containing sentence / paragraph, per the user's choice).

        The previous worker-thread design called `engine.say()` from a
        different thread than `pyttsx3.init()`. On Windows SAPI that
        causes the engine to play audio but silently drop event callbacks
        — the "voice works, no highlight" symptom we hit before.
        """
        # Compute spans lazily — only the granularity currently selected
        # gets built up front. The other two are computed on demand if
        # the user changes the highlight unit mid-read. This used to
        # freeze the main thread for many seconds on a whole book; now
        # only the active granularity bears that cost.
        self._tts_speech_text = text
        self._tts_speech_start_idx = speech_start_idx
        self._word_spans      = []
        self._sentence_spans  = []
        self._paragraph_spans = []
        current_unit = self._current_unit()
        active_spans = self._compute_spans(text, speech_start_idx, current_unit)
        if current_unit == "Word":
            self._word_spans = active_spans
        elif current_unit == "Paragraph":
            self._paragraph_spans = active_spans
        else:
            self._sentence_spans = active_spans
        if not active_spans:
            self._on_speech_done()
            return

        # Disconnect any handlers left over from a previous read.
        for tok_attr in ("_tts_word_token", "_tts_end_token"):
            tok = getattr(self, tok_attr, None)
            if tok is not None:
                try: self.tts_engine.disconnect(tok)
                except Exception: pass
                setattr(self, tok_attr, None)

        def on_word(name, location, length):
            # Gate on is_reading so a late callback after Stop doesn't
            # re-apply the tag we just cleared.
            if not self.is_reading:
                return
            try:
                self._highlight_at_offset(int(location))
            except Exception:
                pass

        def on_end(name, completed):
            # Defer to main-thread tick so we don't tear down the engine
            # loop from inside its own callback.
            self.root.after(0, self._finish_pyttsx3_reading)

        try:
            self._tts_word_token = self.tts_engine.connect("started-word", on_word)
            self._tts_end_token  = self.tts_engine.connect("finished-utterance", on_end)
            self.tts_engine.say(text)
            self.tts_engine.startLoop(False)
        except Exception as e:
            # If startLoop isn't usable, fall back to the PowerShell path so
            # the user still gets audio AND highlighting.
            print(f"[book_reader] pyttsx3 startLoop failed: {e}; using PowerShell.",
                  file=sys.stderr)
            self.tts_mode = "powershell"
            self._speak_powershell(text, speech_start_idx)
            return
        self._tts_iter_after_id = self.root.after(10, self._tts_iterate)

    def _tts_iterate(self) -> None:
        """Drive the pyttsx3 event loop from Tk's main loop."""
        if not self.is_reading:
            return
        try:
            self.tts_engine.iterate()
        except Exception as e:
            self._on_speech_error(f"pyttsx3 iterate failed: {e}")
            return
        self._tts_iter_after_id = self.root.after(20, self._tts_iterate)

    def _highlight_at_offset(self, char_offset: int) -> None:
        """Find the span at the user-chosen unit that contains `char_offset`
        and apply the reading tag to it."""
        unit = self.highlight_unit_var.get() if hasattr(self, "highlight_unit_var") else "Sentence"
        # Lazy span computation — the read-aloud start path only builds
        # spans for the granularity active at the time. If the user
        # changes the unit mid-read, the new granularity's spans are
        # built on first highlight callback.
        if unit == "Word" and not self._word_spans:
            self._word_spans = self._compute_spans(
                getattr(self, "_tts_speech_text", "") or "",
                getattr(self, "_tts_speech_start_idx", "1.0"),
                "Word",
            )
        elif unit == "Sentence" and not self._sentence_spans:
            self._sentence_spans = self._compute_spans(
                getattr(self, "_tts_speech_text", "") or "",
                getattr(self, "_tts_speech_start_idx", "1.0"),
                "Sentence",
            )
        elif unit == "Paragraph" and not self._paragraph_spans:
            self._paragraph_spans = self._compute_spans(
                getattr(self, "_tts_speech_text", "") or "",
                getattr(self, "_tts_speech_start_idx", "1.0"),
                "Paragraph",
            )
        if unit == "Word":
            spans = self._word_spans
        elif unit == "Paragraph":
            spans = self._paragraph_spans
        else:
            spans = self._sentence_spans
        for char_s, char_e, tk_s, tk_e in spans:
            if char_s <= char_offset < char_e:
                self._highlight_range(tk_s, tk_e)
                return

    def _highlight_range(self, start: str, end: str) -> None:
        """Move the reading guide to `start..end` and scroll to it.
        Always called on the main thread."""
        try:
            self.text_area.tag_remove("reading", "1.0", tk.END)
            self.text_area.tag_add("reading", start, end)
            self.text_area.see(start)
        except tk.TclError as e:
            self.set_status(f"Highlight error: {e}")

    def _compute_spans(self, text: str, start_index: str, unit: str
                       ) -> list[tuple[int, int, str, str]]:
        """Return [(char_start, char_end, tk_start, tk_end), ...] for the
        requested granularity within `text`, anchored at `start_index`."""
        if unit == "Word":
            pattern = re.compile(r"\S+")
        elif unit == "Paragraph":
            # One or more non-blank lines; blank lines separate paragraphs.
            pattern = re.compile(r"[^\n]+(?:\n[^\n]+)*")
        else:  # Sentence
            pattern = re.compile(
                r"\S[^\n]*?(?:[.!?]+[\"')\]]?(?=\s|$)|(?=\n)|$)",
                re.MULTILINE,
            )
        spans: list[tuple[int, int, str, str]] = []
        for m in pattern.finditer(text):
            s, e = m.span()
            if not text[s:e].strip():
                continue
            try:
                tk_s = self.text_area.index(f"{start_index} + {s} chars")
                tk_e = self.text_area.index(f"{start_index} + {e} chars")
            except tk.TclError:
                continue
            spans.append((s, e, tk_s, tk_e))
        return spans

    def _finish_pyttsx3_reading(self) -> None:
        """Speech ended — tear down the loop and clear the highlight."""
        self._teardown_tts_loop()
        try:
            self.text_area.tag_remove("reading", "1.0", tk.END)
        except tk.TclError:
            pass
        self._on_speech_done()

    def _teardown_tts_loop(self) -> None:
        """Cancel the iterate poller, end the engine loop, and disconnect
        callbacks. Safe to call multiple times."""
        if self._tts_iter_after_id is not None:
            try: self.root.after_cancel(self._tts_iter_after_id)
            except Exception: pass
            self._tts_iter_after_id = None
        if self._pump_after_id is not None:
            try: self.root.after_cancel(self._pump_after_id)
            except Exception: pass
            self._pump_after_id = None
        try: self.tts_engine.endLoop()
        except Exception: pass
        for tok_attr in ("_tts_word_token", "_tts_end_token"):
            tok = getattr(self, tok_attr, None)
            if tok is not None:
                try: self.tts_engine.disconnect(tok)
                except Exception: pass
                setattr(self, tok_attr, None)

    def _on_speech_done(self) -> None:
        self.is_reading = False
        self.set_status("Done reading.")

    def _on_speech_error(self, msg: str) -> None:
        self.is_reading = False
        self.set_status(f"Read aloud error: {msg}")

    # ---- Piper path: neural voice, chunked highlighting ------------------
    def _speak_piper(self, text: str, speech_start_idx: str) -> None:
        """Speak via Piper neural TTS. Same chunked-highlight worker
        pattern as the PowerShell path:
          1. Split text into spans at the current highlight unit.
          2. Worker thread loops the spans, runs `piper.exe` per span
             (feeding text on stdin, capturing wav to a temp file), and
             plays the wav via Python's stdlib `winsound`.
          3. Before each span starts speaking, the worker pushes a
             ("highlight", tk_s, tk_e) event onto a queue; the main
             thread drains it via the same `_pump_highlights` after()
             poller the PowerShell path uses.
          4. Stop button sets is_reading=False and PURGEs the current
             winsound playback so audio cuts immediately.
        """
        import winsound
        chunks = self._compute_spans(text, speech_start_idx, self._current_unit())
        if not chunks:
            self._on_speech_done()
            return
        self._highlight_queue = queue.Queue()
        self._pump_after_id = self.root.after(50, self._pump_highlights)

        def _run() -> None:
            for char_s, char_e, tk_s, tk_e in chunks:
                if not self.is_reading:
                    break
                chunk_text = text[char_s:char_e].strip()
                if not chunk_text:
                    continue
                self._highlight_queue.put(("highlight", tk_s, tk_e))
                wav_path = None
                try:
                    fd, wav_path = tempfile.mkstemp(suffix=".wav")
                    os.close(fd)
                    # Piper reads text from stdin, writes wav to file.
                    # Capture stderr so subprocess failures are visible
                    # (Piper logs voice-load + RTF info to stderr on
                    # success; a non-zero exit means real trouble).
                    proc = subprocess.Popen(
                        [PIPER_EXE, "--model", PIPER_VOICE,
                          "--output_file", wav_path],
                        stdin=subprocess.PIPE,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.PIPE,
                        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                    )
                    self._ps_proc = proc  # reuse the kill-switch slot
                    try:
                        _stdout, _stderr = proc.communicate(
                            input=chunk_text.encode("utf-8"), timeout=60,
                        )
                    except subprocess.TimeoutExpired:
                        proc.kill()
                        continue
                    finally:
                        self._ps_proc = None
                    if proc.returncode != 0:
                        err_tail = (_stderr or b"").decode("utf-8", "replace")[-400:]
                        self._highlight_queue.put((
                            "error",
                            f"piper.exe exit {proc.returncode}: {err_tail}",
                        ))
                        return
                    if not self.is_reading:
                        break
                    if os.path.exists(wav_path) and os.path.getsize(wav_path) > 44:
                        # SND_FILENAME blocks until the wav finishes. We
                        # honor Stop by calling PlaySound(None, SND_PURGE)
                        # from stop_reading() — winsound interrupts.
                        try:
                            winsound.PlaySound(
                                wav_path,
                                winsound.SND_FILENAME | winsound.SND_NODEFAULT,
                            )
                        except RuntimeError:
                            pass  # PURGE was called from stop_reading
                except Exception as e:
                    self._highlight_queue.put(("error", str(e)))
                    return
                finally:
                    if wav_path and os.path.exists(wav_path):
                        try: os.unlink(wav_path)
                        except Exception: pass
            self._highlight_queue.put(("done",))

        self._tts_thread = threading.Thread(target=_run, daemon=True)
        self._tts_thread.start()

    # ---- PowerShell path: also highlights per chunk ---------------------
    def _speak_powershell(self, text: str, speech_start_idx: str) -> None:
        """Speak via PowerShell's System.Speech.Synthesis, one chunk at a
        time, so the same reading guide that the pyttsx3 path uses still
        works when we fall back to PowerShell.

        A worker thread runs PowerShell synchronously per chunk and
        pushes ``("highlight", tk_start, tk_end)`` events onto a thread-safe
        queue; the main thread drains the queue via a Tk after() poller
        and applies the reading tag from there. Direct Tk calls from
        the worker would race the main loop on Python 3.13 / Windows.
        """
        chunks = self._compute_spans(text, speech_start_idx, self._current_unit())
        if not chunks:
            self._on_speech_done()
            return
        self._highlight_queue = queue.Queue()

        def _run():
            for char_s, char_e, tk_s, tk_e in chunks:
                if not self.is_reading:
                    break
                chunk_text = text[char_s:char_e].strip()
                if not chunk_text:
                    continue
                self._highlight_queue.put(("highlight", tk_s, tk_e))
                tmp = None
                try:
                    fd, tmp = tempfile.mkstemp(suffix=".txt", text=False)
                    os.close(fd)
                    with open(tmp, "w", encoding="utf-8") as f:
                        f.write(chunk_text)
                    ps_cmd = (
                        "Add-Type -AssemblyName System.Speech; "
                        f"$t = Get-Content -Raw -Encoding UTF8 -LiteralPath '{tmp}'; "
                        "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                        "$s.Speak($t)"
                    )
                    proc = subprocess.Popen(
                        ["powershell", "-NoProfile", "-Command", ps_cmd],
                        stdin=subprocess.DEVNULL,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                    )
                    self._ps_proc = proc
                    proc.wait()
                    self._ps_proc = None
                except Exception as e:
                    self._highlight_queue.put(("error", str(e)))
                    return
                finally:
                    if tmp and os.path.exists(tmp):
                        try: os.unlink(tmp)
                        except Exception: pass
            self._highlight_queue.put(("done",))

        self._tts_thread = threading.Thread(target=_run, daemon=True)
        self._tts_thread.start()
        self._ps_poll_queue()

    def _current_unit(self) -> str:
        return self.highlight_unit_var.get() if hasattr(self, "highlight_unit_var") else "Sentence"

    def _ps_poll_queue(self) -> None:
        """Drain the PowerShell-path highlight queue on the main thread."""
        try:
            while True:
                msg = self._highlight_queue.get_nowait()
                tag = msg[0]
                if tag == "highlight":
                    _, tk_s, tk_e = msg
                    self._highlight_range(tk_s, tk_e)
                elif tag == "done":
                    self._finish_ps_reading()
                    return
                elif tag == "error":
                    self._on_speech_error(msg[1])
                    return
        except queue.Empty:
            pass
        if self.is_reading:
            self._pump_after_id = self.root.after(40, self._ps_poll_queue)

    def _finish_ps_reading(self) -> None:
        if self._pump_after_id is not None:
            try: self.root.after_cancel(self._pump_after_id)
            except Exception: pass
            self._pump_after_id = None
        try:
            self.text_area.tag_remove("reading", "1.0", tk.END)
        except tk.TclError:
            pass
        self._on_speech_done()

    def stop_reading(self) -> None:
        if not self.is_reading:
            return
        self.is_reading = False
        if self.tts_mode == "pyttsx3" and self.tts_engine is not None:
            try:
                self.tts_engine.stop()
            except Exception:
                pass
            self._teardown_tts_loop()
        else:
            if self._ps_proc is not None:
                try: self._ps_proc.terminate()
                except Exception: pass
                self._ps_proc = None
            # Piper mode plays via winsound — PURGE interrupts the
            # currently-playing wav. No-op for PowerShell mode.
            if self.tts_mode == "piper":
                try:
                    import winsound
                    winsound.PlaySound(None, winsound.SND_PURGE)
                except Exception:
                    pass
            if self._pump_after_id is not None:
                try: self.root.after_cancel(self._pump_after_id)
                except Exception: pass
                self._pump_after_id = None
        try:
            self.text_area.tag_remove("reading", "1.0", tk.END)
        except tk.TclError:
            pass
        self.set_status("Stopped.")

    # ---- Microphone / voice note ---------------------------------------
    # The mic uses Windows' built-in offline speech recognition
    # (System.Speech in PowerShell). Recognized phrases stream out on
    # the PS process's stdout and get appended to the Notes panel on
    # the main thread.
    #
    # IMPORTANT: we use the SYNCHRONOUS Recognize() API rather than the
    # async event-handler pattern. When PowerShell is launched with
    # `-Command`, .NET event callbacks registered via add_X() can fail
    # to dispatch because the script-block runspace has no message
    # pump — speech is "heard" but the callback never fires. Synchronous
    # Recognize() blocks the script thread until a phrase is recognized
    # (or an initial-silence timeout elapses), so no event pump is needed.
    # A diagnostic log is written to %TEMP%\bookreader_mic.log to make
    # future failures easy to triage.
    _MIC_PS_SCRIPT = r"""
$ErrorActionPreference = 'Stop'
$logPath = Join-Path $env:TEMP 'bookreader_mic.log'
function _Log($m) {
    try {
        Add-Content -Path $logPath -Encoding UTF8 -Value (
            '[' + ([DateTime]::Now.ToString('yyyy-MM-dd HH:mm:ss.fff')) + '] ' + $m)
    } catch {}
}
# Truncate the log at start so each session is easy to read.
try { Set-Content -Path $logPath -Value '' -Encoding UTF8 } catch {}
_Log '=== mic script start (sync Recognize mode) ==='
try {
    Add-Type -AssemblyName System.Speech
    _Log 'System.Speech assembly loaded'
    $rec = New-Object System.Speech.Recognition.SpeechRecognitionEngine
    _Log ('Recognizer: ' + $rec.RecognizerInfo.Name + ' / ' + $rec.RecognizerInfo.Culture)
    $rec.LoadGrammar((New-Object System.Speech.Recognition.DictationGrammar))
    _Log 'Dictation grammar loaded'
    $rec.SetInputToDefaultAudioDevice()
    _Log 'Audio input set to default device'
    [Console]::Out.WriteLine('__MIC_READY__')
    [Console]::Out.Flush()
    _Log '__MIC_READY__ written'
    while ($true) {
        try {
            # 10s initial-silence timeout. If the user is quiet for that
            # long, Recognize returns $null and we loop again — keeps
            # the script alive without burning CPU.
            $result = $rec.Recognize([TimeSpan]::FromSeconds(10))
            if ($result -and $result.Text) {
                _Log ('recognized: ' + $result.Text)
                [Console]::Out.WriteLine($result.Text)
                [Console]::Out.Flush()
            }
        } catch {
            _Log ('recognize-loop error: ' + $_.Exception.Message)
        }
    }
} catch {
    _Log ('FATAL: ' + $_.Exception.Message)
    Write-Output ('STT_ERROR: ' + $_.Exception.Message)
    exit 1
}
"""

    def toggle_mic(self) -> None:
        """Mic button handler — start listening if off, stop if on."""
        if self.is_listening:
            self._stop_mic()
            return
        if self.is_reading:
            messagebox.showinfo(
                "Stop reading first",
                "Read aloud is currently playing through the speakers, "
                "which the microphone would pick up. Click ■ Stop, then "
                "press 🎤 Voice note again.",
            )
            return
        self._start_mic()

    def _start_mic(self) -> None:
        """Spawn the PowerShell dictation process and start a stdout reader."""
        try:
            self._mic_proc = subprocess.Popen(
                ["powershell", "-NoProfile", "-Command", self._MIC_PS_SCRIPT],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,
                text=True, encoding="utf-8", errors="replace",
                bufsize=1,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except Exception as e:
            messagebox.showerror("Microphone could not start", str(e))
            return

        self._mic_queue = queue.Queue()
        self.is_listening = True

        def reader() -> None:
            try:
                assert self._mic_proc is not None and self._mic_proc.stdout is not None
                for raw in self._mic_proc.stdout:
                    line = raw.rstrip("\r\n")
                    if not line:
                        continue
                    if line.startswith("STT_ERROR:"):
                        self._mic_queue.put(("error", line[len("STT_ERROR:"):].strip()))
                    elif line == "__MIC_READY__":
                        self._mic_queue.put(("ready",))
                    else:
                        self._mic_queue.put(("text", line))
            except Exception:
                pass
            self._mic_queue.put(("done",))

        self._mic_thread = threading.Thread(target=reader, daemon=True)
        self._mic_thread.start()

        # Mic UI: red "Stop mic" while recording.
        self.mic_btn.configure(text="■  Stop mic", bg=ACCENT_RED,
                               activebackground=ACCENT_RED)

        # Lock the dictation target for this listening session. We use
        # whichever text widget the user last clicked into — falls back
        # to Notes if nothing has been focused yet, or if the previous
        # target (e.g. a Matrix quadrant) has since been destroyed.
        target = getattr(self, "_mic_target", None) or self.notes_area
        try:
            if not target.winfo_exists():
                target = self.notes_area
        except (tk.TclError, AttributeError):
            target = self.notes_area
        self._mic_active_target = target
        try:
            target.focus_set()
            target.mark_set(tk.INSERT, tk.INSERT)
            target.see(tk.INSERT)
        except tk.TclError:
            pass

        target_name = self._mic_target_label(target)
        self._mic_target_name = target_name
        self.set_status(
            f"🎤 Starting microphone… dictation will go to {target_name}.")

        self._mic_poll_after_id = self.root.after(50, self._mic_poll_queue)

    def _mic_poll_queue(self) -> None:
        """Drain the mic queue on the main thread and apply updates."""
        if not self.is_listening:
            return
        try:
            while True:
                msg = self._mic_queue.get_nowait()
                kind = msg[0]
                if kind == "text":
                    self._append_dictation(msg[1])
                elif kind == "ready":
                    target_name = getattr(self, "_mic_target_name", "Notes")
                    self.set_status(
                        f"🎤 Listening… dictating into {target_name}. "
                        "Click ■ Stop mic to finish.")
                elif kind == "error":
                    self._stop_mic(error=msg[1])
                    return
                elif kind == "done":
                    # Process exited unexpectedly — treat as stop.
                    self._stop_mic()
                    return
        except queue.Empty:
            pass
        self._mic_poll_after_id = self.root.after(50, self._mic_poll_queue)

    def _append_dictation(self, text: str) -> None:
        """Insert a recognized phrase at the active target's cursor with
        smart spacing (don't double-space; trailing space so the next
        phrase flows on). The target is whichever text widget had focus
        when the user clicked 🎤 — Notes by default, Reader if they
        clicked into the reader first."""
        text = text.strip()
        if not text:
            return
        target = getattr(self, "_mic_active_target", None) or self.notes_area
        try:
            prev_char = target.get("insert -1c", "insert")
        except tk.TclError:
            prev_char = ""
        leading = "" if (prev_char == "" or prev_char.isspace()) else " "
        try:
            target.insert(tk.INSERT, leading + text + " ")
            target.see(tk.INSERT)
        except tk.TclError:
            # Widget gone (window closed mid-dictation) — bail quietly.
            pass
        # If we just wrote to Notes, _on_notes_modified will pick it up and
        # debounce-save to disk. Reader writes are session-only.

    def _stop_mic(self, error: str | None = None) -> None:
        """Tear down the dictation process and reset the button to idle."""
        self.is_listening = False
        if self._mic_poll_after_id is not None:
            try: self.root.after_cancel(self._mic_poll_after_id)
            except Exception: pass
            self._mic_poll_after_id = None
        if self._mic_proc is not None:
            try: self._mic_proc.terminate()
            except Exception: pass
            try: self._mic_proc.wait(timeout=2)
            except Exception:
                try: self._mic_proc.kill()
                except Exception: pass
            self._mic_proc = None
        # Restore the idle button.
        try:
            self.mic_btn.configure(text="🎤  Voice note", bg=ACCENT_MIC,
                                   activebackground=ACCENT_MIC)
        except Exception:
            pass
        if error:
            log_path = os.path.join(os.environ.get("TEMP", ""),
                                     "bookreader_mic.log")
            messagebox.showerror(
                "Microphone could not start",
                f"{error}\n\n"
                "Tips:\n"
                "  • Plug in a microphone and set it as the default input "
                "device in Windows Sound settings.\n"
                "  • Windows Settings → Time & Language → Speech: install "
                "an English (or your language) speech pack.\n"
                "  • Windows Settings → Privacy → Microphone: allow desktop "
                "apps to use the microphone.\n\n"
                f"Diagnostic log: {log_path}",
            )
            self.set_status("Microphone error.")
        else:
            self.set_status("Mic off.")

    # ====================================================================
    # STUDY MODE — five e-Sword-inspired companions for secular reading.
    # Design lift: source content (books) lives in one place; user content
    # (highlights, bookmarks, topics, glossary, journal) lives in a
    # separate SQLite database. Location-anchored items (highlights,
    # bookmarks) reference (book_key, char_offset). None of this is
    # religious — the schema, labels, and workflow are all general-purpose.
    # ====================================================================

    # ---- Database helpers ----------------------------------------------
    def _init_study_db(self) -> None:
        """Create the study database and its tables if they don't exist."""
        try:
            os.makedirs(STUDY_DIR, exist_ok=True)
        except Exception as e:
            print(f"[book_reader] Could not create {STUDY_DIR}: {e}",
                  file=sys.stderr)
            return
        try:
            con = self._db()
            con.executescript("""
                CREATE TABLE IF NOT EXISTS highlights (
                    id INTEGER PRIMARY KEY,
                    book TEXT NOT NULL,
                    start_offset INTEGER NOT NULL,
                    end_offset INTEGER NOT NULL,
                    text TEXT,
                    color TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_highlights_book ON highlights(book);

                CREATE TABLE IF NOT EXISTS topics (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS topic_entries (
                    id INTEGER PRIMARY KEY,
                    topic_id INTEGER NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
                    text TEXT NOT NULL,
                    source_book TEXT,
                    source_offset INTEGER,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_entries_topic ON topic_entries(topic_id);

                CREATE TABLE IF NOT EXISTS bookmarks (
                    id INTEGER PRIMARY KEY,
                    book TEXT NOT NULL,
                    position INTEGER NOT NULL,
                    label TEXT,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_bookmarks_book ON bookmarks(book);

                CREATE TABLE IF NOT EXISTS glossary (
                    id INTEGER PRIMARY KEY,
                    term TEXT NOT NULL COLLATE NOCASE UNIQUE,
                    definition TEXT NOT NULL,
                    source TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS journal (
                    id INTEGER PRIMARY KEY,
                    entry_date TEXT NOT NULL,
                    body TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_journal_date ON journal(entry_date);

                /* Eisenhower priority matrix — one row per quadrant.
                   Keys are 'do' (urgent+important), 'schedule' (important
                   only), 'delegate' (urgent only), 'eliminate' (neither). */
                CREATE TABLE IF NOT EXISTS eisenhower (
                    quadrant TEXT PRIMARY KEY,
                    body TEXT NOT NULL DEFAULT '',
                    updated_at TEXT NOT NULL
                );

                /* Study Notes — one freeform notepad scoped to the
                   Study workspace (separate from the always-visible
                   Notes panel). Single-row by design; the CHECK keeps
                   it that way. Highlights can be sent here via the
                   right-click menu in the Highlights tab. */
                CREATE TABLE IF NOT EXISTS study_notes (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    body TEXT NOT NULL DEFAULT '',
                    updated_at TEXT NOT NULL
                );

                /* Day blocks — the new Matrix Do-Now / Schedule layer.
                   One row per Pomodoro block: which day it's for, how
                   long it runs, its title, and flags for done / active.
                   slot_order keeps them in user-chosen order within a day. */
                CREATE TABLE IF NOT EXISTS day_blocks (
                    id INTEGER PRIMARY KEY,
                    block_date TEXT NOT NULL,
                    slot_order INTEGER NOT NULL,
                    duration_min INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    notes TEXT NOT NULL DEFAULT '',
                    done INTEGER NOT NULL DEFAULT 0,
                    is_current INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_blocks_date
                    ON day_blocks(block_date);

                /* Workflow folders. Each row pairs metadata (color,
                   title, date label) with a real directory under
                   WORKFLOW_DIR, named after `name`. UNIQUE(name) is
                   case-insensitive so the disk-folder rename stays
                   collision-free. */
                CREATE TABLE IF NOT EXISTS workflow_folders (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    title TEXT NOT NULL DEFAULT '',
                    date_label TEXT NOT NULL DEFAULT '',
                    color TEXT NOT NULL DEFAULT 'green',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(name COLLATE NOCASE)
                );

                /* Audit rubric (Walkenbach / Sentinel Prime audit pattern).
                   One row per audit session. Findings live as a JSON array
                   in `findings_json` to keep the schema flat — each entry
                   is {finding, location, grade, fix}. The 5-column rubric
                   (# | Finding | Where | Grade | Recommended fix) is
                   reconstructed at render time. */
                CREATE TABLE IF NOT EXISTS audits (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL DEFAULT '',
                    subject TEXT NOT NULL DEFAULT '',
                    overall_grade TEXT NOT NULL DEFAULT '',
                    mentors_note TEXT NOT NULL DEFAULT '',
                    findings_json TEXT NOT NULL DEFAULT '[]',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                /* Prompt journal — schema matches the Google Prompting
                   Essentials prompt-library template verbatim
                   (docs/prompt-library/prompt-library-template.md).
                   Eight user-facing fields; `refs` is named to avoid
                   collision with the SQL keyword REFERENCES. */
                CREATE TABLE IF NOT EXISTS prompts (
                    id INTEGER PRIMARY KEY,
                    prompt TEXT NOT NULL DEFAULT '',
                    purpose TEXT NOT NULL DEFAULT '',
                    refs TEXT NOT NULL DEFAULT '',
                    iterations TEXT NOT NULL DEFAULT '',
                    ai_tools TEXT NOT NULL DEFAULT '',
                    input_type TEXT NOT NULL DEFAULT '',
                    output_type TEXT NOT NULL DEFAULT '',
                    notes TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
            """)
            con.commit()
            con.close()
        except sqlite3.Error as e:
            print(f"[book_reader] DB init error: {e}", file=sys.stderr)

    def _db(self) -> sqlite3.Connection:
        """Return a fresh connection. Each caller closes it after use."""
        con = sqlite3.connect(STUDY_DB)
        con.execute("PRAGMA foreign_keys = ON")
        return con

    def _db_query(self, sql: str, params: tuple = ()) -> list[tuple]:
        con = self._db()
        try:
            return con.execute(sql, params).fetchall()
        finally:
            con.close()

    def _db_exec(self, sql: str, params: tuple = ()) -> int:
        """Execute a write; return the last inserted rowid (or 0)."""
        con = self._db()
        try:
            cur = con.execute(sql, params)
            con.commit()
            return cur.lastrowid or 0
        finally:
            con.close()

    def _book_key(self, path: str | None) -> str | None:
        """Stable identifier for a book. Use a path relative to LIBRARY_DIR
        when possible so the whole library can be moved/renamed without
        breaking highlights and bookmarks; fall back to absolute path."""
        if not path:
            return None
        try:
            rel = os.path.relpath(path, LIBRARY_DIR)
            if not rel.startswith("..") and not os.path.isabs(rel):
                return "lib:" + rel.replace("\\", "/")
        except (ValueError, OSError):
            pass
        try:
            return "abs:" + os.path.abspath(path).replace("\\", "/")
        except Exception:
            return None

    def _book_path_for_key(self, key: str) -> str | None:
        if not key:
            return None
        if key.startswith("lib:"):
            return os.path.join(LIBRARY_DIR, key[4:].replace("/", os.sep))
        if key.startswith("abs:"):
            return key[4:].replace("/", os.sep)
        return key

    def _book_short_label(self, key: str | None) -> str:
        if not key:
            return "(no book)"
        if key.startswith("lib:"):
            return key[4:]
        if key.startswith("abs:"):
            return os.path.basename(key[4:])
        return key

    def _char_offset(self, tk_index: str) -> int:
        """Convert a Tk text index (e.g. '5.3') to an absolute char offset."""
        try:
            c = self.text_area.count("1.0", tk_index, "chars")
        except tk.TclError:
            return 0
        if c is None:
            return 0
        if isinstance(c, tuple):
            return int(c[0]) if c else 0
        return int(c)

    def _tk_index_for_offset(self, offset: int) -> str:
        return self.text_area.index(f"1.0 + {int(offset)} chars")

    # ---- 1. Highlights (persistent color overlay) ----------------------
    def _highlight_tag(self, color_name: str) -> str:
        """Return the tag name for `color_name`; configure it if needed."""
        tag = f"hl_{color_name.lower()}"
        color_hex = self.HIGHLIGHT_COLORS.get(color_name, "#fde047")
        try:
            self.text_area.tag_configure(tag, background=color_hex,
                                          foreground="#0f172a")
            # Reading guide must stay on top so audio-follow remains visible.
            self.text_area.tag_raise("reading", tag)
        except tk.TclError:
            pass
        return tag

    def highlight_selection(self, color_name: str | None = None) -> None:
        """Apply a persistent color highlight to the current selection."""
        try:
            s_idx = self.text_area.index(tk.SEL_FIRST)
            e_idx = self.text_area.index(tk.SEL_LAST)
            text = self.text_area.get(s_idx, e_idx)
        except tk.TclError:
            messagebox.showinfo(
                "Nothing selected",
                "Select some text in the reader first, then click 🖍 Highlight.",
            )
            return
        if not text.strip():
            return
        color = color_name or self.highlight_color_var.get() or "Yellow"
        tag = self._highlight_tag(color)
        self.text_area.tag_add(tag, s_idx, e_idx)
        book_key = self._book_key(self.current_file)
        if book_key:
            try:
                self._db_exec(
                    "INSERT INTO highlights "
                    "(book, start_offset, end_offset, text, color, created_at) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (book_key, self._char_offset(s_idx), self._char_offset(e_idx),
                     text, color, datetime.now().isoformat()),
                )
                self.set_status(f"🖍 Highlighted in {color} (saved).")
            except Exception as e:
                self.set_status(f"🖍 Highlighted in {color} (not saved: {e}).")
        else:
            self.set_status(
                f"🖍 Highlighted in {color} (session only — open a saved book to persist).")

    def remove_highlights_in_selection(self) -> None:
        """Clear color tags in the current selection AND delete matching
        rows in the database so they don't come back on reload."""
        try:
            s_idx = self.text_area.index(tk.SEL_FIRST)
            e_idx = self.text_area.index(tk.SEL_LAST)
        except tk.TclError:
            messagebox.showinfo("Nothing selected",
                                "Select the highlighted text first.")
            return
        for color in self.HIGHLIGHT_COLORS:
            try:
                self.text_area.tag_remove(f"hl_{color.lower()}", s_idx, e_idx)
            except tk.TclError:
                pass
        book_key = self._book_key(self.current_file)
        if not book_key:
            return
        s_off = self._char_offset(s_idx)
        e_off = self._char_offset(e_idx)
        try:
            self._db_exec(
                "DELETE FROM highlights WHERE book = ? "
                "AND NOT (end_offset <= ? OR start_offset >= ?)",
                (book_key, s_off, e_off),
            )
        except Exception:
            pass
        self.set_status("Highlight removed.")

    def _render_persisted_highlights(self) -> None:
        """Re-apply all stored highlights for the loaded book."""
        book_key = self._book_key(self.current_file)
        if not book_key:
            return
        try:
            rows = self._db_query(
                "SELECT start_offset, end_offset, color FROM highlights "
                "WHERE book = ?", (book_key,),
            )
        except Exception:
            return
        for s_off, e_off, color in rows:
            tag = self._highlight_tag(color)
            try:
                self.text_area.tag_add(
                    tag,
                    self._tk_index_for_offset(s_off),
                    self._tk_index_for_offset(e_off),
                )
            except tk.TclError:
                continue

    # ---- Reading timer (5 / 10 / 15 / 20 / 25 minute presets) ----------
    def toggle_timer(self) -> None:
        """Start or stop the countdown timer."""
        if self._timer_running:
            self._stop_timer(announce=False)
        else:
            self._start_timer()

    def _start_timer(self, duration_min: int | None = None) -> None:
        """Start the Pomodoro timer. If `duration_min` is given, use it
        directly (this is how the Matrix's block "▶ Start" button hands
        off to the timer). Otherwise fall back to the dropdown preset."""
        if duration_min is None:
            preset = self.timer_preset_var.get()
            duration_min = self._timer_presets.get(preset, 10)
        self._timer_remaining_seconds = int(duration_min) * 60
        self._timer_running = True
        self.timer_button.configure(text="Stop", bg=ACCENT_RED,
                                     activebackground=ACCENT_RED)
        self._update_timer_display()
        self._tick_timer()
        self.set_status(
            f"⏱ Timer started — {duration_min} minute"
            f"{'s' if duration_min != 1 else ''}.")

    def _tick_timer(self) -> None:
        if not self._timer_running:
            return
        if self._timer_remaining_seconds <= 0:
            self._timer_done()
            return
        self._timer_remaining_seconds -= 1
        self._update_timer_display()
        self._timer_after_id = self.root.after(1000, self._tick_timer)

    def _update_timer_display(self) -> None:
        secs = max(0, self._timer_remaining_seconds)
        m, s = divmod(secs, 60)
        self.timer_display_var.set(f"{m:02d}:{s:02d}")

    def _stop_timer(self, announce: bool = True) -> None:
        """Cancel the countdown and reset the UI to idle."""
        self._timer_running = False
        if self._timer_after_id is not None:
            try:
                self.root.after_cancel(self._timer_after_id)
            except Exception:
                pass
            self._timer_after_id = None
        try:
            self.timer_button.configure(text="Start", bg=ACCENT_GREEN,
                                         activebackground=ACCENT_GREEN)
            self.timer_display_var.set("00:00")
        except Exception:
            pass
        if announce:
            self.set_status("⏱ Timer stopped.")

    def _timer_done(self) -> None:
        """Countdown reached zero — play a beep, reset the button,
        and pop up a non-blocking 'Time's up' notice."""
        self._timer_running = False
        self._timer_after_id = None
        try:
            self.timer_button.configure(text="Start", bg=ACCENT_GREEN,
                                         activebackground=ACCENT_GREEN)
            self.timer_display_var.set("00:00")
        except Exception:
            pass
        # System chime — works without any extra dependency on Windows.
        try:
            import winsound
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
        except Exception:
            pass
        self.set_status("⏱ Time's up!")
        # Use root.after so the popup doesn't block the after() callback chain.
        self.root.after(50, lambda: messagebox.showinfo(
            "⏱ Timer", "Time's up!"))

    # ---- 2. Topics (commonplace book) ----------------------------------
    def add_selection_to_topic(self, source_widget=None) -> None:
        """MOVE the current selection into a topic of the user's
        choice. Source is cleared on success when it's Notes or
        Study Notes. Reader keeps a COPY."""
        widget = source_widget if source_widget is not None else self.text_area
        text, sel_range, used_whole = self._capture_widget_text(widget)
        if not text:
            if widget is self.text_area:
                messagebox.showinfo(
                    "Nothing selected",
                    "Highlight some text first, then choose 📌 Add to topic.")
            else:
                messagebox.showinfo("Nothing to send",
                                     "There's no text in the panel to send.")
            return
        try:
            rows = self._db_query("SELECT id, title FROM topics "
                                  "ORDER BY title COLLATE NOCASE")
        except Exception as e:
            messagebox.showerror("Database error", str(e))
            return
        topic_id = self._pick_or_create_topic_dialog(rows)
        if topic_id is None:
            return
        # Source linkage only makes sense for reader selections — that's
        # what the (book_key, char_offset) anchor refers to.
        if widget is self.text_area and sel_range is not None:
            source_key = self._book_key(self.current_file)
            source_off = (self._char_offset(sel_range[0])
                          if source_key else None)
        else:
            source_key = None
            source_off = None
        try:
            self._db_exec(
                "INSERT INTO topic_entries "
                "(topic_id, text, source_book, source_offset, created_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (topic_id, text, source_key, source_off,
                 datetime.now().isoformat()),
            )
        except Exception as e:
            messagebox.showerror("Could not save topic entry", str(e))
            return
        self._clear_moved_source(widget, sel_range, used_whole)
        self.set_status("📌 Moved to topic.")

    def _pick_or_create_topic_dialog(self, topics: list[tuple]) -> int | None:
        """Modal: pick an existing topic or type a new name. Returns the
        topic id, or None on cancel."""
        dlg = tk.Toplevel(self.root)
        dlg.title("Add to topic")
        dlg.configure(bg=BG_DARK)
        dlg.transient(self.root)
        dlg.grab_set()
        dlg.geometry("420x440")

        tk.Label(dlg, text="Pick an existing topic, or type a new one:",
                 bg=BG_DARK, fg=FG_TEXT, font=("Segoe UI", 11, "bold"),
                 padx=14, pady=10).pack(anchor=tk.W)

        listbox = tk.Listbox(
            dlg, bg=BG_INPUT, fg=FG_TEXT,
            selectbackground=ACCENT_CYAN, selectforeground="white",
            font=("Segoe UI", 11), relief=tk.FLAT, bd=0, highlightthickness=0,
            activestyle="none",
        )
        listbox.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 8))
        ids = [t[0] for t in topics]
        for _id, title in topics:
            listbox.insert(tk.END, title)

        tk.Label(dlg, text="Or new topic:", bg=BG_DARK, fg=FG_MUTED,
                 font=("Segoe UI", 10), padx=14).pack(anchor=tk.W)
        entry_var = tk.StringVar()
        entry = tk.Entry(dlg, textvariable=entry_var,
                         bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT,
                         font=("Segoe UI", 11), relief=tk.FLAT, bd=0)
        entry.pack(fill=tk.X, padx=14, ipady=5, pady=(2, 10))

        out = {"id": None}

        def commit() -> None:
            new_name = entry_var.get().strip()
            if new_name:
                try:
                    tid = self._db_exec(
                        "INSERT INTO topics (title, created_at) VALUES (?, ?)",
                        (new_name, datetime.now().isoformat()),
                    )
                    out["id"] = tid
                except sqlite3.IntegrityError:
                    rows = self._db_query(
                        "SELECT id FROM topics WHERE title = ? COLLATE NOCASE",
                        (new_name,))
                    if rows:
                        out["id"] = rows[0][0]
                except Exception as e:
                    messagebox.showerror("Could not create topic",
                                          str(e), parent=dlg)
                    return
            else:
                sel = listbox.curselection()
                if not sel:
                    messagebox.showinfo(
                        "Pick or type a topic",
                        "Click an existing topic, or type a new name.",
                        parent=dlg,
                    )
                    return
                out["id"] = ids[sel[0]]
            dlg.destroy()

        btn_row = tk.Frame(dlg, bg=BG_DARK, padx=14, pady=10)
        btn_row.pack(fill=tk.X)
        tk.Button(btn_row, text="Add", command=commit,
                  font=("Segoe UI", 11, "bold"), bg=ACCENT_GREEN, fg="white",
                  activebackground=ACCENT_GREEN, relief=tk.FLAT,
                  padx=14, pady=6, cursor="hand2", borderwidth=0,
                  ).pack(side=tk.RIGHT, padx=(6, 0))
        tk.Button(btn_row, text="Cancel", command=dlg.destroy,
                  font=("Segoe UI", 11, "bold"), bg=ACCENT_SLATE, fg="white",
                  activebackground=ACCENT_SLATE, relief=tk.FLAT,
                  padx=14, pady=6, cursor="hand2", borderwidth=0,
                  ).pack(side=tk.RIGHT)

        entry.bind("<Return>", lambda _e: commit())
        listbox.bind("<Double-Button-1>", lambda _e: commit())
        listbox.focus_set()
        dlg.wait_window()
        return out["id"]

    # ---- 3. Bookmarks --------------------------------------------------
    def bookmark_here(self) -> None:
        """Save the current position with an auto-generated context label."""
        book_key = self._book_key(self.current_file)
        if not book_key:
            messagebox.showinfo(
                "Cannot bookmark",
                "Bookmarks need a saved book. Open one from 📂 Open or "
                "📚 Library first.",
            )
            return
        try:
            cursor_idx = self.text_area.index(tk.INSERT)
            top_idx    = self.text_area.index("@0,0")
            cursor_off = self._char_offset(cursor_idx)
            top_off    = self._char_offset(top_idx)
            visible_end = self._char_offset(self.text_area.index(
                f"@0,{self.text_area.winfo_height()}"))
            position = cursor_off if top_off <= cursor_off <= visible_end else top_off
        except tk.TclError:
            position = 0
        try:
            snippet_idx = self._tk_index_for_offset(position)
            snippet = self.text_area.get(snippet_idx, f"{snippet_idx} + 80 chars")
            snippet = " ".join(snippet.split())[:60]
        except tk.TclError:
            snippet = ""
        label = snippet or f"Position {position}"
        try:
            self._db_exec(
                "INSERT INTO bookmarks (book, position, label, created_at) "
                "VALUES (?, ?, ?, ?)",
                (book_key, position, label, datetime.now().isoformat()),
            )
            display = label[:40] + ("…" if len(label) > 40 else "")
            self.set_status(f"🔖 Bookmarked: {display}")
        except Exception as e:
            messagebox.showerror("Bookmark failed", str(e))

    def _jump_to_book_offset(self, book_key: str, position: int) -> None:
        """Open the book (if not already loaded) and scroll to position."""
        path = self._book_path_for_key(book_key)
        if not path or not os.path.exists(path):
            messagebox.showerror(
                "Book file missing",
                f"This pointer references a book that's no longer on disk:\n\n{path}",
            )
            return
        if self._book_key(self.current_file) != book_key:
            self._load_book(path)
        try:
            idx = self._tk_index_for_offset(position)
            self.text_area.mark_set(tk.INSERT, idx)
            self.text_area.see(idx)
            self.text_area.focus_set()
        except tk.TclError:
            pass

    # ---- 4a. Glossary --------------------------------------------------
    def lookup_selected_in_glossary(self, source_widget=None) -> None:
        """Look up the selected word/phrase; offer to define it if not
        present. `source_widget` defaults to the reader."""
        widget = source_widget if source_widget is not None else self.text_area
        try:
            term = widget.get(tk.SEL_FIRST, tk.SEL_LAST).strip()
        except tk.TclError:
            term = ""
        if not term:
            entered = self._prompt_for_text("Look up term", "Enter a term:")
            if not entered:
                return
            term = entered.strip()
            if not term:
                return
        rows = self._db_query(
            "SELECT term, definition, source FROM glossary "
            "WHERE term = ? COLLATE NOCASE", (term,),
        )
        if rows:
            t, d, src = rows[0]
            self._show_glossary_entry(t, d, src or "")
        else:
            if messagebox.askyesno(
                "Not in glossary",
                f"'{term}' isn't in your glossary yet.\n\nDefine it now?",
            ):
                self._edit_glossary_entry(
                    term=term, definition="",
                    source=self._book_key(self.current_file) or "",
                )

    def _prompt_for_text(self, title: str, prompt: str) -> str | None:
        """Tiny themed text-input dialog. Returns text or None on cancel."""
        dlg = tk.Toplevel(self.root)
        dlg.title(title)
        dlg.configure(bg=BG_DARK)
        dlg.transient(self.root)
        dlg.grab_set()
        dlg.geometry("400x150")
        tk.Label(dlg, text=prompt, bg=BG_DARK, fg=FG_TEXT,
                 font=("Segoe UI", 11), padx=14, pady=14).pack(anchor=tk.W)
        var = tk.StringVar()
        e = tk.Entry(dlg, textvariable=var, bg=BG_INPUT, fg=FG_TEXT,
                     insertbackground=FG_TEXT, font=("Segoe UI", 11),
                     relief=tk.FLAT, bd=0)
        e.pack(fill=tk.X, padx=14, ipady=5)
        e.focus_set()
        out = {"v": None}
        def ok():
            out["v"] = var.get(); dlg.destroy()
        row = tk.Frame(dlg, bg=BG_DARK, padx=14, pady=12)
        row.pack(fill=tk.X)
        tk.Button(row, text="OK", command=ok, font=("Segoe UI", 11, "bold"),
                  bg=ACCENT_GREEN, fg="white", activebackground=ACCENT_GREEN,
                  relief=tk.FLAT, padx=14, pady=6, cursor="hand2", borderwidth=0,
                  ).pack(side=tk.RIGHT, padx=(6, 0))
        tk.Button(row, text="Cancel", command=dlg.destroy,
                  font=("Segoe UI", 11, "bold"), bg=ACCENT_SLATE, fg="white",
                  activebackground=ACCENT_SLATE, relief=tk.FLAT,
                  padx=14, pady=6, cursor="hand2", borderwidth=0,
                  ).pack(side=tk.RIGHT)
        e.bind("<Return>", lambda _e: ok())
        dlg.wait_window()
        return out["v"]

    def _show_glossary_entry(self, term: str, definition: str, source: str) -> None:
        """Read-only popup showing a single glossary entry."""
        dlg = tk.Toplevel(self.root)
        dlg.title(f"📒 {term}")
        dlg.configure(bg=BG_DARK)
        dlg.transient(self.root)
        dlg.geometry("520x380")
        tk.Label(dlg, text=term, bg=BG_DARK, fg=FG_TEXT,
                 font=("Segoe UI", 16, "bold"), padx=16, pady=12,
                 anchor=tk.W).pack(fill=tk.X)
        body = scrolledtext.ScrolledText(
            dlg, wrap=tk.WORD, font=("Segoe UI", 12),
            bg=BG_INPUT, fg=FG_TEXT, padx=14, pady=12, relief=tk.FLAT,
        )
        body.pack(fill=tk.BOTH, expand=True, padx=14, pady=4)
        body.insert("1.0", definition)
        body.configure(state=tk.DISABLED)
        if source:
            src_label = (self._book_short_label(source)
                         if source.startswith(("lib:", "abs:")) else source)
            tk.Label(dlg, text=f"Source: {src_label}",
                     bg=BG_DARK, fg=FG_MUTED, font=("Segoe UI", 10),
                     padx=14).pack(anchor=tk.W)
        row = tk.Frame(dlg, bg=BG_DARK, padx=14, pady=10)
        row.pack(fill=tk.X)
        tk.Button(row, text="Edit",
                  command=lambda: (dlg.destroy(),
                                   self._edit_glossary_entry(
                                       term=term, definition=definition,
                                       source=source)),
                  font=("Segoe UI", 11, "bold"), bg=ACCENT_CYAN, fg="white",
                  activebackground=ACCENT_CYAN, relief=tk.FLAT, padx=14, pady=6,
                  cursor="hand2", borderwidth=0,
                  ).pack(side=tk.LEFT)
        tk.Button(row, text="Close", command=dlg.destroy,
                  font=("Segoe UI", 11, "bold"), bg=ACCENT_SLATE, fg="white",
                  activebackground=ACCENT_SLATE, relief=tk.FLAT,
                  padx=14, pady=6, cursor="hand2", borderwidth=0,
                  ).pack(side=tk.RIGHT)

    def _edit_glossary_entry(self, term: str = "", definition: str = "",
                              source: str = "",
                              existing_id: int | None = None) -> None:
        """Add or edit a glossary entry."""
        dlg = tk.Toplevel(self.root)
        dlg.title("📒 Glossary entry")
        dlg.configure(bg=BG_DARK)
        dlg.transient(self.root)
        dlg.grab_set()
        dlg.geometry("560x460")

        tk.Label(dlg, text="Term:", bg=BG_DARK, fg=FG_MUTED,
                 font=("Segoe UI", 10), padx=14, pady=(12, 2)).pack(anchor=tk.W)
        term_var = tk.StringVar(value=term)
        term_e = tk.Entry(dlg, textvariable=term_var,
                          bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT,
                          font=("Segoe UI", 12, "bold"), relief=tk.FLAT, bd=0)
        term_e.pack(fill=tk.X, padx=14, ipady=5)

        tk.Label(dlg, text="Definition:", bg=BG_DARK, fg=FG_MUTED,
                 font=("Segoe UI", 10), padx=14, pady=(10, 2)).pack(anchor=tk.W)
        body = scrolledtext.ScrolledText(
            dlg, wrap=tk.WORD, font=("Segoe UI", 11),
            bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT,
            padx=12, pady=10, relief=tk.FLAT, undo=True,
        )
        body.pack(fill=tk.BOTH, expand=True, padx=14, pady=4)
        if definition:
            body.insert("1.0", definition)

        def save():
            t = term_var.get().strip()
            d = body.get("1.0", tk.END).strip()
            if not t:
                messagebox.showinfo("Term required",
                                     "Enter a term first.", parent=dlg)
                return
            if not d:
                messagebox.showinfo("Definition required",
                                     "Enter a definition.", parent=dlg)
                return
            now = datetime.now().isoformat()
            try:
                if existing_id is not None:
                    self._db_exec(
                        "UPDATE glossary SET term=?, definition=?, source=?, "
                        "updated_at=? WHERE id=?",
                        (t, d, source, now, existing_id),
                    )
                else:
                    rows = self._db_query(
                        "SELECT id FROM glossary WHERE term=? COLLATE NOCASE",
                        (t,))
                    if rows:
                        self._db_exec(
                            "UPDATE glossary SET definition=?, source=?, "
                            "updated_at=? WHERE id=?",
                            (d, source, now, rows[0][0]),
                        )
                    else:
                        self._db_exec(
                            "INSERT INTO glossary "
                            "(term, definition, source, created_at, updated_at) "
                            "VALUES (?, ?, ?, ?, ?)",
                            (t, d, source, now, now),
                        )
            except Exception as e:
                messagebox.showerror("Could not save", str(e), parent=dlg)
                return
            self.set_status(f"📒 Saved glossary entry: {t}")
            try:
                self._refresh_tab_glossary()
            except Exception:
                pass
            dlg.destroy()

        row = tk.Frame(dlg, bg=BG_DARK, padx=14, pady=10)
        row.pack(fill=tk.X)
        tk.Button(row, text="Save", command=save,
                  font=("Segoe UI", 11, "bold"), bg=ACCENT_GREEN, fg="white",
                  activebackground=ACCENT_GREEN, relief=tk.FLAT,
                  padx=14, pady=6, cursor="hand2", borderwidth=0,
                  ).pack(side=tk.RIGHT, padx=(6, 0))
        tk.Button(row, text="Cancel", command=dlg.destroy,
                  font=("Segoe UI", 11, "bold"), bg=ACCENT_SLATE, fg="white",
                  activebackground=ACCENT_SLATE, relief=tk.FLAT,
                  padx=14, pady=6, cursor="hand2", borderwidth=0,
                  ).pack(side=tk.RIGHT)

        (body if term else term_e).focus_set()

    # ---- 4b. Journal helpers (used by the workspace tab) ----------------
    # The Journal tab is fully built/refreshed inside the workspace; no
    # reader-side trigger method needed here.

    # ---- Study workspace (tabbed window) -------------------------------
    def open_study_workspace(self) -> None:
        """Open (or focus) the Study workspace. Acts as 'restore' too —
        if the window is iconified, this brings it back."""
        if self._study_win is not None:
            try:
                if self._study_win.winfo_exists():
                    # `deiconify` un-minimizes; `lift` + `focus_force`
                    # raise it above other windows.
                    try:
                        self._study_win.deiconify()
                    except Exception:
                        pass
                    self._study_win.lift()
                    self._study_win.focus_force()
                    return
            except Exception:
                pass
            self._study_win = None

        win = tk.Toplevel(self.root)
        self._study_win = win
        win.title("📓 Study workspace")
        win.geometry("1200x680")
        win.minsize(640, 420)
        win.configure(bg=BG_DARK)
        # NOTE: do NOT call win.transient(self.root) here. A transient
        # window on Windows doesn't get its own taskbar entry, so once
        # it's iconified there's no way for the user to restore it from
        # the taskbar. The Study window is rich enough to deserve a
        # proper top-level identity — separate taskbar button, normal
        # Alt+Tab participation, independent minimize/restore.

        def on_close():
            # Force-save any pending Matrix edits before the widgets die.
            try:
                if self._eisenhower_widgets:
                    self._save_all_eisenhower()
            except Exception:
                pass
            # Force-save pending Study Notes too.
            try:
                if self._study_notes_widget is not None:
                    self._save_study_notes()
            except Exception:
                pass
            # If the mic target points at a Study workspace widget that's
            # about to be destroyed (Matrix quadrant, journal body, or
            # study notes), redirect it back to Notes so the next mic
            # session lands somewhere real.
            try:
                doomed = set(self._eisenhower_widgets.values())
                for w in (getattr(self, "_journal_body", None),
                          getattr(self, "_study_notes_widget", None)):
                    if w is not None:
                        doomed.add(w)
                if self._mic_target in doomed:
                    self._mic_target = self.notes_area
            except Exception:
                pass
            self._eisenhower_widgets = {}
            self._eisenhower_save_after_ids = {}
            self._study_notes_widget = None
            self._study_notes_save_after_id = None
            self._study_win = None
            win.destroy()
        win.protocol("WM_DELETE_WINDOW", on_close)

        tabbar = tk.Frame(win, bg=BG_PANEL, padx=10, pady=8)
        tabbar.pack(fill=tk.X)
        content = tk.Frame(win, bg=BG_DARK)
        content.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        self._study_tab_frames = {}
        self._study_tab_buttons = {}

        tabs = [
            ("highlights",  "🖍 Highlights",  self._build_tab_highlights),
            ("workflow",    "🗂 Workflow",    self._build_tab_workflow),
            ("study_notes", "📝 Study Notes", self._build_tab_study_notes),
            ("topics",      "📌 Topics",      self._build_tab_topics),
            ("bookmarks",   "🔖 Bookmarks",   self._build_tab_bookmarks),
            ("glossary",    "📒 Glossary",    self._build_tab_glossary),
            ("journal",     "📅 Journal",     self._build_tab_journal),
            ("matrix",      "🎯 Matrix",      self._build_tab_eisenhower),
            ("audit",       "🔍 Audit",       self._build_tab_audit),
            ("prompts",     "💬 Prompts",     self._build_tab_prompts),
        ]
        for key, label, builder in tabs:
            b = tk.Button(
                tabbar, text=label,
                command=lambda k=key: self._show_study_tab(k),
                font=("Segoe UI", 11, "bold"),
                bg=BG_INPUT, fg=FG_TEXT,
                activebackground=ACCENT_SLATE, activeforeground="white",
                relief=tk.FLAT, padx=11, pady=8, cursor="hand2", borderwidth=0,
            )
            b.pack(side=tk.LEFT, padx=(0, 3))
            self._study_tab_buttons[key] = b
            f = tk.Frame(content, bg=BG_DARK)
            self._study_tab_frames[key] = f
            builder(f)

        # Expand / Restore toggle in the upper-right of the tab bar.
        # Click to maximize the Study window so the active tab gets the
        # whole screen; click again to return to the normal size.
        self._study_expanded = False
        expand_btn = tk.Button(
            tabbar, text="⛶  Expand",
            font=("Segoe UI", 11, "bold"),
            bg=ACCENT_CYAN, fg="white", activebackground=ACCENT_CYAN,
            relief=tk.FLAT, padx=14, pady=8, cursor="hand2", borderwidth=0,
        )
        def _toggle_expand():
            try:
                if self._study_expanded:
                    win.state("normal")
                    expand_btn.configure(text="⛶  Expand")
                    self._study_expanded = False
                else:
                    win.state("zoomed")     # Windows full-screen maximize
                    expand_btn.configure(text="⛶  Restore")
                    self._study_expanded = True
            except tk.TclError:
                # Fallback if the platform doesn't support 'zoomed':
                # size the window to the full screen manually.
                try:
                    if self._study_expanded:
                        win.geometry("960x680")
                        expand_btn.configure(text="⛶  Expand")
                        self._study_expanded = False
                    else:
                        sw = win.winfo_screenwidth()
                        sh = win.winfo_screenheight()
                        win.geometry(f"{sw}x{sh}+0+0")
                        expand_btn.configure(text="⛶  Restore")
                        self._study_expanded = True
                except Exception:
                    pass
        expand_btn.configure(command=_toggle_expand)
        expand_btn.pack(side=tk.RIGHT, padx=(8, 0))

        # Minimize button — sends the Study window to the taskbar. Sits
        # to the left of Expand so the upper-right reads [— Minimize][⛶ …].
        # (Pack order with side=RIGHT means later-packed widgets land
        # further to the left of earlier ones.)
        min_btn = tk.Button(
            tabbar, text="—  Minimize",
            command=lambda: win.iconify(),
            font=("Segoe UI", 11, "bold"),
            bg=ACCENT_SLATE, fg="white", activebackground=ACCENT_SLATE,
            relief=tk.FLAT, padx=14, pady=8, cursor="hand2", borderwidth=0,
        )
        min_btn.pack(side=tk.RIGHT, padx=(4, 0))

        self._show_study_tab("highlights")

    # ---- Audit tab ------------------------------------------------------
    # Matches the rubric structure shared by the Walkenbach Excel audits
    # in the A1 Form & System course (Parts XIX–XX, every Course-Week tab)
    # and the Sentinel Prime field_schema audit pattern. Five columns:
    # #  |  Finding  |  Where  |  Grade  |  Recommended fix
    # Plus an overall grade and a closing "Mentor's Note" — the warm,
    # italic register the A1 workbook closes every Part with.
    def _build_tab_audit(self, parent: tk.Frame) -> None:
        # Two-pane: left = audit list, right = selected audit detail.
        wrap = tk.Frame(parent, bg=BG_DARK)
        wrap.pack(fill=tk.BOTH, expand=True)

        # --- Left: audit list -----------------------------------------
        left = tk.Frame(wrap, bg=BG_DARK, padx=8, pady=8)
        left.pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(left, text="Audits", bg=BG_DARK, fg=FG_MUTED,
                 font=("Segoe UI", 10, "bold")).pack(anchor=tk.W)
        list_box = tk.Listbox(
            left, width=28, height=18,
            bg=BG_INPUT, fg=FG_TEXT,
            selectbackground=ACCENT_CYAN, selectforeground="white",
            font=("Segoe UI", 10), activestyle="none",
            relief=tk.FLAT, bd=0, highlightthickness=0,
        )
        list_box.pack(fill=tk.Y, expand=True, pady=(4, 6))
        list_box.bind("<<ListboxSelect>>", lambda _e: self._audit_on_list_select())
        self._audit_listbox = list_box
        list_btns = tk.Frame(left, bg=BG_DARK)
        list_btns.pack(fill=tk.X)
        def lb(text: str, cmd, color: str) -> tk.Button:
            return tk.Button(
                list_btns, text=text, command=cmd,
                font=("Segoe UI", 9, "bold"),
                bg=color, fg="white", activebackground=color,
                relief=tk.FLAT, padx=8, pady=4, cursor="hand2", borderwidth=0,
            )
        lb("+ New",   self._audit_new,             ACCENT_GREEN
           ).pack(side=tk.LEFT, padx=(0, 4))
        lb("Delete", self._audit_delete_current,   ACCENT_RED
           ).pack(side=tk.LEFT, padx=4)
        lb("Refresh", self._refresh_tab_audit,     ACCENT_SLATE
           ).pack(side=tk.LEFT, padx=4)

        # --- Right: audit detail --------------------------------------
        right = tk.Frame(wrap, bg=BG_DARK, padx=12, pady=8)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Title + Subject
        tk.Label(right, text="Title", bg=BG_DARK, fg=FG_MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor=tk.W)
        self._audit_title_var = tk.StringVar()
        tk.Entry(right, textvariable=self._audit_title_var,
                 bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT,
                 font=("Segoe UI", 12, "bold"),
                 relief=tk.FLAT, bd=0
                 ).pack(fill=tk.X, ipady=6, pady=(2, 8))
        self._audit_title_var.trace_add("write",
                                         lambda *_: self._audit_schedule_save())

        tk.Label(right, text="Subject (book, chapter, note, project…)",
                 bg=BG_DARK, fg=FG_MUTED, font=("Segoe UI", 9)
                 ).pack(anchor=tk.W)
        self._audit_subject_var = tk.StringVar()
        tk.Entry(right, textvariable=self._audit_subject_var,
                 bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT,
                 font=("Segoe UI", 10),
                 relief=tk.FLAT, bd=0
                 ).pack(fill=tk.X, ipady=4, pady=(2, 12))
        self._audit_subject_var.trace_add("write",
                                          lambda *_: self._audit_schedule_save())

        # Findings header
        head = tk.Frame(right, bg=BG_PANEL, padx=6, pady=4)
        head.pack(fill=tk.X)
        cols = [("#", 3), ("Finding", 28), ("Where", 14),
                ("Grade", 6), ("Recommended fix", 28), ("", 3)]
        for label, w in cols:
            tk.Label(head, text=label, bg=BG_PANEL, fg=FG_TEXT,
                     font=("Segoe UI", 9, "bold"), width=w, anchor=tk.W
                     ).pack(side=tk.LEFT, padx=2)

        # Scrollable findings container
        findings_scroll_holder = tk.Frame(right, bg=BG_DARK)
        findings_scroll_holder.pack(fill=tk.BOTH, expand=True, pady=(4, 8))
        canvas = tk.Canvas(findings_scroll_holder, bg=BG_DARK,
                            highlightthickness=0, borderwidth=0)
        fsb = tk.Scrollbar(findings_scroll_holder, command=canvas.yview)
        canvas.configure(yscrollcommand=fsb.set)
        fsb.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        inner = tk.Frame(canvas, bg=BG_DARK)
        inner_id = canvas.create_window((0, 0), window=inner, anchor="nw")
        def _on_inner_config(_e=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfigure(inner_id, width=canvas.winfo_width())
        inner.bind("<Configure>", _on_inner_config)
        canvas.bind("<Configure>", _on_inner_config)
        self._audit_findings_frame = inner

        # Action row + summary
        action_row = tk.Frame(right, bg=BG_DARK)
        action_row.pack(fill=tk.X)
        tk.Button(action_row, text="+ Add Finding",
                  command=self._audit_add_finding,
                  bg=ACCENT_CYAN, fg="white",
                  font=("Segoe UI", 10, "bold"),
                  relief=tk.FLAT, padx=10, pady=5,
                  cursor="hand2", borderwidth=0
                  ).pack(side=tk.LEFT)
        tk.Label(action_row, text="    Overall grade:",
                 bg=BG_DARK, fg=FG_MUTED, font=("Segoe UI", 10)
                 ).pack(side=tk.LEFT)
        self._audit_overall_var = tk.StringVar(value="")
        overall_menu = ttk.Combobox(action_row,
                                     textvariable=self._audit_overall_var,
                                     values=list(AUDIT_GRADES),
                                     width=5, state="readonly")
        overall_menu.pack(side=tk.LEFT, padx=4)
        self._audit_overall_var.trace_add("write",
                                          lambda *_: self._audit_schedule_save())

        # Mentor's Note (warm, italic register from the A1 workbook style)
        tk.Label(right, text="Mentor's Note (closing summary, plain language)",
                 bg=BG_DARK, fg=FG_MUTED, font=("Segoe UI", 9)
                 ).pack(anchor=tk.W, pady=(10, 2))
        note = tk.Text(right, height=4,
                       bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT,
                       font=("Segoe UI", 10, "italic"),
                       relief=tk.FLAT, bd=0, wrap=tk.WORD)
        note.pack(fill=tk.X)
        self._audit_mentors_widget = note
        note.bind("<<Modified>>", self._audit_on_note_modified)

        self._refresh_tab_audit()

    # --- list / refresh ----------------------------------------------
    def _refresh_tab_audit(self) -> None:
        if self._audit_listbox is None:
            return
        try:
            rows = self._db_query(
                "SELECT id, title, updated_at FROM audits "
                "ORDER BY updated_at DESC"
            )
        except sqlite3.Error:
            rows = []
        self._audit_items = [(r[0], r[1] or "(untitled)") for r in rows]
        lb = self._audit_listbox
        lb.delete(0, tk.END)
        for _id, title in self._audit_items:
            lb.insert(tk.END, title[:30])
        # Restore selection if the current audit still exists; otherwise
        # clear the detail pane.
        if self._audit_current_id is not None:
            for i, (aid, _t) in enumerate(self._audit_items):
                if aid == self._audit_current_id:
                    lb.selection_clear(0, tk.END)
                    lb.selection_set(i)
                    lb.see(i)
                    return
        self._audit_current_id = None
        self._audit_clear_detail()

    def _audit_on_list_select(self) -> None:
        if self._audit_listbox is None:
            return
        sel = self._audit_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        if idx >= len(self._audit_items):
            return
        self._audit_load(self._audit_items[idx][0])

    # --- CRUD --------------------------------------------------------
    def _audit_new(self) -> None:
        now = datetime.now().isoformat(timespec="seconds")
        try:
            new_id = self._db_exec(
                "INSERT INTO audits "
                "(title, subject, overall_grade, mentors_note, "
                "findings_json, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                ("New audit", "", "", "", "[]", now, now),
            )
        except sqlite3.Error as e:
            messagebox.showerror("Audit error", str(e))
            return
        self._audit_current_id = new_id
        self._refresh_tab_audit()
        self._audit_load(new_id)
        if self._audit_title_var is not None:
            try:
                # Pre-select the placeholder title so the user can just
                # start typing.
                pass
            except tk.TclError:
                pass

    def _audit_delete_current(self) -> None:
        if self._audit_current_id is None:
            messagebox.showinfo("Nothing selected",
                                "Pick an audit on the left first.")
            return
        title = next((t for i, t in self._audit_items
                      if i == self._audit_current_id), "this audit")
        if not messagebox.askyesno("Delete audit?",
                                    f"Permanently delete \"{title}\"?"):
            return
        try:
            self._db_exec("DELETE FROM audits WHERE id=?",
                          (self._audit_current_id,))
        except sqlite3.Error as e:
            messagebox.showerror("Delete failed", str(e))
            return
        self._audit_current_id = None
        self._refresh_tab_audit()

    def _audit_load(self, audit_id: int) -> None:
        try:
            rows = self._db_query(
                "SELECT title, subject, overall_grade, mentors_note, "
                "findings_json FROM audits WHERE id=?",
                (audit_id,),
            )
        except sqlite3.Error:
            rows = []
        if not rows:
            return
        title, subject, overall, mentors, findings_json = rows[0]
        # Pause autosave while we re-hydrate the widgets to avoid a
        # spurious write triggered by the StringVar updates below.
        prev = self._audit_save_after_id
        self._audit_save_after_id = "__loading__"
        self._audit_current_id = audit_id
        if self._audit_title_var is not None:
            self._audit_title_var.set(title or "")
        if self._audit_subject_var is not None:
            self._audit_subject_var.set(subject or "")
        if self._audit_overall_var is not None:
            self._audit_overall_var.set(overall or "")
        if self._audit_mentors_widget is not None:
            self._audit_mentors_widget.delete("1.0", tk.END)
            if mentors:
                self._audit_mentors_widget.insert("1.0", mentors)
            self._audit_mentors_widget.edit_modified(False)
        try:
            findings = json.loads(findings_json or "[]")
            if not isinstance(findings, list):
                findings = []
        except json.JSONDecodeError:
            findings = []
        self._audit_render_findings(findings)
        # Resume normal autosave behavior
        self._audit_save_after_id = (
            None if prev == "__loading__" else prev
        )

    def _audit_clear_detail(self) -> None:
        if self._audit_title_var is not None:
            self._audit_title_var.set("")
        if self._audit_subject_var is not None:
            self._audit_subject_var.set("")
        if self._audit_overall_var is not None:
            self._audit_overall_var.set("")
        if self._audit_mentors_widget is not None:
            try:
                self._audit_mentors_widget.delete("1.0", tk.END)
                self._audit_mentors_widget.edit_modified(False)
            except tk.TclError:
                pass
        self._audit_render_findings([])

    # --- findings rendering -------------------------------------------
    def _audit_render_findings(self, findings: list[dict]) -> None:
        """Rebuild the findings rows from a list of dicts. Each row is a
        small frame with four widgets (finding entry, location entry,
        grade combobox, fix entry) + a delete button. We rebuild rather
        than patch — the list is short, the cost is negligible."""
        frame = self._audit_findings_frame
        if frame is None:
            return
        for child in frame.winfo_children():
            child.destroy()
        self._audit_finding_widgets = []
        for i, item in enumerate(findings):
            self._audit_make_finding_row(i, item)

    def _audit_make_finding_row(self, position: int,
                                 data: dict | None = None) -> None:
        if self._audit_findings_frame is None:
            return
        data = data or {}
        row = tk.Frame(self._audit_findings_frame, bg=BG_DARK)
        row.pack(fill=tk.X, pady=1)

        tk.Label(row, text=str(position + 1),
                 bg=BG_DARK, fg=FG_MUTED, font=("Segoe UI", 10),
                 width=3, anchor=tk.W
                 ).pack(side=tk.LEFT, padx=2)

        f_var = tk.StringVar(value=data.get("finding", ""))
        l_var = tk.StringVar(value=data.get("location", ""))
        g_var = tk.StringVar(value=data.get("grade", ""))
        x_var = tk.StringVar(value=data.get("fix", ""))

        def _on_change(*_a):
            self._audit_schedule_save()

        for var in (f_var, l_var, g_var, x_var):
            var.trace_add("write", _on_change)

        tk.Entry(row, textvariable=f_var,
                 bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT,
                 font=("Segoe UI", 10),
                 relief=tk.FLAT, bd=0, width=28
                 ).pack(side=tk.LEFT, padx=2, ipady=2)
        tk.Entry(row, textvariable=l_var,
                 bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT,
                 font=("Segoe UI", 10),
                 relief=tk.FLAT, bd=0, width=14
                 ).pack(side=tk.LEFT, padx=2, ipady=2)
        ttk.Combobox(row, textvariable=g_var,
                      values=list(AUDIT_GRADES),
                      width=5, state="readonly"
                      ).pack(side=tk.LEFT, padx=2)
        tk.Entry(row, textvariable=x_var,
                 bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT,
                 font=("Segoe UI", 10),
                 relief=tk.FLAT, bd=0, width=28
                 ).pack(side=tk.LEFT, padx=2, ipady=2)

        widget_ref = {
            "row": row,
            "finding_var":  f_var,
            "location_var": l_var,
            "grade_var":    g_var,
            "fix_var":      x_var,
        }

        def _remove():
            try:
                row.destroy()
            except tk.TclError:
                pass
            if widget_ref in self._audit_finding_widgets:
                self._audit_finding_widgets.remove(widget_ref)
            # Re-number the remaining rows so the # column stays sensible.
            self._audit_renumber_findings()
            self._audit_schedule_save()

        tk.Button(row, text="🗑",
                  command=_remove,
                  bg=ACCENT_SLATE, fg="white",
                  font=("Segoe UI", 9, "bold"),
                  relief=tk.FLAT, padx=4, pady=2,
                  cursor="hand2", borderwidth=0
                  ).pack(side=tk.LEFT, padx=2)

        self._audit_finding_widgets.append(widget_ref)

    def _audit_renumber_findings(self) -> None:
        """Walk the existing rows and update the # label on each one."""
        for i, w in enumerate(self._audit_finding_widgets):
            row = w["row"]
            try:
                # First child of the row is the number label
                children = row.winfo_children()
                if children:
                    children[0].configure(text=str(i + 1))
            except tk.TclError:
                pass

    def _audit_add_finding(self) -> None:
        if self._audit_current_id is None:
            self._audit_new()
            return
        self._audit_make_finding_row(len(self._audit_finding_widgets), {})
        self._audit_schedule_save()

    # --- autosave -----------------------------------------------------
    def _audit_on_note_modified(self, _event=None) -> None:
        w = self._audit_mentors_widget
        if w is None:
            return
        try:
            if not w.edit_modified():
                return
            w.edit_modified(False)
        except tk.TclError:
            return
        self._audit_schedule_save()

    def _audit_schedule_save(self) -> None:
        if self._audit_save_after_id == "__loading__":
            return  # don't autosave during _audit_load re-hydration
        if self._audit_current_id is None:
            return
        if self._audit_save_after_id:
            try:
                self.root.after_cancel(self._audit_save_after_id)
            except (tk.TclError, ValueError):
                pass
        self._audit_save_after_id = self.root.after(900, self._audit_save_now)

    def _audit_save_now(self) -> None:
        self._audit_save_after_id = None
        if self._audit_current_id is None:
            return
        findings = []
        for w in self._audit_finding_widgets:
            try:
                findings.append({
                    "finding":  w["finding_var"].get(),
                    "location": w["location_var"].get(),
                    "grade":    w["grade_var"].get(),
                    "fix":      w["fix_var"].get(),
                })
            except tk.TclError:
                continue
        title    = self._audit_title_var.get()    if self._audit_title_var    else ""
        subject  = self._audit_subject_var.get()  if self._audit_subject_var  else ""
        overall  = self._audit_overall_var.get()  if self._audit_overall_var  else ""
        mentors  = ""
        if self._audit_mentors_widget is not None:
            try:
                mentors = self._audit_mentors_widget.get("1.0", tk.END).rstrip()
            except tk.TclError:
                mentors = ""
        try:
            self._db_exec(
                "UPDATE audits SET title=?, subject=?, overall_grade=?, "
                "mentors_note=?, findings_json=?, updated_at=? WHERE id=?",
                (title, subject, overall, mentors,
                 json.dumps(findings, ensure_ascii=False),
                 datetime.now().isoformat(timespec="seconds"),
                 self._audit_current_id),
            )
        except sqlite3.Error as e:
            self.set_status(f"🔍 Audit save failed: {e}")
            return
        # Refresh the left list so a renamed title shows up immediately.
        if self._audit_listbox is not None:
            try:
                rows = self._db_query(
                    "SELECT id, title FROM audits "
                    "ORDER BY updated_at DESC"
                )
                self._audit_items = [(r[0], r[1] or "(untitled)") for r in rows]
                self._audit_listbox.delete(0, tk.END)
                for i, (aid, t) in enumerate(self._audit_items):
                    self._audit_listbox.insert(tk.END, t[:30])
                    if aid == self._audit_current_id:
                        self._audit_listbox.selection_set(i)
            except sqlite3.Error:
                pass

    # ---- Prompt journal tab --------------------------------------------
    # Schema matches docs/prompt-library/prompt-library-template.md
    # verbatim. The Iterations field is the unique value — captures the
    # refinement chain of a prompt, not just the final form.
    _PROMPT_FIELDS = (
        ("prompt",      "Prompt",         "multiline"),
        ("purpose",     "Purpose",        "single"),
        ("refs",        "References",     "single"),
        ("iterations",  "Iterations",     "multiline"),
        ("ai_tools",    "AI tools used",  "single"),
        ("input_type",  "Input Type",     "single"),
        ("output_type", "Output Type",    "single"),
        ("notes",       "Notes",          "multiline"),
    )

    def _build_tab_prompts(self, parent: tk.Frame) -> None:
        wrap = tk.Frame(parent, bg=BG_DARK)
        wrap.pack(fill=tk.BOTH, expand=True)

        # --- Left: prompt list ---------------------------------------
        left = tk.Frame(wrap, bg=BG_DARK, padx=8, pady=8)
        left.pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(left, text="Prompts", bg=BG_DARK, fg=FG_MUTED,
                 font=("Segoe UI", 10, "bold")).pack(anchor=tk.W)
        list_box = tk.Listbox(
            left, width=32, height=20,
            bg=BG_INPUT, fg=FG_TEXT,
            selectbackground=ACCENT_CYAN, selectforeground="white",
            font=("Segoe UI", 10), activestyle="none",
            relief=tk.FLAT, bd=0, highlightthickness=0,
        )
        list_box.pack(fill=tk.Y, expand=True, pady=(4, 6))
        list_box.bind("<<ListboxSelect>>",
                       lambda _e: self._prompts_on_list_select())
        self._prompts_listbox = list_box

        list_btns = tk.Frame(left, bg=BG_DARK)
        list_btns.pack(fill=tk.X)
        def lb(text: str, cmd, color: str) -> tk.Button:
            return tk.Button(
                list_btns, text=text, command=cmd,
                font=("Segoe UI", 9, "bold"),
                bg=color, fg="white", activebackground=color,
                relief=tk.FLAT, padx=8, pady=4,
                cursor="hand2", borderwidth=0,
            )
        lb("+ New",     self._prompts_new,           ACCENT_GREEN
           ).pack(side=tk.LEFT, padx=(0, 4))
        lb("Delete",   self._prompts_delete_current, ACCENT_RED
           ).pack(side=tk.LEFT, padx=4)
        lb("Refresh",  self._refresh_tab_prompts,    ACCENT_SLATE
           ).pack(side=tk.LEFT, padx=4)
        # Export below — full-width row to stand apart from list actions
        tk.Button(left, text="⤓ Export CSV",
                  command=self._prompts_export_csv,
                  bg=ACCENT_CYAN, fg="white",
                  font=("Segoe UI", 9, "bold"),
                  relief=tk.FLAT, padx=8, pady=4,
                  cursor="hand2", borderwidth=0
                  ).pack(fill=tk.X, pady=(8, 0))

        # --- Right: detail pane (scrollable) -------------------------
        right_holder = tk.Frame(wrap, bg=BG_DARK, padx=8, pady=8)
        right_holder.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        canvas = tk.Canvas(right_holder, bg=BG_DARK,
                            highlightthickness=0, borderwidth=0)
        psb = tk.Scrollbar(right_holder, command=canvas.yview)
        canvas.configure(yscrollcommand=psb.set)
        psb.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        right = tk.Frame(canvas, bg=BG_DARK)
        right_id = canvas.create_window((0, 0), window=right, anchor="nw")
        def _on_right_config(_e=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfigure(right_id, width=canvas.winfo_width())
        right.bind("<Configure>", _on_right_config)
        canvas.bind("<Configure>", _on_right_config)

        self._prompts_fields = {}
        for key, label, mode in self._PROMPT_FIELDS:
            tk.Label(right, text=label, bg=BG_DARK, fg=FG_MUTED,
                     font=("Segoe UI", 9, "bold")
                     ).pack(anchor=tk.W, pady=(6, 2))
            if mode == "multiline":
                # Prompt/Iterations/Notes deserve room to breathe.
                height = 6 if key == "iterations" else (5 if key == "prompt" else 3)
                w = tk.Text(right, height=height,
                            bg=BG_INPUT, fg=FG_TEXT,
                            insertbackground=FG_TEXT,
                            font=("Segoe UI", 10),
                            relief=tk.FLAT, bd=0, wrap=tk.WORD)
                w.pack(fill=tk.X)
                w.bind("<<Modified>>",
                        lambda _e, k=key: self._prompts_on_text_modified(k))
                self._prompts_fields[key] = w
            else:
                v = tk.StringVar()
                tk.Entry(right, textvariable=v,
                         bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT,
                         font=("Segoe UI", 11),
                         relief=tk.FLAT, bd=0
                         ).pack(fill=tk.X, ipady=4)
                v.trace_add("write",
                             lambda *_a, _k=key: self._prompts_schedule_save())
                self._prompts_fields[key] = v

        self._refresh_tab_prompts()

    def _prompts_on_text_modified(self, key: str) -> None:
        w = self._prompts_fields.get(key)
        if w is None:
            return
        try:
            if not w.edit_modified():
                return
            w.edit_modified(False)
        except tk.TclError:
            return
        self._prompts_schedule_save()

    def _refresh_tab_prompts(self) -> None:
        if self._prompts_listbox is None:
            return
        try:
            rows = self._db_query(
                "SELECT id, prompt, purpose FROM prompts "
                "ORDER BY updated_at DESC"
            )
        except sqlite3.Error:
            rows = []
        self._prompts_items = [(r[0], r[1] or "", r[2] or "") for r in rows]
        lb = self._prompts_listbox
        lb.delete(0, tk.END)
        for _id, prompt, purpose in self._prompts_items:
            head = (prompt[:30] + "…") if len(prompt) > 30 else prompt
            tag  = f" [{purpose}]" if purpose else ""
            lb.insert(tk.END, (head or "(empty)") + tag)
        if self._prompts_current_id is not None:
            for i, (pid, _p, _q) in enumerate(self._prompts_items):
                if pid == self._prompts_current_id:
                    lb.selection_clear(0, tk.END)
                    lb.selection_set(i)
                    lb.see(i)
                    return
        self._prompts_current_id = None
        self._prompts_clear_detail()

    def _prompts_on_list_select(self) -> None:
        if self._prompts_listbox is None:
            return
        sel = self._prompts_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        if idx >= len(self._prompts_items):
            return
        self._prompts_load(self._prompts_items[idx][0])

    def _prompts_new(self) -> None:
        now = datetime.now().isoformat(timespec="seconds")
        try:
            new_id = self._db_exec(
                "INSERT INTO prompts (prompt, purpose, refs, iterations, "
                "ai_tools, input_type, output_type, notes, "
                "created_at, updated_at) "
                "VALUES (?,?,?,?,?,?,?,?,?,?)",
                ("", "", "", "", "", "Text", "Text", "", now, now),
            )
        except sqlite3.Error as e:
            messagebox.showerror("Prompt error", str(e))
            return
        self._prompts_current_id = new_id
        self._refresh_tab_prompts()
        self._prompts_load(new_id)

    def _prompts_delete_current(self) -> None:
        if self._prompts_current_id is None:
            messagebox.showinfo("Nothing selected",
                                "Pick a prompt on the left first.")
            return
        if not messagebox.askyesno("Delete prompt?",
                                    "Permanently delete this prompt entry?"):
            return
        try:
            self._db_exec("DELETE FROM prompts WHERE id=?",
                          (self._prompts_current_id,))
        except sqlite3.Error as e:
            messagebox.showerror("Delete failed", str(e))
            return
        self._prompts_current_id = None
        self._refresh_tab_prompts()

    def _prompts_load(self, pid: int) -> None:
        try:
            rows = self._db_query(
                "SELECT prompt, purpose, refs, iterations, ai_tools, "
                "input_type, output_type, notes FROM prompts WHERE id=?",
                (pid,),
            )
        except sqlite3.Error:
            rows = []
        if not rows:
            return
        prev = self._prompts_save_after_id
        self._prompts_save_after_id = "__loading__"
        self._prompts_current_id = pid
        keys = [k for k, _l, _m in self._PROMPT_FIELDS]
        for key, value in zip(keys, rows[0]):
            w = self._prompts_fields.get(key)
            if w is None:
                continue
            if isinstance(w, tk.StringVar):
                w.set(value or "")
            else:
                try:
                    w.delete("1.0", tk.END)
                    if value:
                        w.insert("1.0", value)
                    w.edit_modified(False)
                except tk.TclError:
                    pass
        self._prompts_save_after_id = (
            None if prev == "__loading__" else prev
        )

    def _prompts_clear_detail(self) -> None:
        for key, w in self._prompts_fields.items():
            if isinstance(w, tk.StringVar):
                w.set("")
            else:
                try:
                    w.delete("1.0", tk.END)
                    w.edit_modified(False)
                except tk.TclError:
                    pass

    def _prompts_schedule_save(self) -> None:
        if self._prompts_save_after_id == "__loading__":
            return
        if self._prompts_current_id is None:
            return
        if self._prompts_save_after_id:
            try:
                self.root.after_cancel(self._prompts_save_after_id)
            except (tk.TclError, ValueError):
                pass
        self._prompts_save_after_id = self.root.after(
            900, self._prompts_save_now)

    def _prompts_save_now(self) -> None:
        self._prompts_save_after_id = None
        if self._prompts_current_id is None:
            return
        values: dict[str, str] = {}
        for key, _label, mode in self._PROMPT_FIELDS:
            w = self._prompts_fields.get(key)
            if w is None:
                values[key] = ""
                continue
            try:
                if isinstance(w, tk.StringVar):
                    values[key] = w.get()
                else:
                    values[key] = w.get("1.0", tk.END).rstrip()
            except tk.TclError:
                values[key] = ""
        try:
            self._db_exec(
                "UPDATE prompts SET prompt=?, purpose=?, refs=?, "
                "iterations=?, ai_tools=?, input_type=?, output_type=?, "
                "notes=?, updated_at=? WHERE id=?",
                (values["prompt"], values["purpose"], values["refs"],
                 values["iterations"], values["ai_tools"], values["input_type"],
                 values["output_type"], values["notes"],
                 datetime.now().isoformat(timespec="seconds"),
                 self._prompts_current_id),
            )
        except sqlite3.Error as e:
            self.set_status(f"💬 Prompt save failed: {e}")
            return
        # Refresh the listbox so a renamed prompt's preview updates.
        if self._prompts_listbox is not None:
            try:
                rows = self._db_query(
                    "SELECT id, prompt, purpose FROM prompts "
                    "ORDER BY updated_at DESC"
                )
                self._prompts_items = [(r[0], r[1] or "", r[2] or "")
                                       for r in rows]
                self._prompts_listbox.delete(0, tk.END)
                for i, (pid, prompt, purpose) in enumerate(self._prompts_items):
                    head = (prompt[:30] + "…") if len(prompt) > 30 else prompt
                    tag  = f" [{purpose}]" if purpose else ""
                    self._prompts_listbox.insert(tk.END,
                                                  (head or "(empty)") + tag)
                    if pid == self._prompts_current_id:
                        self._prompts_listbox.selection_set(i)
            except sqlite3.Error:
                pass

    def _prompts_export_csv(self) -> None:
        """Export all prompts to a CSV matching the Google Prompting
        Essentials template header row exactly. Single-column heading
        names; data rows below."""
        try:
            rows = self._db_query(
                "SELECT prompt, purpose, refs, iterations, ai_tools, "
                "input_type, output_type, notes FROM prompts "
                "ORDER BY updated_at DESC"
            )
        except sqlite3.Error as e:
            messagebox.showerror("Export failed", str(e))
            return
        if not rows:
            messagebox.showinfo("Nothing to export",
                                 "No prompts saved yet.")
            return
        out = filedialog.asksaveasfilename(
            title="Export prompts to CSV",
            defaultextension=".csv",
            initialfile="prompt-library.csv",
            filetypes=[("CSV", "*.csv"), ("All files", "*.*")],
        )
        if not out:
            return
        # Header must match the template exactly so the export round-trips
        # back into Google Sheets / Excel without column-name drift.
        headers = ["Prompt", "Purpose", "References", "Iterations",
                    "AI tools used", "Input Type", "Output Type", "Notes"]
        try:
            import csv as _csv
            with open(out, "w", newline="", encoding="utf-8") as f:
                w = _csv.writer(f)
                w.writerow(headers)
                for row in rows:
                    w.writerow(row)
        except OSError as e:
            messagebox.showerror("Export failed", str(e))
            return
        messagebox.showinfo(
            "Export complete",
            f"Exported {len(rows)} prompt{'s' if len(rows) != 1 else ''} "
            f"to:\n\n{out}",
        )
        self.set_status(f"💬 Exported {len(rows)} prompts → {os.path.basename(out)}")

    def _show_study_tab(self, key: str) -> None:
        for k, frame in self._study_tab_frames.items():
            frame.pack_forget()
            self._study_tab_buttons[k].configure(bg=BG_INPUT, fg=FG_TEXT)
        self._study_tab_frames[key].pack(fill=tk.BOTH, expand=True)
        self._study_tab_buttons[key].configure(bg=ACCENT_CYAN, fg="white")
        refresh = getattr(self, f"_refresh_tab_{key}", None)
        if refresh:
            try:
                refresh()
            except Exception as e:
                print(f"[study] refresh {key}: {e}", file=sys.stderr)

    # ---- Workspace tab: Highlights -------------------------------------
    def _build_tab_highlights(self, parent: tk.Frame) -> None:
        head = tk.Frame(parent, bg=BG_PANEL, padx=12, pady=8)
        head.pack(fill=tk.X)
        tk.Label(head, text="🖍 Highlights", bg=BG_PANEL, fg=FG_TEXT,
                 font=("Segoe UI", 13, "bold")).pack(side=tk.LEFT)
        self._highlights_stats_var = tk.StringVar(value="")
        tk.Label(head, textvariable=self._highlights_stats_var,
                 bg=BG_PANEL, fg=FG_MUTED, font=("Segoe UI", 10)
                 ).pack(side=tk.RIGHT)

        scope_row = tk.Frame(parent, bg=BG_DARK, padx=12, pady=4)
        scope_row.pack(fill=tk.X)
        tk.Label(scope_row, text="Show:", bg=BG_DARK, fg=FG_MUTED,
                 font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=(0, 6))
        self._highlights_scope_var = tk.StringVar(value="Current book")
        scope_menu = tk.OptionMenu(
            scope_row, self._highlights_scope_var,
            "Current book", "All books",
            command=lambda _v: self._refresh_tab_highlights(),
        )
        _style_optionmenu(scope_menu)
        scope_menu.configure(width=14)
        scope_menu.pack(side=tk.LEFT)

        list_frame = tk.Frame(parent, bg=BG_DARK, padx=12, pady=4)
        list_frame.pack(fill=tk.BOTH, expand=True)
        self._highlights_listbox = tk.Listbox(
            list_frame, bg=BG_INPUT, fg=FG_TEXT,
            selectbackground=ACCENT_CYAN, selectforeground="white",
            font=("Segoe UI", 11), relief=tk.FLAT, bd=0, highlightthickness=0,
            activestyle="none",
        )
        sb = tk.Scrollbar(list_frame, command=self._highlights_listbox.yview)
        self._highlights_listbox.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self._highlights_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._highlights_listbox.bind("<Double-Button-1>",
            lambda _e: self._jump_to_selected_highlight())
        self._highlights_listbox.bind("<Return>",
            lambda _e: self._jump_to_selected_highlight())
        # Right-click → quick actions including "Send to Study Notes".
        self._highlights_listbox.bind("<Button-3>",
            self._show_highlights_context_menu)

        row = tk.Frame(parent, bg=BG_DARK, padx=12, pady=8)
        row.pack(fill=tk.X)
        def b(text, cmd, color):
            return tk.Button(row, text=text, command=cmd,
                             font=("Segoe UI", 11, "bold"),
                             bg=color, fg="white", activebackground=color,
                             relief=tk.FLAT, padx=12, pady=6,
                             cursor="hand2", borderwidth=0)
        b("Jump to", self._jump_to_selected_highlight, ACCENT_CYAN).pack(side=tk.LEFT)
        b("Delete",  self._delete_selected_highlight,  ACCENT_RED).pack(side=tk.LEFT, padx=6)
        b("Refresh", self._refresh_tab_highlights,     ACCENT_SLATE).pack(side=tk.LEFT)

    def _refresh_tab_highlights(self) -> None:
        if not hasattr(self, "_highlights_listbox") or \
                self._highlights_listbox is None:
            return
        lb = self._highlights_listbox
        lb.delete(0, tk.END)
        scope = self._highlights_scope_var.get() if hasattr(self, "_highlights_scope_var") else "Current book"
        if scope == "All books":
            rows = self._db_query(
                "SELECT id, book, start_offset, end_offset, text, color, created_at "
                "FROM highlights ORDER BY created_at DESC")
        else:
            book = self._book_key(self.current_file)
            if not book:
                self._highlights_stats_var.set("No book loaded.")
                self._highlights_records = []
                return
            rows = self._db_query(
                "SELECT id, book, start_offset, end_offset, text, color, created_at "
                "FROM highlights WHERE book=? ORDER BY start_offset", (book,))
        self._highlights_records = rows
        for _id, book, _s, _e, text, color, _ts in rows:
            snippet = " ".join((text or "").split())[:80]
            label = self._book_short_label(book)
            lb.insert(tk.END, f" [{color:<6}] {snippet:<70}  ({label})")
        self._highlights_stats_var.set(
            f"{len(rows)} highlight{'s' if len(rows) != 1 else ''}")

    def _jump_to_selected_highlight(self) -> None:
        sel = self._highlights_listbox.curselection()
        if not sel:
            return
        _id, book, s, _e, _t, _c, _ts = self._highlights_records[sel[0]]
        self._jump_to_book_offset(book, s)

    def _delete_selected_highlight(self) -> None:
        sel = self._highlights_listbox.curselection()
        if not sel:
            return
        hid, book, s, e, _t, color, _ts = self._highlights_records[sel[0]]
        if not messagebox.askyesno("Delete highlight?", "Remove this highlight?"):
            return
        try:
            self._db_exec("DELETE FROM highlights WHERE id=?", (hid,))
        except Exception as ex:
            messagebox.showerror("Delete failed", str(ex)); return
        if self._book_key(self.current_file) == book:
            try:
                self.text_area.tag_remove(
                    f"hl_{color.lower()}",
                    self._tk_index_for_offset(s),
                    self._tk_index_for_offset(e),
                )
            except tk.TclError:
                pass
        self._refresh_tab_highlights()

    def _show_highlights_context_menu(self, event) -> None:
        """Right-click menu on the highlights list — quick send to
        Study Notes, jump to the passage, or delete."""
        # Select the row under the cursor first so the action targets it
        # even if the user hasn't single-clicked yet.
        try:
            idx = self._highlights_listbox.nearest(event.y)
            if 0 <= idx < self._highlights_listbox.size():
                self._highlights_listbox.selection_clear(0, tk.END)
                self._highlights_listbox.selection_set(idx)
                self._highlights_listbox.activate(idx)
        except tk.TclError:
            pass
        m = tk.Menu(self._highlights_listbox, tearoff=0,
                    bg=BG_PANEL, fg=FG_TEXT,
                    activebackground=ACCENT_SLATE, activeforeground="white")
        m.add_command(label="📝  Add to Study Notes",
                      command=self._add_selected_highlight_to_study_notes)
        m.add_command(label="Jump to",
                      command=self._jump_to_selected_highlight)
        m.add_separator()
        m.add_command(label="Delete highlight",
                      command=self._delete_selected_highlight)
        try:
            m.tk_popup(event.x_root, event.y_root)
        finally:
            m.grab_release()

    def _add_selected_highlight_to_study_notes(self) -> None:
        """Send the highlighted row's text to the Study Notes editor."""
        sel = self._highlights_listbox.curselection()
        if not sel:
            return
        rec = self._highlights_records[sel[0]]
        _id, book, _s, _e, text, _color, _ts = rec
        if not text:
            messagebox.showinfo(
                "Empty highlight",
                "This highlight has no captured text. (Older highlights "
                "may not have stored their text.)")
            return
        self.add_text_to_study_notes(
            text, source_label=self._book_short_label(book))

    # ---- Workspace tab: Topics -----------------------------------------
    def _build_tab_topics(self, parent: tk.Frame) -> None:
        head = tk.Frame(parent, bg=BG_PANEL, padx=12, pady=8)
        head.pack(fill=tk.X)
        tk.Label(head, text="📌 Topics", bg=BG_PANEL, fg=FG_TEXT,
                 font=("Segoe UI", 13, "bold")).pack(side=tk.LEFT)
        self._topics_stats_var = tk.StringVar(value="")
        tk.Label(head, textvariable=self._topics_stats_var,
                 bg=BG_PANEL, fg=FG_MUTED, font=("Segoe UI", 10)
                 ).pack(side=tk.RIGHT)

        paned = tk.PanedWindow(parent, orient=tk.HORIZONTAL, sashwidth=6,
                                bg=BG_DARK, bd=0, sashrelief=tk.FLAT)
        paned.pack(fill=tk.BOTH, expand=True, padx=12, pady=4)

        # Left — topic list
        left = tk.Frame(paned, bg=BG_DARK)
        tk.Label(left, text="Topics", bg=BG_DARK, fg=FG_MUTED,
                 font=("Segoe UI", 11, "bold"), anchor=tk.W
                 ).pack(fill=tk.X, padx=2, pady=(0, 4))
        self._topics_listbox = tk.Listbox(
            left, bg=BG_INPUT, fg=FG_TEXT,
            selectbackground=ACCENT_CYAN, selectforeground="white",
            font=("Segoe UI", 11), relief=tk.FLAT, bd=0,
            highlightthickness=0, activestyle="none",
        )
        self._topics_listbox.pack(fill=tk.BOTH, expand=True)
        self._topics_listbox.bind("<<ListboxSelect>>",
            lambda _e: self._show_topic_entries())
        ltbtn = tk.Frame(left, bg=BG_DARK, pady=6)
        ltbtn.pack(fill=tk.X)
        def lb_btn(text, cmd, color):
            return tk.Button(ltbtn, text=text, command=cmd,
                             font=("Segoe UI", 10, "bold"),
                             bg=color, fg="white", activebackground=color,
                             relief=tk.FLAT, padx=10, pady=4,
                             cursor="hand2", borderwidth=0)
        lb_btn("+ New",  self._create_new_topic,      ACCENT_GREEN).pack(side=tk.LEFT, padx=(0,4))
        lb_btn("Rename", self._rename_selected_topic, ACCENT_CYAN).pack(side=tk.LEFT, padx=4)
        lb_btn("Delete", self._delete_selected_topic, ACCENT_RED).pack(side=tk.LEFT, padx=4)

        # Right — entries in selected topic
        right = tk.Frame(paned, bg=BG_DARK)
        self._topic_entries_label_var = tk.StringVar(value="Entries")
        tk.Label(right, textvariable=self._topic_entries_label_var,
                 bg=BG_DARK, fg=FG_MUTED, font=("Segoe UI", 11, "bold"),
                 anchor=tk.W).pack(fill=tk.X, padx=2, pady=(0,4))
        entry_frame = tk.Frame(right, bg=BG_DARK)
        entry_frame.pack(fill=tk.BOTH, expand=True)
        self._topic_entries_listbox = tk.Listbox(
            entry_frame, bg=BG_INPUT, fg=FG_TEXT,
            selectbackground=ACCENT_CYAN, selectforeground="white",
            font=("Segoe UI", 11), relief=tk.FLAT, bd=0,
            highlightthickness=0, activestyle="none",
        )
        sb = tk.Scrollbar(entry_frame, command=self._topic_entries_listbox.yview)
        self._topic_entries_listbox.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self._topic_entries_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._topic_entries_listbox.bind("<Double-Button-1>",
            lambda _e: self._view_or_jump_topic_entry())
        self._topic_entries_listbox.bind("<Return>",
            lambda _e: self._view_or_jump_topic_entry())
        rtbtn = tk.Frame(right, bg=BG_DARK, pady=6)
        rtbtn.pack(fill=tk.X)
        def rb(text, cmd, color):
            return tk.Button(rtbtn, text=text, command=cmd,
                             font=("Segoe UI", 10, "bold"),
                             bg=color, fg="white", activebackground=color,
                             relief=tk.FLAT, padx=10, pady=4,
                             cursor="hand2", borderwidth=0)
        rb("View / Jump", self._view_or_jump_topic_entry, ACCENT_CYAN).pack(side=tk.LEFT, padx=(0, 4))
        rb("Copy text",   self._copy_topic_entry_text,    ACCENT_SLATE).pack(side=tk.LEFT, padx=4)
        rb("Delete entry", self._delete_topic_entry,      ACCENT_RED).pack(side=tk.LEFT, padx=4)

        paned.add(left,  minsize=200, stretch="always")
        paned.add(right, minsize=320, stretch="always")

    def _refresh_tab_topics(self) -> None:
        if not hasattr(self, "_topics_listbox"):
            return
        rows = self._db_query(
            "SELECT t.id, t.title, COUNT(e.id) "
            "FROM topics t LEFT JOIN topic_entries e ON e.topic_id = t.id "
            "GROUP BY t.id ORDER BY t.title COLLATE NOCASE")
        self._topics_records = rows
        self._topics_listbox.delete(0, tk.END)
        for _id, title, n in rows:
            self._topics_listbox.insert(tk.END, f" {title}  ({n})")
        self._topics_stats_var.set(
            f"{len(rows)} topic{'s' if len(rows) != 1 else ''}")
        self._topic_entries_listbox.delete(0, tk.END)
        self._topic_entries_records = []
        self._topic_entries_label_var.set("Entries")

    def _show_topic_entries(self) -> None:
        sel = self._topics_listbox.curselection()
        if not sel:
            return
        tid, title, _n = self._topics_records[sel[0]]
        rows = self._db_query(
            "SELECT id, text, source_book, source_offset, created_at "
            "FROM topic_entries WHERE topic_id=? ORDER BY created_at DESC",
            (tid,))
        self._topic_entries_records = rows
        self._topic_entries_listbox.delete(0, tk.END)
        for _id, text, book, _off, _ts in rows:
            snippet = " ".join((text or "").split())[:90]
            src = f"  ({self._book_short_label(book)})" if book else ""
            self._topic_entries_listbox.insert(tk.END, f" {snippet}{src}")
        self._topic_entries_label_var.set(f"Entries in '{title}'")

    def _create_new_topic(self) -> None:
        name = self._prompt_for_text("New topic", "Topic name:")
        if not name:
            return
        name = name.strip()
        if not name:
            return
        try:
            self._db_exec(
                "INSERT INTO topics (title, created_at) VALUES (?, ?)",
                (name, datetime.now().isoformat()),
            )
        except sqlite3.IntegrityError:
            messagebox.showinfo(
                "Already exists", f"A topic named '{name}' already exists.")
        self._refresh_tab_topics()

    def _rename_selected_topic(self) -> None:
        sel = self._topics_listbox.curselection()
        if not sel:
            return
        tid, title, _n = self._topics_records[sel[0]]
        new = self._prompt_for_text("Rename topic",
                                      f"New name (current: {title}):")
        if not new:
            return
        new = new.strip()
        if not new or new == title:
            return
        try:
            self._db_exec("UPDATE topics SET title=? WHERE id=?", (new, tid))
        except sqlite3.IntegrityError:
            messagebox.showinfo("Name in use",
                                  f"A topic named '{new}' already exists.")
        self._refresh_tab_topics()

    def _delete_selected_topic(self) -> None:
        sel = self._topics_listbox.curselection()
        if not sel:
            return
        tid, title, n = self._topics_records[sel[0]]
        if not messagebox.askyesno(
            "Delete topic?",
            f"Permanently delete '{title}' and its {n} entries?",
        ):
            return
        self._db_exec("DELETE FROM topics WHERE id=?", (tid,))
        # Safety net in case ON DELETE CASCADE is unavailable (older SQLite).
        self._db_exec("DELETE FROM topic_entries WHERE topic_id=?", (tid,))
        self._refresh_tab_topics()

    def _view_or_jump_topic_entry(self) -> None:
        sel = self._topic_entries_listbox.curselection()
        if not sel:
            return
        _eid, text, book, offset, _ts = self._topic_entries_records[sel[0]]
        if book and offset is not None:
            self._jump_to_book_offset(book, offset)
            return
        self._show_text_popup("Topic entry", text)

    def _show_text_popup(self, title: str, body_text: str) -> None:
        dlg = tk.Toplevel(self.root)
        dlg.title(title)
        dlg.configure(bg=BG_DARK)
        dlg.geometry("520x360")
        dlg.transient(self.root)
        body = scrolledtext.ScrolledText(
            dlg, wrap=tk.WORD, font=("Segoe UI", 11),
            bg=BG_INPUT, fg=FG_TEXT, padx=14, pady=12, relief=tk.FLAT,
        )
        body.pack(fill=tk.BOTH, expand=True, padx=14, pady=14)
        body.insert("1.0", body_text)
        body.configure(state=tk.DISABLED)
        tk.Button(dlg, text="Close", command=dlg.destroy,
                  font=("Segoe UI", 11, "bold"),
                  bg=ACCENT_SLATE, fg="white", activebackground=ACCENT_SLATE,
                  relief=tk.FLAT, padx=14, pady=6, cursor="hand2",
                  borderwidth=0).pack(pady=(0, 12))

    def _copy_topic_entry_text(self) -> None:
        sel = self._topic_entries_listbox.curselection()
        if not sel:
            return
        _eid, text, _book, _off, _ts = self._topic_entries_records[sel[0]]
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.set_status("Copied entry to clipboard.")

    def _delete_topic_entry(self) -> None:
        sel = self._topic_entries_listbox.curselection()
        if not sel:
            return
        eid, _t, _b, _o, _ts = self._topic_entries_records[sel[0]]
        if not messagebox.askyesno("Delete entry?",
                                     "Remove this entry from the topic?"):
            return
        self._db_exec("DELETE FROM topic_entries WHERE id=?", (eid,))
        self._show_topic_entries()
        self._refresh_tab_topics()

    # ---- Workspace tab: Bookmarks --------------------------------------
    def _build_tab_bookmarks(self, parent: tk.Frame) -> None:
        head = tk.Frame(parent, bg=BG_PANEL, padx=12, pady=8)
        head.pack(fill=tk.X)
        tk.Label(head, text="🔖 Bookmarks", bg=BG_PANEL, fg=FG_TEXT,
                 font=("Segoe UI", 13, "bold")).pack(side=tk.LEFT)
        self._bookmarks_stats_var = tk.StringVar(value="")
        tk.Label(head, textvariable=self._bookmarks_stats_var,
                 bg=BG_PANEL, fg=FG_MUTED, font=("Segoe UI", 10)
                 ).pack(side=tk.RIGHT)

        list_frame = tk.Frame(parent, bg=BG_DARK, padx=12, pady=4)
        list_frame.pack(fill=tk.BOTH, expand=True)
        self._bookmarks_listbox = tk.Listbox(
            list_frame, bg=BG_INPUT, fg=FG_TEXT,
            selectbackground=ACCENT_CYAN, selectforeground="white",
            font=("Segoe UI", 11), relief=tk.FLAT, bd=0,
            highlightthickness=0, activestyle="none",
        )
        sb = tk.Scrollbar(list_frame, command=self._bookmarks_listbox.yview)
        self._bookmarks_listbox.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self._bookmarks_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._bookmarks_listbox.bind("<Double-Button-1>",
            lambda _e: self._jump_to_selected_bookmark())
        self._bookmarks_listbox.bind("<Return>",
            lambda _e: self._jump_to_selected_bookmark())

        row = tk.Frame(parent, bg=BG_DARK, padx=12, pady=8)
        row.pack(fill=tk.X)
        def b(text, cmd, color):
            return tk.Button(row, text=text, command=cmd,
                             font=("Segoe UI", 11, "bold"),
                             bg=color, fg="white", activebackground=color,
                             relief=tk.FLAT, padx=12, pady=6,
                             cursor="hand2", borderwidth=0)
        b("Jump to", self._jump_to_selected_bookmark, ACCENT_CYAN).pack(side=tk.LEFT)
        b("Rename",  self._rename_selected_bookmark,  ACCENT_SLATE).pack(side=tk.LEFT, padx=6)
        b("Delete",  self._delete_selected_bookmark,  ACCENT_RED).pack(side=tk.LEFT)
        b("Bookmark current spot", self.bookmark_here, ACCENT_GREEN).pack(side=tk.RIGHT)

    def _refresh_tab_bookmarks(self) -> None:
        if not hasattr(self, "_bookmarks_listbox"):
            return
        rows = self._db_query(
            "SELECT id, book, position, label, created_at "
            "FROM bookmarks ORDER BY created_at DESC")
        self._bookmarks_records = rows
        lb = self._bookmarks_listbox
        lb.delete(0, tk.END)
        for _id, book, _pos, label, _ts in rows:
            short = self._book_short_label(book)
            lb.insert(tk.END, f" {label:<60}  ({short})")
        self._bookmarks_stats_var.set(
            f"{len(rows)} bookmark{'s' if len(rows) != 1 else ''}")

    def _jump_to_selected_bookmark(self) -> None:
        sel = self._bookmarks_listbox.curselection()
        if not sel:
            return
        _id, book, pos, _label, _ts = self._bookmarks_records[sel[0]]
        self._jump_to_book_offset(book, pos)

    def _rename_selected_bookmark(self) -> None:
        sel = self._bookmarks_listbox.curselection()
        if not sel:
            return
        bid, _book, _pos, label, _ts = self._bookmarks_records[sel[0]]
        new = self._prompt_for_text("Rename bookmark",
                                      f"New label (current: {label}):")
        if not new:
            return
        new = new.strip()
        if not new:
            return
        self._db_exec("UPDATE bookmarks SET label=? WHERE id=?", (new, bid))
        self._refresh_tab_bookmarks()

    def _delete_selected_bookmark(self) -> None:
        sel = self._bookmarks_listbox.curselection()
        if not sel:
            return
        bid, _book, _pos, _label, _ts = self._bookmarks_records[sel[0]]
        if not messagebox.askyesno("Delete bookmark?",
                                     "Remove this bookmark?"):
            return
        self._db_exec("DELETE FROM bookmarks WHERE id=?", (bid,))
        self._refresh_tab_bookmarks()

    # ---- Workspace tab: Glossary ---------------------------------------
    def _build_tab_glossary(self, parent: tk.Frame) -> None:
        head = tk.Frame(parent, bg=BG_PANEL, padx=12, pady=8)
        head.pack(fill=tk.X)
        tk.Label(head, text="📒 Glossary", bg=BG_PANEL, fg=FG_TEXT,
                 font=("Segoe UI", 13, "bold")).pack(side=tk.LEFT)
        self._glossary_stats_var = tk.StringVar(value="")
        tk.Label(head, textvariable=self._glossary_stats_var,
                 bg=BG_PANEL, fg=FG_MUTED, font=("Segoe UI", 10)
                 ).pack(side=tk.RIGHT)

        search_row = tk.Frame(parent, bg=BG_DARK, padx=12, pady=6)
        search_row.pack(fill=tk.X)
        tk.Label(search_row, text="Search:", bg=BG_DARK, fg=FG_MUTED,
                 font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=(0, 6))
        self._glossary_search_var = tk.StringVar()
        e = tk.Entry(search_row, textvariable=self._glossary_search_var,
                     bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT,
                     font=("Segoe UI", 11), relief=tk.FLAT, bd=0)
        e.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)
        self._glossary_search_var.trace_add(
            "write", lambda *_: self._refresh_tab_glossary())

        paned = tk.PanedWindow(parent, orient=tk.HORIZONTAL, sashwidth=6,
                                bg=BG_DARK, bd=0, sashrelief=tk.FLAT)
        paned.pack(fill=tk.BOTH, expand=True, padx=12, pady=4)

        left = tk.Frame(paned, bg=BG_DARK)
        list_frame = tk.Frame(left, bg=BG_DARK)
        list_frame.pack(fill=tk.BOTH, expand=True)
        self._glossary_listbox = tk.Listbox(
            list_frame, bg=BG_INPUT, fg=FG_TEXT,
            selectbackground=ACCENT_CYAN, selectforeground="white",
            font=("Segoe UI", 11), relief=tk.FLAT, bd=0,
            highlightthickness=0, activestyle="none",
        )
        sb = tk.Scrollbar(list_frame, command=self._glossary_listbox.yview)
        self._glossary_listbox.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self._glossary_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._glossary_listbox.bind("<<ListboxSelect>>",
            lambda _e: self._show_glossary_selected())

        right = tk.Frame(paned, bg=BG_DARK)
        self._glossary_term_var = tk.StringVar(value="")
        tk.Label(right, textvariable=self._glossary_term_var,
                 bg=BG_DARK, fg=FG_TEXT, font=("Segoe UI", 14, "bold"),
                 anchor=tk.W).pack(fill=tk.X, padx=2)
        self._glossary_definition_widget = scrolledtext.ScrolledText(
            right, wrap=tk.WORD, font=("Segoe UI", 11),
            bg=BG_INPUT, fg=FG_TEXT, padx=12, pady=10, relief=tk.FLAT,
        )
        self._glossary_definition_widget.pack(fill=tk.BOTH, expand=True, pady=(4, 0))
        self._glossary_definition_widget.configure(state=tk.DISABLED)

        paned.add(left,  minsize=200, stretch="always")
        paned.add(right, minsize=320, stretch="always")

        row = tk.Frame(parent, bg=BG_DARK, padx=12, pady=8)
        row.pack(fill=tk.X)
        def b(text, cmd, color):
            return tk.Button(row, text=text, command=cmd,
                             font=("Segoe UI", 11, "bold"),
                             bg=color, fg="white", activebackground=color,
                             relief=tk.FLAT, padx=12, pady=6,
                             cursor="hand2", borderwidth=0)
        b("+ Add entry", lambda: self._edit_glossary_entry(),  ACCENT_GREEN).pack(side=tk.LEFT, padx=(0,4))
        b("Edit",        self._edit_glossary_selected,         ACCENT_CYAN).pack(side=tk.LEFT, padx=4)
        b("Delete",      self._delete_glossary_selected,       ACCENT_RED).pack(side=tk.LEFT, padx=4)

    def _refresh_tab_glossary(self) -> None:
        if not hasattr(self, "_glossary_listbox"):
            return
        q = (self._glossary_search_var.get()
             if hasattr(self, "_glossary_search_var") else "").strip().lower()
        if q:
            rows = self._db_query(
                "SELECT id, term, definition, source FROM glossary "
                "WHERE LOWER(term) LIKE ? OR LOWER(definition) LIKE ? "
                "ORDER BY term COLLATE NOCASE",
                (f"%{q}%", f"%{q}%"),
            )
        else:
            rows = self._db_query(
                "SELECT id, term, definition, source FROM glossary "
                "ORDER BY term COLLATE NOCASE")
        self._glossary_records = rows
        lb = self._glossary_listbox
        lb.delete(0, tk.END)
        for _id, term, _def, _src in rows:
            lb.insert(tk.END, f" {term}")
        self._glossary_stats_var.set(
            f"{len(rows)} term{'s' if len(rows) != 1 else ''}")
        # Clear the read pane when the list refreshes
        self._glossary_term_var.set("")
        w = self._glossary_definition_widget
        w.configure(state=tk.NORMAL); w.delete("1.0", tk.END)
        w.configure(state=tk.DISABLED)

    def _show_glossary_selected(self) -> None:
        sel = self._glossary_listbox.curselection()
        if not sel:
            return
        _id, term, definition, _src = self._glossary_records[sel[0]]
        self._glossary_term_var.set(term)
        w = self._glossary_definition_widget
        w.configure(state=tk.NORMAL)
        w.delete("1.0", tk.END)
        w.insert("1.0", definition)
        w.configure(state=tk.DISABLED)

    def _edit_glossary_selected(self) -> None:
        sel = self._glossary_listbox.curselection()
        if not sel:
            return
        gid, term, definition, source = self._glossary_records[sel[0]]
        self._edit_glossary_entry(
            term=term, definition=definition,
            source=source or "", existing_id=gid)

    def _delete_glossary_selected(self) -> None:
        sel = self._glossary_listbox.curselection()
        if not sel:
            return
        gid, term, _def, _src = self._glossary_records[sel[0]]
        if not messagebox.askyesno("Delete entry?",
                                     f"Delete glossary entry for '{term}'?"):
            return
        self._db_exec("DELETE FROM glossary WHERE id=?", (gid,))
        self._refresh_tab_glossary()

    # ---- Workspace tab: Journal ----------------------------------------
    def _build_tab_journal(self, parent: tk.Frame) -> None:
        head = tk.Frame(parent, bg=BG_PANEL, padx=12, pady=8)
        head.pack(fill=tk.X)
        tk.Label(head, text="📅 Journal", bg=BG_PANEL, fg=FG_TEXT,
                 font=("Segoe UI", 13, "bold")).pack(side=tk.LEFT)
        self._journal_stats_var = tk.StringVar(value="")
        tk.Label(head, textvariable=self._journal_stats_var,
                 bg=BG_PANEL, fg=FG_MUTED, font=("Segoe UI", 10)
                 ).pack(side=tk.RIGHT)

        paned = tk.PanedWindow(parent, orient=tk.HORIZONTAL, sashwidth=6,
                                bg=BG_DARK, bd=0, sashrelief=tk.FLAT)
        paned.pack(fill=tk.BOTH, expand=True, padx=12, pady=4)

        left = tk.Frame(paned, bg=BG_DARK)
        tk.Label(left, text="Entries (newest first)", bg=BG_DARK, fg=FG_MUTED,
                 font=("Segoe UI", 11, "bold"), anchor=tk.W
                 ).pack(fill=tk.X, padx=2, pady=(0, 4))
        list_frame = tk.Frame(left, bg=BG_DARK)
        list_frame.pack(fill=tk.BOTH, expand=True)
        self._journal_listbox = tk.Listbox(
            list_frame, bg=BG_INPUT, fg=FG_TEXT,
            selectbackground=ACCENT_CYAN, selectforeground="white",
            font=("Consolas", 11), relief=tk.FLAT, bd=0,
            highlightthickness=0, activestyle="none",
        )
        sb = tk.Scrollbar(list_frame, command=self._journal_listbox.yview)
        self._journal_listbox.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self._journal_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._journal_listbox.bind("<<ListboxSelect>>",
            lambda _e: self._load_selected_journal_entry())

        ltbtn = tk.Frame(left, bg=BG_DARK, pady=6)
        ltbtn.pack(fill=tk.X)
        def lb_btn(text, cmd, color):
            return tk.Button(ltbtn, text=text, command=cmd,
                             font=("Segoe UI", 10, "bold"),
                             bg=color, fg="white", activebackground=color,
                             relief=tk.FLAT, padx=10, pady=4,
                             cursor="hand2", borderwidth=0)
        lb_btn("+ Today", self._new_today_journal_entry, ACCENT_GREEN).pack(side=tk.LEFT, padx=(0, 4))
        lb_btn("Delete",  self._delete_selected_journal,  ACCENT_RED).pack(side=tk.LEFT)

        right = tk.Frame(paned, bg=BG_DARK)
        self._journal_date_var = tk.StringVar(value="")
        tk.Label(right, textvariable=self._journal_date_var,
                 bg=BG_DARK, fg=FG_TEXT, font=("Segoe UI", 14, "bold"),
                 anchor=tk.W).pack(fill=tk.X, padx=2)
        self._journal_body = scrolledtext.ScrolledText(
            right, wrap=tk.WORD, font=("Segoe UI", 12),
            bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT,
            padx=14, pady=12, relief=tk.FLAT, undo=True,
        )
        self._journal_body.pack(fill=tk.BOTH, expand=True, pady=(4, 4))
        # Right-click clipboard menu, Ctrl+A select-all, and mic focus
        # tracking — so dictation lands here when the user clicks into
        # this editor before pressing 🎤 Voice note.
        self._attach_clipboard_menu(
            self._journal_body,
            clear_cmd=self._clear_current_journal_entry,
            clear_label="Clear this entry",
        )
        rtbtn = tk.Frame(right, bg=BG_DARK, pady=4)
        rtbtn.pack(fill=tk.X)
        tk.Button(rtbtn, text="Save entry",
                  command=self._save_current_journal_entry,
                  font=("Segoe UI", 11, "bold"),
                  bg=ACCENT_GREEN, fg="white", activebackground=ACCENT_GREEN,
                  relief=tk.FLAT, padx=14, pady=6,
                  cursor="hand2", borderwidth=0).pack(side=tk.RIGHT)

        paned.add(left,  minsize=200, stretch="never")
        paned.add(right, minsize=320, stretch="always")

    def _refresh_tab_journal(self) -> None:
        if not hasattr(self, "_journal_listbox"):
            return
        rows = self._db_query(
            "SELECT id, entry_date, body FROM journal "
            "ORDER BY entry_date DESC, id DESC")
        self._journal_records = rows
        lb = self._journal_listbox
        lb.delete(0, tk.END)
        for _id, dstr, body in rows:
            preview = " ".join((body or "").split())[:36]
            lb.insert(tk.END, f" {dstr}  {preview}")
        self._journal_stats_var.set(
            f"{len(rows)} entr{'ies' if len(rows) != 1 else 'y'}")

    def _load_selected_journal_entry(self) -> None:
        sel = self._journal_listbox.curselection()
        if not sel:
            return
        jid, dstr, body = self._journal_records[sel[0]]
        self._journal_current_id = jid
        self._journal_date_var.set(dstr)
        self._journal_body.delete("1.0", tk.END)
        self._journal_body.insert("1.0", body)

    def _new_today_journal_entry(self) -> None:
        today = datetime.now().strftime("%Y-%m-%d")
        # If today already has an entry, load and focus it.
        rows = self._db_query(
            "SELECT id, entry_date, body FROM journal "
            "WHERE entry_date=? ORDER BY id DESC LIMIT 1",
            (today,))
        if rows:
            jid, dstr, body = rows[0]
            self._journal_current_id = jid
            self._journal_date_var.set(dstr)
            self._journal_body.delete("1.0", tk.END)
            self._journal_body.insert("1.0", body)
            self._journal_body.focus_set()
            return
        now = datetime.now().isoformat()
        jid = self._db_exec(
            "INSERT INTO journal (entry_date, body, created_at, updated_at) "
            "VALUES (?, ?, ?, ?)", (today, "", now, now))
        self._journal_current_id = jid
        self._journal_date_var.set(today)
        self._journal_body.delete("1.0", tk.END)
        self._journal_body.focus_set()
        self._refresh_tab_journal()

    def _save_current_journal_entry(self) -> None:
        if self._journal_current_id is None:
            messagebox.showinfo(
                "Pick or create",
                "Select an entry on the left, or click '+ Today' to start one.")
            return
        body = self._journal_body.get("1.0", tk.END).rstrip()
        self._db_exec(
            "UPDATE journal SET body=?, updated_at=? WHERE id=?",
            (body, datetime.now().isoformat(), self._journal_current_id))
        self.set_status("Journal entry saved.")
        self._refresh_tab_journal()

    def _clear_current_journal_entry(self) -> None:
        """Empty the currently-loaded entry's body and persist the change.
        Ctrl+Z still undoes within the session if the user changes their
        mind. If no entry is loaded, no-ops."""
        if self._journal_current_id is None:
            messagebox.showinfo(
                "No entry selected",
                "Click an entry on the left, or '+ Today' to start one.")
            return
        try:
            if not self._journal_body.get("1.0", tk.END).strip():
                return
        except tk.TclError:
            return
        if messagebox.askyesno(
            "Clear journal entry?",
            "Erase this entry's text?\n\n"
            "(Ctrl+Z to undo within the session.)",
        ):
            try:
                self._journal_body.delete("1.0", tk.END)
            except tk.TclError:
                return
            self._save_current_journal_entry()
            self.set_status("Journal entry cleared.")

    def _delete_selected_journal(self) -> None:
        sel = self._journal_listbox.curselection()
        if not sel:
            return
        jid, dstr, _body = self._journal_records[sel[0]]
        if not messagebox.askyesno("Delete entry?",
                                     f"Delete journal entry from {dstr}?"):
            return
        self._db_exec("DELETE FROM journal WHERE id=?", (jid,))
        if self._journal_current_id == jid:
            self._journal_current_id = None
            self._journal_date_var.set("")
            self._journal_body.delete("1.0", tk.END)
        self._refresh_tab_journal()

    # ---- Workspace tab: Workflow ---------------------------------------
    # Color-coded folders for grouping work documents (Word/Excel/PPT/
    # PDFs etc.). Each row in `workflow_folders` pairs metadata with a
    # real directory under WORKFLOW_DIR; files dropped into a folder
    # land on disk so OneDrive backs them up and you can open them in
    # their native apps (Word, Excel, PowerPoint, …) with one click.
    def _build_tab_workflow(self, parent: tk.Frame) -> None:
        head = tk.Frame(parent, bg=BG_PANEL, padx=12, pady=8)
        head.pack(fill=tk.X)
        tk.Label(head, text="🗂 Workflow", bg=BG_PANEL, fg=FG_TEXT,
                 font=("Segoe UI", 13, "bold")).pack(side=tk.LEFT)
        self._workflow_stats_var = tk.StringVar(value="")
        tk.Label(head, textvariable=self._workflow_stats_var,
                 bg=BG_PANEL, fg=FG_MUTED, font=("Segoe UI", 10)
                 ).pack(side=tk.RIGHT)

        paned = tk.PanedWindow(parent, orient=tk.HORIZONTAL, sashwidth=6,
                                bg=BG_DARK, bd=0, sashrelief=tk.FLAT)
        paned.pack(fill=tk.BOTH, expand=True, padx=12, pady=4)

        # ---- LEFT: list of folders ------------------------------------
        left = tk.Frame(paned, bg=BG_DARK)

        # Color-filter tab row. Each tab is a button: click to view only
        # folders of that color (or "All" for everything). Counts are
        # appended to each label so the user sees how many folders sit
        # in each bucket at a glance. Active tab is highlighted cyan,
        # same convention as the Study workspace's main tabs.
        filter_bar = tk.Frame(left, bg=BG_DARK)
        filter_bar.pack(fill=tk.X, pady=(0, 6))
        self._workflow_filter_buttons = {}
        for filter_key, default_label in (
            (None,     "All"),
            ("green",  "🟢 Green"),
            ("yellow", "🟡 Yellow"),
            ("red",    "🔴 Red"),
        ):
            b = tk.Button(
                filter_bar, text=default_label,
                command=lambda k=filter_key: self._set_workflow_filter(k),
                font=("Segoe UI", 10, "bold"),
                bg=BG_INPUT, fg=FG_TEXT,
                activebackground=ACCENT_SLATE, activeforeground="white",
                relief=tk.FLAT, padx=10, pady=4,
                cursor="hand2", borderwidth=0,
            )
            b.pack(side=tk.LEFT, padx=(0, 4))
            self._workflow_filter_buttons[filter_key] = b

        tk.Label(left, text="Folders",
                 bg=BG_DARK, fg=FG_MUTED, font=("Segoe UI", 11, "bold"),
                 anchor=tk.W).pack(fill=tk.X, padx=2, pady=(0, 4))
        list_frame = tk.Frame(left, bg=BG_DARK)
        list_frame.pack(fill=tk.BOTH, expand=True)
        self._workflow_folders_listbox = tk.Listbox(
            list_frame, bg=BG_INPUT, fg=FG_TEXT,
            selectbackground=ACCENT_CYAN, selectforeground="white",
            font=("Segoe UI", 11), relief=tk.FLAT, bd=0,
            highlightthickness=0, activestyle="none",
        )
        sb = tk.Scrollbar(list_frame, command=self._workflow_folders_listbox.yview)
        self._workflow_folders_listbox.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self._workflow_folders_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # Picking a folder loads its files into the right pane.
        self._workflow_folders_listbox.bind(
            "<<ListboxSelect>>",
            lambda _e: self._refresh_workflow_files_for_selected())

        ltbtn = tk.Frame(left, bg=BG_DARK, pady=6)
        ltbtn.pack(fill=tk.X)
        def lb_btn(parent, text, cmd, color):
            return tk.Button(parent, text=text, command=cmd,
                             font=("Segoe UI", 10, "bold"),
                             bg=color, fg="white", activebackground=color,
                             relief=tk.FLAT, padx=10, pady=4,
                             cursor="hand2", borderwidth=0)
        lb_btn(ltbtn, "+ New folder", self._create_new_workflow_folder,
                ACCENT_GREEN).pack(side=tk.LEFT, padx=(0, 4))
        lb_btn(ltbtn, "Edit",         self._edit_selected_workflow_folder,
                ACCENT_CYAN).pack(side=tk.LEFT, padx=4)
        lb_btn(ltbtn, "Delete",       self._delete_selected_workflow_folder,
                ACCENT_RED).pack(side=tk.LEFT, padx=4)

        # ---- RIGHT: files in selected folder ---------------------------
        right = tk.Frame(paned, bg=BG_DARK)
        self._workflow_files_label_var = tk.StringVar(value="Files")
        tk.Label(right, textvariable=self._workflow_files_label_var,
                 bg=BG_DARK, fg=FG_MUTED, font=("Segoe UI", 11, "bold"),
                 anchor=tk.W).pack(fill=tk.X, padx=2, pady=(0, 4))
        files_frame = tk.Frame(right, bg=BG_DARK)
        files_frame.pack(fill=tk.BOTH, expand=True)
        self._workflow_files_listbox = tk.Listbox(
            files_frame, bg=BG_INPUT, fg=FG_TEXT,
            selectbackground=ACCENT_CYAN, selectforeground="white",
            font=("Consolas", 11), relief=tk.FLAT, bd=0,
            highlightthickness=0, activestyle="none",
        )
        sb2 = tk.Scrollbar(files_frame, command=self._workflow_files_listbox.yview)
        self._workflow_files_listbox.configure(yscrollcommand=sb2.set)
        sb2.pack(side=tk.RIGHT, fill=tk.Y)
        self._workflow_files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # Double-click → open. For .docx/.pdf/.txt etc. that the reader
        # supports, the file loads here. Otherwise it launches in the
        # OS default app (Excel for .xlsx, PowerPoint for .pptx, etc.).
        self._workflow_files_listbox.bind(
            "<Double-Button-1>",
            lambda _e: self._open_selected_workflow_file())
        self._workflow_files_listbox.bind(
            "<Return>", lambda _e: self._open_selected_workflow_file())

        rtbtn = tk.Frame(right, bg=BG_DARK, pady=6)
        rtbtn.pack(fill=tk.X)
        lb_btn(rtbtn, "+ Add files…",  self._add_files_to_workflow_folder,
                ACCENT_GREEN).pack(side=tk.LEFT, padx=(0, 4))
        lb_btn(rtbtn, "+ Add folder…", self._add_folder_to_workflow_folder,
                ACCENT_GREEN).pack(side=tk.LEFT, padx=4)
        lb_btn(rtbtn, "Open",          self._open_selected_workflow_file,
                ACCENT_CYAN).pack(side=tk.LEFT, padx=4)
        lb_btn(rtbtn, "Remove file",   self._remove_workflow_file,
                ACCENT_RED).pack(side=tk.LEFT, padx=4)
        lb_btn(rtbtn, "📂 Open folder", self._open_workflow_folder_in_explorer,
                ACCENT_SLATE).pack(side=tk.RIGHT)

        paned.add(left,  minsize=300, stretch="always")
        paned.add(right, minsize=320, stretch="always")

    def _refresh_tab_workflow(self) -> None:
        """Reload the folder list. Honors `_workflow_filter_color` so
        only folders matching the active color tab show up. Also
        updates each filter tab's label (with current counts) and
        active-state highlighting."""
        if self._workflow_folders_listbox is None:
            return
        try:
            rows = self._db_query(
                "SELECT id, name, title, date_label, color, "
                "created_at, updated_at "
                "FROM workflow_folders ORDER BY updated_at DESC")
        except Exception:
            rows = []
        all_records = [
            {"id": r[0], "name": r[1], "title": r[2], "date_label": r[3],
             "color": r[4], "created_at": r[5], "updated_at": r[6]}
            for r in rows
        ]

        # Tally each color so filter-tab labels can show counts.
        counts = {"green": 0, "yellow": 0, "red": 0}
        for rec in all_records:
            if rec["color"] in counts:
                counts[rec["color"]] += 1
        total = len(all_records)
        tab_labels = {
            None:     f"All  ({total})",
            "green":  f"🟢 Green  ({counts['green']})",
            "yellow": f"🟡 Yellow  ({counts['yellow']})",
            "red":    f"🔴 Red  ({counts['red']})",
        }
        for key, btn in self._workflow_filter_buttons.items():
            try:
                btn.configure(text=tab_labels.get(key, ""))
                if key == self._workflow_filter_color:
                    btn.configure(bg=ACCENT_CYAN, fg="white")
                else:
                    btn.configure(bg=BG_INPUT, fg=FG_TEXT)
            except tk.TclError:
                pass

        # Apply the active color filter. _workflow_records is the
        # filtered view used by every action handler downstream — so
        # listbox indices and record indices stay in sync.
        f = self._workflow_filter_color
        self._workflow_records = (
            all_records if f is None
            else [r for r in all_records if r["color"] == f]
        )

        lb = self._workflow_folders_listbox
        lb.delete(0, tk.END)
        for rec in self._workflow_records:
            emoji = WORKFLOW_COLOR_EMOJI.get(rec["color"], "⚪")
            parts = [rec["name"]]
            if rec["title"]:
                parts.append(rec["title"])
            if rec["date_label"]:
                parts.append(f"({rec['date_label']})")
            lb.insert(tk.END, f" {emoji}  {'  —  '.join(parts)}")
        if self._workflow_stats_var is not None:
            shown = len(self._workflow_records)
            if f is None:
                self._workflow_stats_var.set(
                    f"{total} folder{'s' if total != 1 else ''}")
            else:
                self._workflow_stats_var.set(
                    f"{shown} of {total} — filtered by {f}")
        # Clear file pane (selection is gone after a list rebuild).
        if self._workflow_files_listbox is not None:
            self._workflow_files_listbox.delete(0, tk.END)
            self._workflow_files = []
            if self._workflow_files_label_var is not None:
                self._workflow_files_label_var.set("Files")

    def _set_workflow_filter(self, color: str | None) -> None:
        """Switch the active color filter and redraw."""
        self._workflow_filter_color = color
        self._refresh_tab_workflow()

    def _refresh_workflow_files_for_selected(self) -> None:
        """Show files inside the currently-selected workflow folder."""
        if self._workflow_folders_listbox is None:
            return
        sel = self._workflow_folders_listbox.curselection()
        if not sel:
            return
        rec = self._workflow_records[sel[0]]
        disk_path = self._workflow_disk_path_for(rec["name"])
        if self._workflow_files_label_var is not None:
            label = f"Files in '{rec['name']}'"
            if rec["title"]:
                label += f"  —  {rec['title']}"
            self._workflow_files_label_var.set(label)
        self._workflow_files_listbox.delete(0, tk.END)
        self._workflow_files = []
        if not os.path.isdir(disk_path):
            return
        try:
            names = sorted(os.listdir(disk_path), key=str.lower)
        except OSError:
            names = []
        for name in names:
            full = os.path.join(disk_path, name)
            if not os.path.isfile(full):
                continue
            try:
                size = os.path.getsize(full)
                size_str = self._format_size(size)
            except OSError:
                size_str = "?"
            self._workflow_files.append((name, full))
            display = name if len(name) <= 52 else name[:49] + "…"
            self._workflow_files_listbox.insert(
                tk.END, f" {display:<52} {size_str:>10}")

    @staticmethod
    def _workflow_disk_path_for(folder_name: str) -> str:
        return os.path.join(WORKFLOW_DIR, folder_name)

    @staticmethod
    def _default_browse_dir() -> str:
        """Most useful starting place for the file/folder picker. We
        try the user's OneDrive Documents, then plain Documents, then
        their home folder — first one that exists wins."""
        for candidate in (
            os.path.expanduser(r"~\OneDrive\Documents"),
            os.path.expanduser(r"~\Documents"),
            os.path.expanduser("~"),
        ):
            if os.path.isdir(candidate):
                return candidate
        return os.path.expanduser("~")

    def _open_workflow_folder_dialog(self, existing: dict | None = None,
                                       default_color: str | None = None
                                       ) -> dict | None:
        """Modal create/edit dialog. Returns the entered values as a
        dict (keys: name, title, date_label, color) or None on cancel.

        `default_color` lets callers pre-select green/yellow/red when
        creating a new folder — handy when the user is in a color
        tab and clicks + New folder (we assume they want the new
        folder to belong to that tab)."""
        dlg = tk.Toplevel(self.root)
        dlg.title("Edit workflow folder" if existing else "New workflow folder")
        dlg.configure(bg=BG_DARK)
        dlg.geometry("460x380")
        dlg.transient(self.root)
        dlg.grab_set()

        name_var  = tk.StringVar(value=existing["name"]       if existing else "")
        title_var = tk.StringVar(value=existing["title"]      if existing else "")
        date_var  = tk.StringVar(value=existing["date_label"] if existing else "")
        initial_color = (existing["color"] if existing
                         else (default_color or "green"))
        color_var = tk.StringVar(value=initial_color)

        def labeled(label_text, var, focus_first=False):
            tk.Label(dlg, text=label_text, bg=BG_DARK, fg=FG_MUTED,
                     font=("Segoe UI", 10),
                     padx=14, pady=(10, 2)).pack(anchor=tk.W)
            e = tk.Entry(dlg, textvariable=var, bg=BG_INPUT, fg=FG_TEXT,
                         insertbackground=FG_TEXT, font=("Segoe UI", 11),
                         relief=tk.FLAT, bd=0)
            e.pack(fill=tk.X, padx=14, ipady=5)
            if focus_first:
                e.focus_set()
            return e

        name_e = labeled("Name  (used as the folder on disk):",
                          name_var, focus_first=not existing)
        title_e = labeled("Title:", title_var, focus_first=bool(existing))
        labeled("Date / year  (free text, e.g. 'Q1 2026'):", date_var)

        tk.Label(dlg, text="Color:", bg=BG_DARK, fg=FG_MUTED,
                 font=("Segoe UI", 10),
                 padx=14, pady=(12, 2)).pack(anchor=tk.W)
        color_row = tk.Frame(dlg, bg=BG_DARK, padx=14)
        color_row.pack(fill=tk.X, pady=(0, 8))
        for key, label in (("green", "🟢 Green"),
                            ("yellow", "🟡 Yellow"),
                            ("red", "🔴 Red")):
            tk.Radiobutton(
                color_row, text=label,
                variable=color_var, value=key,
                bg=BG_DARK, fg=FG_TEXT, selectcolor=BG_INPUT,
                activebackground=BG_DARK, activeforeground=FG_TEXT,
                font=("Segoe UI", 11),
            ).pack(side=tk.LEFT, padx=(0, 14))

        out: dict = {"data": None}
        def commit():
            name = name_var.get().strip()
            if not name:
                messagebox.showinfo("Name required",
                                     "Enter a folder name first.", parent=dlg)
                return
            out["data"] = {
                "name": name,
                "title": title_var.get().strip(),
                "date_label": date_var.get().strip(),
                "color": color_var.get(),
            }
            dlg.destroy()

        row = tk.Frame(dlg, bg=BG_DARK, padx=14, pady=12)
        row.pack(fill=tk.X, side=tk.BOTTOM)
        tk.Button(row, text="Save", command=commit,
                  font=("Segoe UI", 11, "bold"), bg=ACCENT_GREEN, fg="white",
                  activebackground=ACCENT_GREEN, relief=tk.FLAT,
                  padx=14, pady=6, cursor="hand2", borderwidth=0,
                  ).pack(side=tk.RIGHT, padx=(6, 0))
        tk.Button(row, text="Cancel", command=dlg.destroy,
                  font=("Segoe UI", 11, "bold"), bg=ACCENT_SLATE, fg="white",
                  activebackground=ACCENT_SLATE, relief=tk.FLAT,
                  padx=14, pady=6, cursor="hand2", borderwidth=0,
                  ).pack(side=tk.RIGHT)
        name_e.bind("<Return>", lambda _e: commit())
        title_e.bind("<Return>", lambda _e: commit())
        dlg.wait_window()
        return out["data"]

    @staticmethod
    def _sanitize_dirname(name: str) -> str:
        """Strip characters Windows hates from a folder name."""
        bad = set('<>:"/\\|?*')
        cleaned = "".join("_" if c in bad else c for c in name).strip(" .")
        return cleaned or "Folder"

    def _create_new_workflow_folder(self) -> None:
        # If a color tab is active, pre-fill the dialog with that color
        # so "I'm in the Yellow tab and want a new Yellow folder" is one
        # click instead of three.
        preset = (self._workflow_filter_color
                  if self._workflow_filter_color in ("green", "yellow", "red")
                  else None)
        data = self._open_workflow_folder_dialog(default_color=preset)
        if data is None:
            return
        # Make sure the on-disk folder name is safe for Windows.
        safe_name = self._sanitize_dirname(data["name"])
        try:
            os.makedirs(WORKFLOW_DIR, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Workflow folder unavailable", str(e))
            return
        # Pick a non-colliding disk path.
        disk_path = self._workflow_disk_path_for(safe_name)
        unique_name = safe_name
        n = 1
        while os.path.exists(disk_path):
            unique_name = f"{safe_name} ({n})"
            disk_path = self._workflow_disk_path_for(unique_name)
            n += 1
        try:
            os.makedirs(disk_path, exist_ok=False)
        except Exception as e:
            messagebox.showerror("Could not create folder", str(e))
            return
        now = datetime.now().isoformat()
        try:
            self._db_exec(
                "INSERT INTO workflow_folders "
                "(name, title, date_label, color, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (unique_name, data["title"], data["date_label"],
                 data["color"], now, now),
            )
        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Name in use",
                f"A workflow folder named '{unique_name}' already exists.")
            try:
                os.rmdir(disk_path)
            except Exception:
                pass
            return
        self._refresh_tab_workflow()
        self.set_status(f"🗂 Created workflow folder: {unique_name}")

    def _edit_selected_workflow_folder(self) -> None:
        sel = self._workflow_folders_listbox.curselection()
        if not sel:
            messagebox.showinfo("Nothing selected",
                                 "Pick a folder to edit.")
            return
        rec = self._workflow_records[sel[0]]
        data = self._open_workflow_folder_dialog(rec)
        if data is None:
            return
        new_safe = self._sanitize_dirname(data["name"])
        old_disk = self._workflow_disk_path_for(rec["name"])
        new_disk = self._workflow_disk_path_for(new_safe)
        if new_safe.lower() != rec["name"].lower() and os.path.exists(new_disk):
            messagebox.showerror(
                "Name in use",
                f"A folder named '{new_safe}' already exists on disk.")
            return
        if new_safe != rec["name"]:
            try:
                if os.path.exists(old_disk):
                    os.rename(old_disk, new_disk)
            except Exception as e:
                messagebox.showerror("Could not rename folder", str(e))
                return
        try:
            self._db_exec(
                "UPDATE workflow_folders "
                "SET name=?, title=?, date_label=?, color=?, updated_at=? "
                "WHERE id=?",
                (new_safe, data["title"], data["date_label"], data["color"],
                 datetime.now().isoformat(), rec["id"]),
            )
        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Name in use",
                f"A workflow folder named '{new_safe}' already exists.")
            return
        self._refresh_tab_workflow()

    def _delete_selected_workflow_folder(self) -> None:
        sel = self._workflow_folders_listbox.curselection()
        if not sel:
            messagebox.showinfo("Nothing selected",
                                 "Pick a folder to delete.")
            return
        rec = self._workflow_records[sel[0]]
        if not messagebox.askyesno(
            "Delete workflow folder?",
            f"Permanently delete '{rec['name']}' AND all files inside?\n\n"
            "This removes the folder and its contents from disk. "
            "It cannot be undone.",
        ):
            return
        disk_path = self._workflow_disk_path_for(rec["name"])
        try:
            if os.path.isdir(disk_path):
                shutil.rmtree(disk_path)
        except Exception as e:
            messagebox.showerror("Could not remove folder", str(e))
            return
        try:
            self._db_exec("DELETE FROM workflow_folders WHERE id=?",
                          (rec["id"],))
        except Exception as e:
            messagebox.showerror("Database error", str(e))
        self._refresh_tab_workflow()

    def _add_files_to_workflow_folder(self) -> None:
        if self._workflow_folders_listbox is None:
            return
        sel = self._workflow_folders_listbox.curselection()
        if not sel:
            messagebox.showinfo(
                "No folder selected",
                "Pick a workflow folder on the left first, then "
                "click + Add files…")
            return
        rec = self._workflow_records[sel[0]]
        paths = filedialog.askopenfilenames(
            title=f"Add files to '{rec['name']}'",
            # Documents is where Office files usually live — opening
            # the dialog there saves the user a few clicks.
            initialdir=self._default_browse_dir(),
            filetypes=[
                ("Microsoft 365", WORKFLOW_OFFICE_GLOB),
                ("PDF",            "*.pdf"),
                ("Text / Markdown", "*.txt *.md *.rtf *.csv *.tsv"),
                ("Images",         "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("All files",      "*.*"),
            ],
        )
        if not paths:
            return
        disk_path = self._workflow_disk_path_for(rec["name"])
        try:
            os.makedirs(disk_path, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Folder unavailable", str(e))
            return
        added = 0
        skipped: list[str] = []
        for src in paths:
            dest = os.path.join(disk_path, os.path.basename(src))
            b_root, b_ext = os.path.splitext(dest)
            n = 1
            while os.path.exists(dest):
                dest = f"{b_root} ({n}){b_ext}"
                n += 1
            try:
                shutil.copy2(src, dest)
                added += 1
            except Exception as e:
                skipped.append(f"{os.path.basename(src)} ({e})")
        # Touch updated_at so the folder floats to the top of the list.
        try:
            self._db_exec(
                "UPDATE workflow_folders SET updated_at=? WHERE id=?",
                (datetime.now().isoformat(), rec["id"]),
            )
        except Exception:
            pass
        self._refresh_workflow_files_for_selected()
        msg = f"Added {added} file{'s' if added != 1 else ''} "
        msg += f"to '{rec['name']}'."
        if skipped:
            msg += "\n\nSkipped:\n  • " + "\n  • ".join(skipped[:12])
        messagebox.showinfo("Files added", msg)

    def _add_folder_to_workflow_folder(self) -> None:
        """Pick a folder anywhere on disk and bulk-import its top-level
        files into the selected workflow folder. Only files matching
        WORKFLOW_IMPORT_EXTS are copied; subfolders are skipped so the
        user doesn't accidentally pull in a giant tree."""
        if self._workflow_folders_listbox is None:
            return
        sel = self._workflow_folders_listbox.curselection()
        if not sel:
            messagebox.showinfo(
                "No folder selected",
                "Pick a workflow folder on the left first, then click "
                "+ Add folder…")
            return
        rec = self._workflow_records[sel[0]]
        src_dir = filedialog.askdirectory(
            title=f"Pick a folder to import into '{rec['name']}'",
            initialdir=self._default_browse_dir(),
            mustexist=True,
        )
        if not src_dir:
            return
        # Scan top-level files only.
        try:
            entries = sorted(os.listdir(src_dir), key=str.lower)
        except OSError as e:
            messagebox.showerror("Could not read folder", str(e))
            return
        eligible: list[str] = []
        for name in entries:
            full = os.path.join(src_dir, name)
            if not os.path.isfile(full):
                continue
            if name.lower().endswith(WORKFLOW_IMPORT_EXTS):
                eligible.append(full)
        if not eligible:
            ext_summary = ", ".join(sorted(set(WORKFLOW_IMPORT_EXTS)))
            messagebox.showinfo(
                "Nothing to import",
                f"No importable files found in:\n{src_dir}\n\n"
                "(Only top-level files are imported; subfolders are "
                "skipped. Looked for these extensions:\n"
                f"{ext_summary})",
            )
            return
        if not messagebox.askyesno(
            "Import folder contents?",
            f"Found {len(eligible)} file"
            f"{'s' if len(eligible) != 1 else ''} in:\n\n{src_dir}\n\n"
            f"Copy them into '{rec['name']}'?\n\n"
            "(Originals stay where they are — this is a copy.)",
        ):
            return
        # Copy.
        disk_path = self._workflow_disk_path_for(rec["name"])
        try:
            os.makedirs(disk_path, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Folder unavailable", str(e))
            return
        added = 0
        skipped: list[str] = []
        for src in eligible:
            dest = os.path.join(disk_path, os.path.basename(src))
            b_root, b_ext = os.path.splitext(dest)
            n = 1
            while os.path.exists(dest):
                dest = f"{b_root} ({n}){b_ext}"
                n += 1
            try:
                shutil.copy2(src, dest)
                added += 1
            except Exception as e:
                skipped.append(f"{os.path.basename(src)} ({e})")
        # Bump updated_at so this folder floats to the top.
        try:
            self._db_exec(
                "UPDATE workflow_folders SET updated_at=? WHERE id=?",
                (datetime.now().isoformat(), rec["id"]),
            )
        except Exception:
            pass
        self._refresh_workflow_files_for_selected()
        msg = (f"Imported {added} file{'s' if added != 1 else ''} "
               f"from:\n{src_dir}\n\ninto '{rec['name']}'.")
        if skipped:
            msg += "\n\nSkipped:\n  • " + "\n  • ".join(skipped[:12])
        messagebox.showinfo("Folder imported", msg)

    def _open_selected_workflow_file(self) -> None:
        sel = self._workflow_files_listbox.curselection()
        if not sel:
            return
        name, full = self._workflow_files[sel[0]]
        ext = os.path.splitext(name)[1].lower()
        if ext in SUPPORTED_EXTS:
            # Reader knows this format — load it into the main window.
            self._load_book(full)
            self.set_status(f"Opened in reader: {name}")
        else:
            # Hand off to the OS default app (Word, Excel, PowerPoint, …).
            try:
                os.startfile(full)  # type: ignore[attr-defined]
                self.set_status(f"Launched in default app: {name}")
            except Exception as e:
                messagebox.showerror("Could not open file", str(e))

    def _remove_workflow_file(self) -> None:
        sel = self._workflow_files_listbox.curselection()
        if not sel:
            messagebox.showinfo("Nothing selected",
                                 "Pick a file to remove.")
            return
        name, full = self._workflow_files[sel[0]]
        if not messagebox.askyesno(
            "Remove file?",
            f"Permanently delete this file from the workflow folder?\n\n"
            f"{name}\n\nThis cannot be undone.",
        ):
            return
        try:
            os.unlink(full)
        except Exception as e:
            messagebox.showerror("Could not remove", str(e))
            return
        self._refresh_workflow_files_for_selected()

    def _open_workflow_folder_in_explorer(self) -> None:
        """Open the currently-selected folder in Explorer — or the
        parent WORKFLOW_DIR if no folder is picked yet."""
        sel = self._workflow_folders_listbox.curselection()
        try:
            os.makedirs(WORKFLOW_DIR, exist_ok=True)
        except Exception:
            pass
        if not sel:
            target = WORKFLOW_DIR
        else:
            rec = self._workflow_records[sel[0]]
            target = self._workflow_disk_path_for(rec["name"])
            try:
                os.makedirs(target, exist_ok=True)
            except Exception:
                pass
        try:
            os.startfile(target)  # type: ignore[attr-defined]
        except Exception as e:
            messagebox.showerror("Could not open folder", str(e))

    # ---- Workspace tab: Study Notes ------------------------------------
    # Single freeform autosaving notepad scoped to the Study workspace.
    # The Notes panel on the main window stays separate (book-side
    # working notes); Study Notes is for collected excerpts, summaries,
    # and dictation done from the Study workspace itself. Highlights can
    # be sent here directly via the right-click menu in the Highlights tab.
    def _build_tab_study_notes(self, parent: tk.Frame) -> None:
        head = tk.Frame(parent, bg=BG_PANEL, padx=12, pady=8)
        head.pack(fill=tk.X)
        tk.Label(head, text="📝 Study Notes", bg=BG_PANEL, fg=FG_TEXT,
                 font=("Segoe UI", 13, "bold")).pack(side=tk.LEFT)
        tk.Label(head,
                 text="Autosaves. Right-click a highlight to add it here.",
                 bg=BG_PANEL, fg=FG_MUTED,
                 font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(12, 0))
        tk.Button(
            head, text="💾 Save now", command=self._save_study_notes,
            font=("Segoe UI", 10), bg=ACCENT_GREEN, fg="white",
            activebackground=ACCENT_GREEN, relief=tk.FLAT,
            padx=10, pady=4, cursor="hand2", borderwidth=0,
        ).pack(side=tk.RIGHT)
        tk.Button(
            head, text="Clear", command=self._clear_study_notes,
            font=("Segoe UI", 10), bg=ACCENT_SLATE, fg="white",
            activebackground=ACCENT_SLATE, relief=tk.FLAT,
            padx=10, pady=4, cursor="hand2", borderwidth=0,
        ).pack(side=tk.RIGHT, padx=4)

        body_frame = tk.Frame(parent, bg=BG_DARK, padx=8, pady=8)
        body_frame.pack(fill=tk.BOTH, expand=True)
        editor = scrolledtext.ScrolledText(
            body_frame, wrap=tk.WORD,
            font=(self.font_family, 12),
            bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT,
            padx=14, pady=12, relief=tk.FLAT,
            selectbackground="#1d4ed8", selectforeground="white",
            undo=True, autoseparators=True, maxundo=-1,
        )
        editor.pack(fill=tk.BOTH, expand=True)
        editor.bind("<<Modified>>",
                     lambda _e: self._on_study_notes_modified())
        # Same affordances as Reader and Notes: clipboard menu, Ctrl+A,
        # mic focus tracking — wired by the shared helper.
        self._attach_clipboard_menu(
            editor,
            clear_cmd=self._clear_study_notes,
            clear_label="Clear study notes",
        )
        self._study_notes_widget = editor

    def _refresh_tab_study_notes(self) -> None:
        """Load study_notes body from the DB into the editor."""
        w = self._study_notes_widget
        if w is None:
            return
        try:
            rows = self._db_query(
                "SELECT body FROM study_notes WHERE id = 1")
        except Exception:
            rows = []
        body = rows[0][0] if rows else ""
        try:
            w.delete("1.0", tk.END)
            if body:
                w.insert("1.0", body)
            w.edit_modified(False)
        except tk.TclError:
            pass

    def _on_study_notes_modified(self) -> None:
        """Debounced autosave on every edit — same 1.5 s timer the
        Notes panel and Matrix quadrants use."""
        w = self._study_notes_widget
        if w is None:
            return
        try:
            if not w.edit_modified():
                return
            w.edit_modified(False)
        except tk.TclError:
            return
        if self._study_notes_save_after_id is not None:
            try:
                self.root.after_cancel(self._study_notes_save_after_id)
            except Exception:
                pass
        self._study_notes_save_after_id = self.root.after(
            1500, self._save_study_notes)

    def _save_study_notes(self) -> None:
        """Write the editor's contents to the single study_notes row."""
        w = self._study_notes_widget
        if w is None:
            return
        try:
            body = w.get("1.0", tk.END).rstrip()
        except tk.TclError:
            return
        try:
            self._db_exec(
                "INSERT OR REPLACE INTO study_notes (id, body, updated_at) "
                "VALUES (1, ?, ?)",
                (body, datetime.now().isoformat()),
            )
            self._study_notes_save_after_id = None
            self.set_status("📝 Study notes saved.")
        except Exception as e:
            self.set_status(f"📝 Study notes save failed: {e}")

    def _clear_study_notes(self) -> None:
        w = self._study_notes_widget
        if w is None:
            return
        try:
            if not w.get("1.0", tk.END).strip():
                return
        except tk.TclError:
            return
        if messagebox.askyesno(
            "Clear study notes?",
            "Erase all study notes?\n\n"
            "(Ctrl+Z to undo within the session.)",
        ):
            try:
                w.delete("1.0", tk.END)
            except tk.TclError:
                return
            self._save_study_notes()
            self.set_status("📝 Study notes cleared.")

    def add_text_to_study_notes(self, text: str,
                                  source_label: str = "") -> bool:
        """Append `text` to the study_notes body, with an optional
        source citation. Returns True on success, False on failure —
        the caller uses the return value to decide whether to clear
        the source widget (for MOVE semantics)."""
        if not text or not text.strip():
            return False
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        if source_label:
            chunk = f"\n> From {source_label}  —  {timestamp}\n{text.strip()}\n"
        else:
            chunk = f"\n—  {timestamp}\n{text.strip()}\n"
        try:
            rows = self._db_query(
                "SELECT body FROM study_notes WHERE id = 1")
        except Exception:
            rows = []
        current = rows[0][0] if rows else ""
        new_body = (current.rstrip() + chunk) if current.strip() else chunk.lstrip()
        try:
            self._db_exec(
                "INSERT OR REPLACE INTO study_notes (id, body, updated_at) "
                "VALUES (1, ?, ?)",
                (new_body, datetime.now().isoformat()),
            )
        except Exception as e:
            messagebox.showerror("Could not save to Study Notes", str(e))
            return False
        w = self._study_notes_widget
        if w is not None:
            try:
                w.delete("1.0", tk.END)
                w.insert("1.0", new_body)
                w.edit_modified(False)
                w.see(tk.END)
            except tk.TclError:
                pass
        self.set_status("📝 Moved to Study Notes.")
        return True

    def _capture_widget_text(self, widget):
        """Helper used by every move-to-X method. Returns
        (text, selection_range, used_whole_buffer) — the caller uses
        these to delete exactly what was moved if the source is one
        of the editable note panes."""
        selection_range = None
        text = ""
        try:
            sel_first = widget.index(tk.SEL_FIRST)
            sel_last = widget.index(tk.SEL_LAST)
            candidate = widget.get(sel_first, sel_last).strip()
            if candidate:
                text = candidate
                selection_range = (sel_first, sel_last)
        except tk.TclError:
            pass
        used_whole_buffer = False
        if not text:
            is_note_pane = (
                widget is self.notes_area
                or widget is getattr(self, "_study_notes_widget", None)
            )
            if is_note_pane:
                text = widget.get("1.0", tk.END).strip()
                used_whole_buffer = True
        return text, selection_range, used_whole_buffer

    def _clear_moved_source(self, widget, selection_range, used_whole_buffer):
        """After a successful MOVE from Notes / Study Notes, delete the
        text that was sent so the user has a clean slate for the next
        note. The Reader (text_area) is never cleared — books are
        precious. Returns True if anything was deleted."""
        is_movable = (
            widget is self.notes_area
            or widget is getattr(self, "_study_notes_widget", None)
        )
        if not is_movable:
            return False
        try:
            if selection_range is not None:
                widget.delete(selection_range[0], selection_range[1])
                return True
            if used_whole_buffer:
                widget.delete("1.0", tk.END)
                return True
        except tk.TclError:
            pass
        return False

    def _source_label_for(self, widget) -> str:
        """Friendly citation label for whichever pane the text came from."""
        if widget is self.text_area:
            return (self._book_short_label(
                        self._book_key(self.current_file))
                    if self.current_file else "Reader")
        if widget is self.notes_area:
            return "Notes"
        if widget is getattr(self, "_study_notes_widget", None):
            return "Study Notes"
        return ""

    def add_selection_to_study_notes(self, source_widget=None) -> None:
        """MOVE selection (or full Notes/Study-Notes buffer if nothing
        is selected) into the Study Notes editor. The source is cleared
        on success when it's one of the editable note panes."""
        widget = source_widget if source_widget is not None else self.text_area
        text, sel_range, used_whole = self._capture_widget_text(widget)
        if not text:
            if widget is self.text_area:
                messagebox.showinfo(
                    "Nothing selected",
                    "Highlight some text in the reader first, then choose "
                    "📝 Add to Study Notes.")
            else:
                messagebox.showinfo("Nothing to send",
                                     "There's no text in the panel to send.")
            return
        source = self._source_label_for(widget)
        if self.add_text_to_study_notes(text, source_label=source):
            self._clear_moved_source(widget, sel_range, used_whole)

    # ---- Move a note to today's Journal entry ---------------------------
    def add_selection_to_journal_today(self, source_widget=None) -> None:
        """Append the selection (or full Notes/Study-Notes buffer) to
        today's Journal entry, creating the entry if it doesn't exist.
        MOVE semantics — source is cleared on success."""
        widget = source_widget if source_widget is not None else self.text_area
        text, sel_range, used_whole = self._capture_widget_text(widget)
        if not text:
            if widget is self.text_area:
                messagebox.showinfo(
                    "Nothing selected",
                    "Highlight some text first, then choose "
                    "📅 Add to today's Journal.")
            else:
                messagebox.showinfo("Nothing to send",
                                     "There's no text in the panel to send.")
            return
        source_label = self._source_label_for(widget)
        today_str = datetime.now().strftime("%Y-%m-%d")
        now_iso = datetime.now().isoformat()
        ts = datetime.now().strftime("%H:%M")
        # Compose the appended chunk so the user can tell entries apart.
        if source_label:
            chunk = f"\n— {ts}  (from {source_label})\n{text.strip()}\n"
        else:
            chunk = f"\n— {ts}\n{text.strip()}\n"
        try:
            rows = self._db_query(
                "SELECT id, body FROM journal WHERE entry_date = ? "
                "ORDER BY id DESC LIMIT 1", (today_str,))
        except Exception as e:
            messagebox.showerror("Database error", str(e))
            return
        try:
            if rows:
                jid, body = rows[0]
                new_body = (body.rstrip() + chunk) if (body and body.strip()) \
                            else chunk.lstrip()
                self._db_exec(
                    "UPDATE journal SET body=?, updated_at=? WHERE id=?",
                    (new_body, now_iso, jid))
            else:
                new_body = chunk.lstrip()
                self._db_exec(
                    "INSERT INTO journal "
                    "(entry_date, body, created_at, updated_at) "
                    "VALUES (?, ?, ?, ?)",
                    (today_str, new_body, now_iso, now_iso))
        except Exception as e:
            messagebox.showerror("Could not save to Journal", str(e))
            return
        # Refresh the journal tab if it's open so the addition is visible.
        try:
            self._refresh_tab_journal()
        except Exception:
            pass
        self._clear_moved_source(widget, sel_range, used_whole)
        self.set_status(f"📅 Moved to Journal — {today_str}.")

    # ---- Move a note into the Glossary as a new term --------------------
    def add_selection_as_glossary_term(self, source_widget=None) -> None:
        """Open the glossary entry dialog with the selection pre-filled
        as the term. The user picks a definition and saves. Source is
        cleared from Notes / Study Notes on save (MOVE semantics)."""
        widget = source_widget if source_widget is not None else self.text_area
        text, sel_range, used_whole = self._capture_widget_text(widget)
        if not text:
            if widget is self.text_area:
                messagebox.showinfo(
                    "Nothing selected",
                    "Highlight a word or phrase first, then choose "
                    "📒 Add to Glossary.")
            else:
                messagebox.showinfo("Nothing to send",
                                     "There's no text in the panel to send.")
            return
        # First non-empty line becomes the term; the rest, if any,
        # becomes a definition draft.
        lines = [ln for ln in text.splitlines()]
        first = next((ln.strip() for ln in lines if ln.strip()), text.strip())
        term = first[:120]
        body_lines = []
        seen_first = False
        for ln in lines:
            if not seen_first and ln.strip():
                seen_first = True
                continue
            body_lines.append(ln)
        definition_draft = "\n".join(body_lines).strip()
        source = self._book_key(self.current_file) or "" if widget is self.text_area else ""
        # The edit dialog handles its own save; we run the clear in a
        # post-step using `after_idle` so it fires after the modal closes.
        self._edit_glossary_entry(
            term=term, definition=definition_draft, source=source)
        # The dialog is modal — by this line it's been dismissed. Check
        # whether the glossary actually has this term now; if it does,
        # the user saved → clear source. If not, they cancelled.
        try:
            rows = self._db_query(
                "SELECT 1 FROM glossary WHERE term = ? COLLATE NOCASE",
                (term,))
        except Exception:
            rows = []
        if rows:
            self._clear_moved_source(widget, sel_range, used_whole)
            self.set_status(f"📒 Moved to Glossary — '{term}'.")

    # ---- Send notes / selections to an Eisenhower Matrix quadrant -----
    # The Notes panel (and the Reader's right-click menu) offers a quick
    # path to drop the current note straight into a Matrix quadrant —
    # 🔥 Do, 🗓 Schedule, 👥 Delegate, or 🗑 Eliminate — without having
    # to open the Study workspace, navigate to the Matrix tab, and
    # retype. If the Matrix widget is currently visible (Study window
    # open on the Matrix tab), the live editor refreshes too so the
    # addition shows up immediately.
    def add_text_to_matrix_quadrant(self, quadrant_key: str,
                                     text: str,
                                     source_label: str = "") -> bool:
        """Send `text` to a Matrix quadrant.

        For 'do' and 'schedule' (the calendar half), a new Pomodoro
        block is created on the active day with the text as its title
        and a default 25-minute duration. For 'delegate' and 'eliminate'
        (the free-form half) the text is appended to the existing body
        as a bulleted entry.

        Returns True on success, False if the input was empty or the
        DB write failed. Callers use this to decide whether to clear
        the source (for the 'move' semantics on Notes / Study Notes)."""
        if not text or not text.strip():
            return False
        quadrant_key = (quadrant_key or "").lower()
        valid = {k for k, *_ in self._EISENHOWER_QUADRANTS}
        if quadrant_key not in valid:
            return False

        # ---- Calendar half — Do / Schedule ----------------------------
        if quadrant_key in ("do", "schedule"):
            # First non-empty line becomes the title; the rest, if any,
            # goes into the block's notes field.
            lines = [ln for ln in text.splitlines()]
            first_nonblank = next(
                (ln.strip() for ln in lines if ln.strip()),
                text.strip())
            title = first_nonblank[:200]
            extra = "\n".join(lines).strip()
            if extra == title:
                notes = ""
            else:
                notes = extra
            if source_label:
                notes = (notes + ("\n\n" if notes else "")
                         + f"(from {source_label})")
            dstr = (self._selected_block_date or date.today()).strftime("%Y-%m-%d")
            now_iso = datetime.now().isoformat()
            try:
                next_order = self._db_query(
                    "SELECT COALESCE(MAX(slot_order), -1) + 1 "
                    "FROM day_blocks WHERE block_date = ?",
                    (dstr,))[0][0]
                self._db_exec(
                    "INSERT INTO day_blocks "
                    "(block_date, slot_order, duration_min, title, notes, "
                    " done, is_current, created_at, updated_at) "
                    "VALUES (?, ?, ?, ?, ?, 0, 0, ?, ?)",
                    (dstr, next_order, 25, title, notes, now_iso, now_iso),
                )
            except Exception as e:
                messagebox.showerror("Could not add block", str(e))
                return False
            # Live refresh if the Matrix tab is visible.
            if self._block_listbox is not None:
                self._refresh_blocks_for_selected_day()
            short = title if len(title) <= 40 else title[:37] + "…"
            label = "🔥 Do Now" if quadrant_key == "do" else "🗓 Schedule"
            self.set_status(f"🎯 Moved to {label}: {short}")
            return True

        # ---- Free-form half — Delegate / Eliminate --------------------
        try:
            rows = self._db_query(
                "SELECT body FROM eisenhower WHERE quadrant = ?",
                (quadrant_key,))
        except Exception:
            rows = []
        current = rows[0][0] if rows else ""
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        if source_label:
            chunk = (f"\n• {text.strip()}\n"
                     f"  ({source_label} — {ts})\n")
        else:
            chunk = f"\n• {text.strip()}\n  ({ts})\n"
        new_body = (current.rstrip() + chunk) if current.strip() else chunk.lstrip()
        now_iso = datetime.now().isoformat()
        try:
            self._db_exec(
                "INSERT OR REPLACE INTO eisenhower "
                "(quadrant, body, updated_at) VALUES (?, ?, ?)",
                (quadrant_key, new_body, now_iso),
            )
        except Exception as e:
            messagebox.showerror("Could not add to Matrix", str(e))
            return False
        if self._eisenhower_widgets:
            w = self._eisenhower_widgets.get(quadrant_key)
            if w is not None:
                try:
                    w.delete("1.0", tk.END)
                    w.insert("1.0", new_body)
                    w.edit_modified(False)
                    w.see(tk.END)
                except tk.TclError:
                    pass
        label = next(
            (lbl for k, lbl, *_ in self._EISENHOWER_QUADRANTS
             if k == quadrant_key),
            quadrant_key,
        )
        self.set_status(f"🎯 Moved to Matrix → {label}.")
        return True

    def add_selection_to_matrix_quadrant(self, quadrant_key: str,
                                          source_widget=None) -> None:
        """Move the selection (or the full buffer if nothing is
        selected and the widget is one of the editable note panes) to
        the named Matrix quadrant.

        For Notes and Study Notes this is a true MOVE — once the
        Matrix accepts the text, the source range (or whole buffer)
        gets cleared so the next dictation starts on a blank slate.
        For the Reader it's a COPY — we never delete from a loaded
        book file.
        """
        widget = source_widget if source_widget is not None else self.text_area

        # Try a real selection first; remember the range so we can
        # delete exactly what we sent if this is a move.
        selection_range: tuple[str, str] | None = None
        text = ""
        try:
            sel_first = widget.index(tk.SEL_FIRST)
            sel_last = widget.index(tk.SEL_LAST)
            candidate = widget.get(sel_first, sel_last).strip()
            if candidate:
                text = candidate
                selection_range = (sel_first, sel_last)
        except tk.TclError:
            pass

        # Source attribution for the citation line.
        if widget is self.text_area:
            source = (self._book_short_label(
                        self._book_key(self.current_file))
                      if self.current_file else "Reader")
        elif widget is self.notes_area:
            source = "Notes"
        elif widget is getattr(self, "_study_notes_widget", None):
            source = "Study Notes"
        else:
            source = ""

        # Fallback: for Notes / Study Notes, grab the whole buffer when
        # nothing's selected. That's the "I dictated a note, hit the
        # Matrix button — send it all" workflow.
        used_whole_buffer = False
        if not text:
            if (widget is self.notes_area
                    or widget is getattr(self, "_study_notes_widget", None)):
                text = widget.get("1.0", tk.END).strip()
                used_whole_buffer = True
            else:
                messagebox.showinfo(
                    "Nothing selected",
                    "Select text in the reader first, then choose "
                    "🎯 Add to Matrix.")
                return
        if not text:
            messagebox.showinfo("Nothing to add",
                                "There's no text to send to the Matrix.")
            return

        ok = self.add_text_to_matrix_quadrant(
            quadrant_key, text, source_label=source)
        if not ok:
            return

        # MOVE semantics: clear the source so the panel is ready for
        # the next note. Only applies to the editable note panes — the
        # Reader keeps its content intact.
        is_movable_source = (
            widget is self.notes_area
            or widget is getattr(self, "_study_notes_widget", None)
        )
        if is_movable_source:
            try:
                if selection_range is not None:
                    widget.delete(selection_range[0], selection_range[1])
                elif used_whole_buffer:
                    widget.delete("1.0", tk.END)
            except tk.TclError:
                pass
            # The autosave bindings on Notes / Study Notes pick up the
            # deletion via <<Modified>> and flush the change to disk.

    # ---- Workspace tab: Eisenhower Matrix ------------------------------
    # A 2×2 notepad organized by Eisenhower's Urgency × Importance grid.
    # Each cell is its own autosaving editor backed by the `eisenhower`
    # table (one row per quadrant). Edits debounce-save after 1.5 s, and
    # closing the Study window force-saves any pending changes.
    _EISENHOWER_QUADRANTS = [
        # (key, label, subtitle, accent_color, grid_row, grid_col)
        ("do",        "🔥 Do",         "Urgent  &  Important",   "ACCENT_RED",   0, 0),
        ("schedule",  "🗓 Schedule",   "Important, Not Urgent",  "ACCENT_GREEN", 0, 1),
        ("delegate",  "👥 Delegate",   "Urgent, Not Important",  "ACCENT_AMBER", 1, 0),
        ("eliminate", "🗑 Eliminate",  "Neither",                "ACCENT_SLATE", 1, 1),
    ]

    def _build_tab_eisenhower(self, parent: tk.Frame) -> None:
        """Calendar redesign of the Matrix tab.

        Top half is a day-planner:
          • Day picker (this week's Mon–Sun, with prev/next week arrows)
          • 🔥 Do Now — the single active block + Start / Done buttons
          • 🗓 Schedule — ordered list of blocks for the selected day
            with Add/Edit/Delete/reorder/duration controls

        Bottom half stays free-form (👥 Delegate, 🗑 Eliminate) — for
        anything that doesn't fit a time slot."""
        # Reset state so a workspace reopen rebuilds cleanly.
        self._eisenhower_widgets = {}
        self._eisenhower_save_after_ids = {}
        self._block_listbox = None
        self._block_records = []
        self._do_now_block_id = None

        head = tk.Frame(parent, bg=BG_PANEL, padx=12, pady=8)
        head.pack(fill=tk.X)
        tk.Label(head, text="🎯 Matrix Calendar",
                 bg=BG_PANEL, fg=FG_TEXT,
                 font=("Segoe UI", 13, "bold")).pack(side=tk.LEFT)
        tk.Label(head,
                 text="Plan your day in 15/20/25-minute Pomodoro blocks.",
                 bg=BG_PANEL, fg=FG_MUTED,
                 font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(12, 0))
        tk.Button(
            head, text="💾 Save now", command=self._save_all_eisenhower,
            font=("Segoe UI", 10), bg=ACCENT_GREEN, fg="white",
            activebackground=ACCENT_GREEN, relief=tk.FLAT,
            padx=10, pady=4, cursor="hand2", borderwidth=0,
        ).pack(side=tk.RIGHT)

        # Day picker bar
        self._build_matrix_day_picker(parent)

        # 2×2 cell grid — top row is the calendar planner, bottom row
        # is the free-form delegate/eliminate notepads.
        grid = tk.Frame(parent, bg=BG_DARK, padx=8, pady=4)
        grid.pack(fill=tk.BOTH, expand=True)
        grid.grid_rowconfigure(0, weight=1)
        grid.grid_rowconfigure(1, weight=1)
        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)

        do_cell = tk.Frame(grid, bg=BG_DARK)
        do_cell.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        self._build_matrix_do_now_panel(do_cell)

        sched_cell = tk.Frame(grid, bg=BG_DARK)
        sched_cell.grid(row=0, column=1, sticky="nsew", padx=4, pady=4)
        self._build_matrix_schedule_panel(sched_cell)

        deleg_cell = tk.Frame(grid, bg=BG_DARK)
        deleg_cell.grid(row=1, column=0, sticky="nsew", padx=4, pady=4)
        self._build_matrix_freeform_quadrant(
            deleg_cell, "delegate", "👥 Delegate",
            "Urgent, Not Important", ACCENT_AMBER)

        elim_cell = tk.Frame(grid, bg=BG_DARK)
        elim_cell.grid(row=1, column=1, sticky="nsew", padx=4, pady=4)
        self._build_matrix_freeform_quadrant(
            elim_cell, "eliminate", "🗑 Eliminate",
            "Neither", ACCENT_SLATE)

    # ---- Day picker ----------------------------------------------------
    def _build_matrix_day_picker(self, parent: tk.Frame) -> None:
        """A Mon–Sun row of buttons for the week containing the
        currently-selected date, with prev / next-week arrows."""
        bar = tk.Frame(parent, bg=BG_PANEL, padx=12, pady=6)
        bar.pack(fill=tk.X)

        tk.Label(bar, text="📅", bg=BG_PANEL, fg=FG_TEXT,
                 font=("Segoe UI", 13)).pack(side=tk.LEFT, padx=(0, 6))
        tk.Button(bar, text="◀", command=self._matrix_prev_week,
                  font=("Segoe UI", 10, "bold"), bg=BG_INPUT, fg=FG_TEXT,
                  activebackground=ACCENT_SLATE, activeforeground="white",
                  relief=tk.FLAT, padx=8, pady=4,
                  cursor="hand2", borderwidth=0,
                  ).pack(side=tk.LEFT, padx=(0, 4))

        # 7 day buttons (created here, labels filled by refresh)
        self._day_picker_buttons = []
        for _ in range(7):
            b = tk.Button(
                bar, text="—",
                font=("Segoe UI", 10, "bold"),
                bg=BG_INPUT, fg=FG_TEXT,
                activebackground=ACCENT_SLATE, activeforeground="white",
                relief=tk.FLAT, padx=10, pady=4,
                cursor="hand2", borderwidth=0,
            )
            b.pack(side=tk.LEFT, padx=2)
            self._day_picker_buttons.append(b)

        tk.Button(bar, text="▶", command=self._matrix_next_week,
                  font=("Segoe UI", 10, "bold"), bg=BG_INPUT, fg=FG_TEXT,
                  activebackground=ACCENT_SLATE, activeforeground="white",
                  relief=tk.FLAT, padx=8, pady=4,
                  cursor="hand2", borderwidth=0,
                  ).pack(side=tk.LEFT, padx=(4, 10))

        tk.Button(bar, text="Today", command=self._matrix_jump_today,
                  font=("Segoe UI", 10, "bold"),
                  bg=ACCENT_CYAN, fg="white",
                  activebackground=ACCENT_CYAN, relief=tk.FLAT,
                  padx=10, pady=4, cursor="hand2", borderwidth=0,
                  ).pack(side=tk.LEFT)

        self._day_picker_date_var = tk.StringVar(value="")
        tk.Label(bar, textvariable=self._day_picker_date_var,
                 bg=BG_PANEL, fg=FG_MUTED,
                 font=("Segoe UI", 10)).pack(side=tk.RIGHT)

    def _refresh_day_picker(self) -> None:
        """Re-label and re-color the 7 day buttons for the week
        containing self._selected_block_date."""
        if not self._day_picker_buttons:
            return
        sel = self._selected_block_date
        monday = sel - timedelta(days=sel.weekday())
        today = date.today()
        for i, btn in enumerate(self._day_picker_buttons):
            d = monday + timedelta(days=i)
            label = d.strftime("%a\n%d")
            btn.configure(text=label,
                          command=lambda dd=d: self._matrix_select_date(dd))
            # Active = selected; outline = today.
            if d == sel:
                btn.configure(bg=ACCENT_RED, fg="white",
                               activebackground=ACCENT_RED)
            elif d == today:
                btn.configure(bg=ACCENT_CYAN, fg="white",
                               activebackground=ACCENT_CYAN)
            else:
                btn.configure(bg=BG_INPUT, fg=FG_TEXT,
                               activebackground=ACCENT_SLATE)
        if self._day_picker_date_var is not None:
            self._day_picker_date_var.set(
                "Viewing: " + sel.strftime("%A, %B %d, %Y"))

    def _matrix_select_date(self, d: date) -> None:
        self._selected_block_date = d
        self._refresh_day_picker()
        self._refresh_blocks_for_selected_day()

    def _matrix_prev_week(self) -> None:
        self._matrix_select_date(self._selected_block_date - timedelta(days=7))

    def _matrix_next_week(self) -> None:
        self._matrix_select_date(self._selected_block_date + timedelta(days=7))

    def _matrix_jump_today(self) -> None:
        self._matrix_select_date(date.today())

    # ---- Do Now panel --------------------------------------------------
    def _build_matrix_do_now_panel(self, cell: tk.Frame) -> None:
        bar = tk.Frame(cell, bg=ACCENT_RED, padx=10, pady=6)
        bar.pack(fill=tk.X)
        tk.Label(bar, text="🔥 Do Now", bg=ACCENT_RED, fg="white",
                 font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT)
        tk.Label(bar, text="Urgent  &  Important", bg=ACCENT_RED, fg="white",
                 font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(10, 0))

        body = tk.Frame(cell, bg=BG_INPUT, padx=12, pady=12)
        body.pack(fill=tk.BOTH, expand=True)

        tk.Label(body, text="Now:", bg=BG_INPUT, fg=FG_MUTED,
                 font=("Segoe UI", 10)).pack(anchor=tk.W)
        self._do_now_title_var = tk.StringVar(
            value="(No active block — pick one from Schedule →)")
        tk.Label(body, textvariable=self._do_now_title_var,
                 bg=BG_INPUT, fg=FG_TEXT, anchor=tk.W,
                 font=(self.font_family, 14, "bold"),
                 wraplength=380, justify=tk.LEFT
                 ).pack(fill=tk.X, pady=(2, 8))

        meta_row = tk.Frame(body, bg=BG_INPUT)
        meta_row.pack(fill=tk.X)
        tk.Label(meta_row, text="Duration:", bg=BG_INPUT, fg=FG_MUTED,
                 font=("Segoe UI", 10)).pack(side=tk.LEFT)
        self._do_now_duration_var = tk.StringVar(value="—")
        tk.Label(meta_row, textvariable=self._do_now_duration_var,
                 bg=BG_INPUT, fg=FG_TEXT,
                 font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT, padx=(6, 0))

        self._do_now_status_var = tk.StringVar(value="")
        tk.Label(body, textvariable=self._do_now_status_var,
                 bg=BG_INPUT, fg=FG_MUTED, anchor=tk.W,
                 font=("Segoe UI", 10)).pack(fill=tk.X, pady=(10, 0))

        # Action buttons row
        actions = tk.Frame(body, bg=BG_INPUT)
        actions.pack(fill=tk.X, pady=(14, 0))
        tk.Button(actions, text="▶  Start timer",
                  command=self._matrix_start_current_block,
                  font=("Segoe UI", 11, "bold"),
                  bg=ACCENT_GREEN, fg="white", activebackground=ACCENT_GREEN,
                  relief=tk.FLAT, padx=14, pady=6,
                  cursor="hand2", borderwidth=0,
                  ).pack(side=tk.LEFT, padx=(0, 6))
        tk.Button(actions, text="✓  Mark done",
                  command=self._matrix_mark_current_done,
                  font=("Segoe UI", 11, "bold"),
                  bg=ACCENT_CYAN, fg="white", activebackground=ACCENT_CYAN,
                  relief=tk.FLAT, padx=14, pady=6,
                  cursor="hand2", borderwidth=0,
                  ).pack(side=tk.LEFT, padx=6)
        tk.Button(actions, text="✗  Clear",
                  command=self._matrix_clear_current,
                  font=("Segoe UI", 11, "bold"),
                  bg=ACCENT_SLATE, fg="white", activebackground=ACCENT_SLATE,
                  relief=tk.FLAT, padx=14, pady=6,
                  cursor="hand2", borderwidth=0,
                  ).pack(side=tk.LEFT, padx=6)

    # ---- Schedule panel ------------------------------------------------
    def _build_matrix_schedule_panel(self, cell: tk.Frame) -> None:
        bar = tk.Frame(cell, bg=ACCENT_GREEN, padx=10, pady=6)
        bar.pack(fill=tk.X)
        tk.Label(bar, text="🗓 Schedule", bg=ACCENT_GREEN, fg="white",
                 font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT)
        tk.Label(bar, text="Important, Not Urgent — later today",
                 bg=ACCENT_GREEN, fg="white",
                 font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(10, 0))

        list_frame = tk.Frame(cell, bg=BG_DARK)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self._block_listbox = tk.Listbox(
            list_frame, bg=BG_INPUT, fg=FG_TEXT,
            selectbackground=ACCENT_CYAN, selectforeground="white",
            font=("Consolas", 11), relief=tk.FLAT, bd=0,
            highlightthickness=0, activestyle="none",
        )
        sb = tk.Scrollbar(list_frame, command=self._block_listbox.yview)
        self._block_listbox.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self._block_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # Double-click → make selected block the Do-Now.
        self._block_listbox.bind(
            "<Double-Button-1>",
            lambda _e: self._matrix_make_selected_current())
        self._block_listbox.bind(
            "<Return>",
            lambda _e: self._matrix_make_selected_current())

        # Actions row
        row = tk.Frame(cell, bg=BG_DARK, padx=4, pady=4)
        row.pack(fill=tk.X)
        def bb(text, cmd, color):
            return tk.Button(row, text=text, command=cmd,
                             font=("Segoe UI", 10, "bold"),
                             bg=color, fg="white", activebackground=color,
                             relief=tk.FLAT, padx=10, pady=4,
                             cursor="hand2", borderwidth=0)
        bb("+ Add block", self._matrix_add_block_dialog,
           ACCENT_GREEN).pack(side=tk.LEFT, padx=(0, 4))
        bb("Edit",        self._matrix_edit_block_dialog,
           ACCENT_CYAN).pack(side=tk.LEFT, padx=4)
        bb("Delete",      self._matrix_delete_block,
           ACCENT_RED).pack(side=tk.LEFT, padx=4)
        bb("↑",           self._matrix_move_block_up,
           ACCENT_SLATE).pack(side=tk.LEFT, padx=(8, 2))
        bb("↓",           self._matrix_move_block_down,
           ACCENT_SLATE).pack(side=tk.LEFT, padx=2)
        bb("→ Make Do-Now", self._matrix_make_selected_current,
           ACCENT_PURPLE).pack(side=tk.RIGHT)

    # ---- Free-form bottom quadrants (Delegate, Eliminate) -------------
    def _build_matrix_freeform_quadrant(self, cell: tk.Frame, key: str,
                                          label: str, subtitle: str,
                                          color: str) -> None:
        header_bar = tk.Frame(cell, bg=color, padx=10, pady=6)
        header_bar.pack(fill=tk.X)
        tk.Label(header_bar, text=label, bg=color, fg="white",
                 font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT)
        tk.Label(header_bar, text=subtitle, bg=color, fg="white",
                 font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(10, 0))

        editor = scrolledtext.ScrolledText(
            cell, wrap=tk.WORD,
            font=(self.font_family, 11),
            bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT,
            padx=10, pady=10, relief=tk.FLAT,
            selectbackground="#1d4ed8", selectforeground="white",
            undo=True, autoseparators=True, maxundo=-1,
        )
        editor.pack(fill=tk.BOTH, expand=True)
        editor.bind("<<Modified>>",
                     lambda _e, k=key: self._on_eisenhower_modified(k))
        self._attach_clipboard_menu(
            editor,
            clear_cmd=(lambda k=key: self._clear_eisenhower_quadrant(k)),
            clear_label=f"Clear  {label}",
        )
        self._eisenhower_widgets[key] = editor
        self._eisenhower_save_after_ids[key] = None

    # ---- Block CRUD ----------------------------------------------------
    def _refresh_blocks_for_selected_day(self) -> None:
        """Pull blocks for self._selected_block_date and rebuild both
        the schedule listbox and the Do-Now panel."""
        if self._block_listbox is None:
            return
        dstr = self._selected_block_date.strftime("%Y-%m-%d")
        try:
            rows = self._db_query(
                "SELECT id, slot_order, duration_min, title, notes, "
                "done, is_current "
                "FROM day_blocks WHERE block_date = ? "
                "ORDER BY slot_order, id",
                (dstr,))
        except Exception:
            rows = []
        self._block_records = [
            {"id": r[0], "slot_order": r[1], "duration_min": r[2],
             "title": r[3], "notes": r[4],
             "done": bool(r[5]), "is_current": bool(r[6])}
            for r in rows
        ]
        # Listbox display
        self._block_listbox.delete(0, tk.END)
        active_rec = None
        for rec in self._block_records:
            mark = "✓" if rec["done"] else ("▶" if rec["is_current"] else " ")
            title = rec["title"]
            if rec["done"]:
                title = f"{title}  (done)"
            line = f" {mark}  {rec['duration_min']:>2}m   {title}"
            self._block_listbox.insert(tk.END, line)
            if rec["is_current"]:
                active_rec = rec
        # Update Do-Now panel
        self._refresh_do_now_panel(active_rec)

    def _refresh_do_now_panel(self, rec: dict | None) -> None:
        if self._do_now_title_var is None:
            return
        if rec is None:
            self._do_now_block_id = None
            self._do_now_title_var.set(
                "(No active block — pick one from Schedule →)")
            self._do_now_duration_var.set("—")
            self._do_now_status_var.set("")
            return
        self._do_now_block_id = rec["id"]
        self._do_now_title_var.set(rec["title"])
        self._do_now_duration_var.set(f"{rec['duration_min']} minutes")
        notes = (rec.get("notes") or "").strip()
        status_bits = []
        if rec["done"]:
            status_bits.append("✓ done")
        if notes:
            status_bits.append(notes)
        self._do_now_status_var.set("   ".join(status_bits))

    def _matrix_add_block_dialog(self, existing: dict | None = None) -> None:
        """Modal for create or edit. `existing` populates fields when
        editing; pass None to create a new block."""
        dlg = tk.Toplevel(self.root)
        dlg.title("Edit block" if existing else "New block")
        dlg.configure(bg=BG_DARK)
        dlg.geometry("440x420")
        dlg.transient(self.root)
        dlg.grab_set()

        tk.Label(dlg, text="Title:", bg=BG_DARK, fg=FG_MUTED,
                 font=("Segoe UI", 10),
                 padx=14, pady=(12, 2)).pack(anchor=tk.W)
        title_var = tk.StringVar(
            value=existing["title"] if existing else "")
        title_e = tk.Entry(dlg, textvariable=title_var,
                            bg=BG_INPUT, fg=FG_TEXT,
                            insertbackground=FG_TEXT,
                            font=("Segoe UI", 12, "bold"),
                            relief=tk.FLAT, bd=0)
        title_e.pack(fill=tk.X, padx=14, ipady=5)
        title_e.focus_set()

        tk.Label(dlg, text="Duration (Pomodoro length):",
                 bg=BG_DARK, fg=FG_MUTED,
                 font=("Segoe UI", 10),
                 padx=14, pady=(12, 2)).pack(anchor=tk.W)
        duration_var = tk.StringVar(
            value=str(existing["duration_min"]) if existing else "25")
        dur_row = tk.Frame(dlg, bg=BG_DARK, padx=14)
        dur_row.pack(fill=tk.X)
        for v in ("15", "20", "25"):
            tk.Radiobutton(
                dur_row, text=f"{v} min", variable=duration_var, value=v,
                bg=BG_DARK, fg=FG_TEXT, selectcolor=BG_INPUT,
                activebackground=BG_DARK, activeforeground=FG_TEXT,
                font=("Segoe UI", 11),
            ).pack(side=tk.LEFT, padx=(0, 12))
        # Custom field for other durations
        tk.Label(dur_row, text="Custom:", bg=BG_DARK, fg=FG_MUTED,
                 font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(8, 4))
        custom_var = tk.StringVar(value="")
        custom_e = tk.Entry(dur_row, textvariable=custom_var, width=5,
                             bg=BG_INPUT, fg=FG_TEXT,
                             insertbackground=FG_TEXT,
                             font=("Segoe UI", 11),
                             relief=tk.FLAT, bd=0)
        custom_e.pack(side=tk.LEFT, ipady=3)
        tk.Label(dur_row, text="min", bg=BG_DARK, fg=FG_MUTED,
                 font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(2, 0))

        tk.Label(dlg, text="Notes (optional):", bg=BG_DARK, fg=FG_MUTED,
                 font=("Segoe UI", 10),
                 padx=14, pady=(12, 2)).pack(anchor=tk.W)
        notes_w = scrolledtext.ScrolledText(
            dlg, wrap=tk.WORD, font=("Segoe UI", 11),
            bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT,
            padx=10, pady=8, relief=tk.FLAT, undo=True, height=5,
        )
        notes_w.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 4))
        if existing and existing.get("notes"):
            notes_w.insert("1.0", existing["notes"])

        def commit() -> None:
            title = title_var.get().strip()
            if not title:
                messagebox.showinfo("Title required",
                                     "Give the block a title.", parent=dlg)
                return
            # Custom duration wins over radio if user typed one.
            cust = custom_var.get().strip()
            try:
                if cust:
                    duration = int(cust)
                else:
                    duration = int(duration_var.get())
                if duration < 1 or duration > 240:
                    raise ValueError
            except ValueError:
                messagebox.showinfo(
                    "Duration must be 1–240 minutes",
                    "Pick a preset (15/20/25) or enter a custom number.",
                    parent=dlg)
                return
            notes = notes_w.get("1.0", tk.END).rstrip()
            now_iso = datetime.now().isoformat()
            dstr = self._selected_block_date.strftime("%Y-%m-%d")
            try:
                if existing is None:
                    next_order = self._db_query(
                        "SELECT COALESCE(MAX(slot_order), -1) + 1 "
                        "FROM day_blocks WHERE block_date = ?",
                        (dstr,))[0][0]
                    self._db_exec(
                        "INSERT INTO day_blocks "
                        "(block_date, slot_order, duration_min, title, "
                        " notes, done, is_current, created_at, updated_at) "
                        "VALUES (?, ?, ?, ?, ?, 0, 0, ?, ?)",
                        (dstr, next_order, duration, title, notes,
                         now_iso, now_iso),
                    )
                else:
                    self._db_exec(
                        "UPDATE day_blocks "
                        "SET duration_min=?, title=?, notes=?, updated_at=? "
                        "WHERE id=?",
                        (duration, title, notes, now_iso, existing["id"]),
                    )
            except Exception as e:
                messagebox.showerror("Could not save block",
                                       str(e), parent=dlg)
                return
            self._refresh_blocks_for_selected_day()
            dlg.destroy()

        row = tk.Frame(dlg, bg=BG_DARK, padx=14, pady=10)
        row.pack(fill=tk.X)
        tk.Button(row, text="Save", command=commit,
                  font=("Segoe UI", 11, "bold"),
                  bg=ACCENT_GREEN, fg="white", activebackground=ACCENT_GREEN,
                  relief=tk.FLAT, padx=14, pady=6,
                  cursor="hand2", borderwidth=0,
                  ).pack(side=tk.RIGHT, padx=(6, 0))
        tk.Button(row, text="Cancel", command=dlg.destroy,
                  font=("Segoe UI", 11, "bold"),
                  bg=ACCENT_SLATE, fg="white", activebackground=ACCENT_SLATE,
                  relief=tk.FLAT, padx=14, pady=6,
                  cursor="hand2", borderwidth=0,
                  ).pack(side=tk.RIGHT)
        title_e.bind("<Return>", lambda _e: commit())
        dlg.wait_window()

    def _matrix_edit_block_dialog(self) -> None:
        sel = self._block_listbox.curselection() if self._block_listbox else ()
        if not sel:
            messagebox.showinfo("Nothing selected",
                                 "Pick a block in the Schedule first.")
            return
        self._matrix_add_block_dialog(existing=self._block_records[sel[0]])

    def _matrix_delete_block(self) -> None:
        sel = self._block_listbox.curselection() if self._block_listbox else ()
        if not sel:
            messagebox.showinfo("Nothing selected",
                                 "Pick a block to delete.")
            return
        rec = self._block_records[sel[0]]
        if not messagebox.askyesno("Delete block?",
                                     f"Remove this block?\n\n{rec['title']}"):
            return
        try:
            self._db_exec("DELETE FROM day_blocks WHERE id=?", (rec["id"],))
        except Exception as e:
            messagebox.showerror("Delete failed", str(e))
            return
        self._refresh_blocks_for_selected_day()

    def _matrix_move_block_up(self) -> None:
        self._matrix_move_block(-1)

    def _matrix_move_block_down(self) -> None:
        self._matrix_move_block(1)

    def _matrix_move_block(self, direction: int) -> None:
        sel = self._block_listbox.curselection() if self._block_listbox else ()
        if not sel:
            return
        idx = sel[0]
        new_idx = idx + direction
        if not (0 <= new_idx < len(self._block_records)):
            return
        a = self._block_records[idx]
        b = self._block_records[new_idx]
        now_iso = datetime.now().isoformat()
        # Swap slot_orders.
        try:
            self._db_exec(
                "UPDATE day_blocks SET slot_order=?, updated_at=? WHERE id=?",
                (b["slot_order"], now_iso, a["id"]))
            self._db_exec(
                "UPDATE day_blocks SET slot_order=?, updated_at=? WHERE id=?",
                (a["slot_order"], now_iso, b["id"]))
        except Exception as e:
            messagebox.showerror("Move failed", str(e))
            return
        self._refresh_blocks_for_selected_day()
        # Preserve selection on the moved row.
        try:
            self._block_listbox.selection_clear(0, tk.END)
            self._block_listbox.selection_set(new_idx)
            self._block_listbox.activate(new_idx)
        except tk.TclError:
            pass

    def _matrix_make_selected_current(self) -> None:
        """Promote the highlighted block into the Do-Now panel."""
        sel = self._block_listbox.curselection() if self._block_listbox else ()
        if not sel:
            return
        rec = self._block_records[sel[0]]
        dstr = self._selected_block_date.strftime("%Y-%m-%d")
        now_iso = datetime.now().isoformat()
        try:
            # Only one block per day can be `is_current`.
            self._db_exec(
                "UPDATE day_blocks SET is_current=0, updated_at=? "
                "WHERE block_date=? AND is_current=1",
                (now_iso, dstr))
            self._db_exec(
                "UPDATE day_blocks SET is_current=1, done=0, updated_at=? "
                "WHERE id=?",
                (now_iso, rec["id"]))
        except Exception as e:
            messagebox.showerror("Could not set Do-Now", str(e))
            return
        self._refresh_blocks_for_selected_day()

    def _matrix_start_current_block(self) -> None:
        """Begin the Pomodoro timer using the current Do-Now block's
        duration. If no block is current, gently nudge the user."""
        if self._do_now_block_id is None:
            messagebox.showinfo(
                "No active block",
                "Pick a block in the Schedule (double-click it or use "
                "→ Make Do-Now) before starting the timer.")
            return
        rec = next((r for r in self._block_records
                     if r["id"] == self._do_now_block_id), None)
        if rec is None:
            return
        # If a timer is already running, stop it first so we don't
        # accidentally double-start.
        if self._timer_running:
            self._stop_timer(announce=False)
        self._start_timer(duration_min=rec["duration_min"])

    def _matrix_mark_current_done(self) -> None:
        if self._do_now_block_id is None:
            return
        now_iso = datetime.now().isoformat()
        try:
            self._db_exec(
                "UPDATE day_blocks SET done=1, is_current=0, updated_at=? "
                "WHERE id=?",
                (now_iso, self._do_now_block_id))
        except Exception as e:
            messagebox.showerror("Could not mark done", str(e))
            return
        self._refresh_blocks_for_selected_day()

    def _matrix_clear_current(self) -> None:
        if self._do_now_block_id is None:
            return
        now_iso = datetime.now().isoformat()
        try:
            self._db_exec(
                "UPDATE day_blocks SET is_current=0, updated_at=? "
                "WHERE id=?",
                (now_iso, self._do_now_block_id))
        except Exception as e:
            messagebox.showerror("Could not clear", str(e))
            return
        self._refresh_blocks_for_selected_day()

    def _refresh_tab_matrix(self) -> None:
        """Refresh both halves: day picker + blocks for the selected
        date AND the free-form delegate/eliminate text editors.

        Named to match the tab key 'matrix' so that
        `_show_study_tab('matrix')` finds it via the
        `_refresh_tab_<key>` convention used by every other tab.
        (Without this naming match the day-picker buttons stay as
        their '—' placeholders because the refresh never runs.)"""
        # Top half — calendar
        self._refresh_day_picker()
        self._refresh_blocks_for_selected_day()
        # Bottom half — free-form quadrants
        if not self._eisenhower_widgets:
            return
        try:
            rows = self._db_query("SELECT quadrant, body FROM eisenhower")
        except Exception:
            rows = []
        by_key = {q: (b or "") for q, b in rows}
        for key, widget in self._eisenhower_widgets.items():
            try:
                widget.delete("1.0", tk.END)
                body = by_key.get(key, "")
                if body:
                    widget.insert("1.0", body)
                widget.edit_modified(False)
            except tk.TclError:
                continue

    def _on_eisenhower_modified(self, key: str) -> None:
        """Debounced autosave — 1.5 s after the last keystroke per quadrant."""
        widget = self._eisenhower_widgets.get(key)
        if widget is None:
            return
        try:
            if not widget.edit_modified():
                return
            widget.edit_modified(False)
        except tk.TclError:
            return
        prev = self._eisenhower_save_after_ids.get(key)
        if prev is not None:
            try:
                self.root.after_cancel(prev)
            except Exception:
                pass
        self._eisenhower_save_after_ids[key] = self.root.after(
            1500, lambda k=key: self._save_eisenhower_quadrant(k))

    def _save_eisenhower_quadrant(self, key: str) -> None:
        widget = self._eisenhower_widgets.get(key)
        if widget is None:
            return
        try:
            body = widget.get("1.0", tk.END).rstrip()
        except tk.TclError:
            return
        try:
            # INSERT OR REPLACE is supported by every modern SQLite and
            # gives us atomic upsert keyed on `quadrant`.
            self._db_exec(
                "INSERT OR REPLACE INTO eisenhower (quadrant, body, updated_at) "
                "VALUES (?, ?, ?)",
                (key, body, datetime.now().isoformat()),
            )
            self._eisenhower_save_after_ids[key] = None
        except Exception as e:
            self.set_status(f"🎯 Matrix save failed: {e}")

    def _save_all_eisenhower(self) -> None:
        """Force-save every quadrant immediately (used by the toolbar
        Save-now button and on window close)."""
        if not self._eisenhower_widgets:
            return
        for key in list(self._eisenhower_widgets.keys()):
            self._save_eisenhower_quadrant(key)
        self.set_status("🎯 Matrix saved.")

    def _clear_eisenhower_quadrant(self, key: str) -> None:
        """Clear a single quadrant after confirming. Ctrl+Z inside the
        editor still undoes the clear within the session, and the DB
        update writes the empty body so it sticks across reopens."""
        widget = self._eisenhower_widgets.get(key)
        if widget is None:
            return
        if not widget.get("1.0", tk.END).strip():
            return
        label = next(
            (lbl for k, lbl, *_ in self._EISENHOWER_QUADRANTS if k == key),
            key,
        )
        if messagebox.askyesno(
            "Clear quadrant?",
            f"Erase all entries in '{label}'?\n\n"
            "(Ctrl+Z to undo within the session.)",
        ):
            try:
                widget.delete("1.0", tk.END)
            except tk.TclError:
                return
            self._save_eisenhower_quadrant(key)
            self.set_status(f"🎯 Cleared {label}.")

    # ---- Save the reader's content to the Library ----------------------
    # Single 💾 Save action with two goals:
    #   1. Primary — drop a .md file into LIBRARY_DIR so the saved
    #      content shows up in 📚 Library and can be re-opened later.
    #      "Nothing gets misplaced or lost" was the user's requirement.
    #   2. Best-effort — also write the same body to EXCERPTS_DIR so the
    #      Claude cross-session memory workflow keeps working.
    # If a Library window is open, refresh it so the new file appears
    # immediately without the user needing to click 🔄 Refresh.
    def save_excerpt(self) -> None:
        # Outer guard — any uncaught error now surfaces a real dialog
        # and logs the traceback so we can diagnose silent failures.
        try:
            self._save_excerpt_inner()
        except Exception as e:
            import traceback as _tb
            try:
                log_dir = os.path.expanduser(r"~\OneDrive\Documents\BookReader")
                os.makedirs(log_dir, exist_ok=True)
                with open(os.path.join(log_dir, "startup-error.log"),
                           "a", encoding="utf-8") as _f:
                    _f.write(f"\n=== save_excerpt {datetime.now().isoformat()} ===\n")
                    _tb.print_exc(file=_f)
            except Exception:
                pass
            try:
                messagebox.showerror(
                    "Save failed",
                    f"Could not save to the Library:\n\n{e}\n\n"
                    "The traceback is in:\n"
                    "~/OneDrive/Documents/BookReader/startup-error.log",
                )
            except tk.TclError:
                pass

    def _save_excerpt_inner(self) -> None:
        try:
            text = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST).strip()
            is_selection = bool(text)
        except tk.TclError:
            text = ""
            is_selection = False
        if not text:
            text = self.text_area.get("1.0", tk.END).strip()
        if not text:
            messagebox.showinfo(
                "Nothing to save",
                "Open a book, paste text, or select something first.")
            return

        now = datetime.now()
        ts_human = now.strftime("%Y-%m-%d %H-%M")
        # Save lands in the user's CURRENT cognitive zone (not always
        # GREEN). This matters because the Library opens filtered to
        # the current zone — saving while at load=5 (YELLOW) used to
        # write a GREEN file the user couldn't find. Now load=5 saves
        # land in YELLOW, load=2 saves land in RED, etc.
        zone = self._zone_for_load(self._cognitive_load)
        load = int(self._cognitive_load)

        # Naming standard from Sentinel Prime spec:
        # BOOKREADER-EXCERPT-<source_slug>_<YYYY-MM-DD>_v001.md
        # We also keep a human-readable title inside the file as the H1.
        if self.current_file:
            source_stem = Path(self.current_file).stem
            what = "excerpt" if is_selection else "copy"
            heading = f"Saved {ts_human} — {what} from {source_stem}"
        else:
            source_stem = None
            heading = f"Saved {ts_human} — pasted text"
        slug = re.sub(r"[^a-z0-9]+", "_",
                       (source_stem or "pasted_text").lower()).strip("_")[:60] or "excerpt"
        # Include H-M-S in the filename so multiple same-day saves of the
        # same source don't collide and pile up as _v002/_v003/...
        ts_machine_local = now.strftime("%Y-%m-%dT%H-%M-%S")
        filename_stem = f"BOOKREADER-EXCERPT-{slug}_{ts_machine_local}_v001"

        # YAML front-matter — schema mirrors the sidecar JSON so the .md
        # is self-describing even if someone reads it outside the app.
        front_matter = (
            "---\n"
            f"doc_id: {filename_stem}\n"
            f"zone: {zone}\n"
            f"cognitive_load: {load}\n"
            f"source_book: {json.dumps(self.current_file)}\n"
            f"timestamp: {now.isoformat(timespec='seconds')}\n"
            f"selection: {'true' if is_selection else 'false'}\n"
            f"word_count: {len(text.split())}\n"
            "tags: []\n"
            "---\n\n"
        )
        body = (
            f"{front_matter}"
            f"# {heading}\n\n"
            f"- Saved: {now.isoformat(timespec='seconds')}\n"
            f"- Source: {self.current_file or '(pasted text)'}\n"
            f"- Word count: {len(text.split())}\n\n"
            f"---\n\n"
            f"{text}\n"
        )

        saved: list[tuple[str, str]] = []

        # --- Primary destination: the Library ---------------------------
        os.makedirs(LIBRARY_DIR, exist_ok=True)
        lib_path = os.path.join(LIBRARY_DIR, filename_stem + ".md")
        b_root, b_ext = os.path.splitext(lib_path)
        n = 1
        while os.path.exists(lib_path):
            lib_path = f"{b_root}_v{n+1:03d}{b_ext}"
            n += 1
        with open(lib_path, "w", encoding="utf-8") as f:
            f.write(body)
        # Sidecar mirrors the YAML front-matter — the Library zone
        # filter reads the sidecar, not the front-matter, so both
        # writes are needed.
        self._save_meta(lib_path, {
            "doc_id":         filename_stem,
            "zone":           zone,
            "cognitive_load": load,
            "source_book":    self.current_file,
            "timestamp":      now.isoformat(timespec="seconds"),
            "tags":           [],
        })
        saved.append(("📚 Library", lib_path))

        # --- Best-effort: Claude cross-session excerpts -----------------
        try:
            os.makedirs(EXCERPTS_DIR, exist_ok=True)
            ts_machine = now.strftime("%Y-%m-%dT%H-%M-%S")
            stem = Path(self.current_file).stem if self.current_file else "excerpt"
            safe2 = "".join(c if c.isalnum() or c in "._-" else "_"
                              for c in stem)[:60] or "excerpt"
            ex_path = os.path.join(EXCERPTS_DIR, f"{ts_machine}__{safe2}.md")
            with open(ex_path, "w", encoding="utf-8") as f:
                f.write(body)
            saved.append(("📎 Claude excerpts", ex_path))
        except Exception:
            # Non-fatal: the Library save already succeeded.
            pass

        # If the Library window is open, flip its filter to the saved
        # file's zone so the new entry is immediately visible. Otherwise
        # the user sees their save "vanish" into a zone the current
        # filter is hiding.
        try:
            if (self._library_win is not None
                    and self._library_win.winfo_exists()):
                if self._library_zone_filter != zone:
                    self._library_set_zone_filter(zone)
                else:
                    self._refresh_library_list()
        except Exception:
            pass

        library_path = saved[0][1]
        emoji = LIBRARY_ZONE_EMOJI.get(zone, "")
        summary = "\n\n".join(f"{lbl}:\n   {p}" for lbl, p in saved)
        messagebox.showinfo(
            "Saved",
            f"Saved to your Library in the {emoji} {zone} zone "
            f"(cognitive load {load}).\n\n"
            f"Filename:\n   {os.path.basename(library_path)}\n\n"
            "It'll show up under 📚 Library — click the "
            f"{emoji} {zone} filter button or All to see it.\n\n{summary}",
        )
        self.set_status(
            f"💾 Saved → {emoji} {zone}: {os.path.basename(library_path)}")


def main() -> None:
    # Use TkinterDnD's Tk subclass if available so Toplevel windows
    # (the Library, study workspace) can register as drop targets.
    # Falls back transparently to a plain Tk root if not installed.
    if HAS_DND:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
    # Apply the Sentinel icon to the window so the taskbar and title bar
    # show "S" instead of the default Tk feather. Missing or unreadable
    # icon files are non-fatal — the app launches without it.
    try:
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  "sentinel.ico")
        if os.path.exists(icon_path):
            root.iconbitmap(default=icon_path)
    except (tk.TclError, OSError):
        pass
    app = BookReader(root)
    # Auto-launch the Session Start wizard on the first launch of the
    # day. Delayed so the dashboard paints first — otherwise the modal
    # pops up against an empty window.
    root.after(400, app._maybe_auto_start_wizard)
    def on_close():
        try: app._stop_mic()
        except Exception: pass
        try: app._stop_timer(announce=False)
        except Exception: pass
        try: app._save_notes()
        except Exception: pass
        try:
            if app._study_win is not None and app._study_win.winfo_exists():
                # Auto-save any open journal entry that has unsaved edits.
                try:
                    if (app._journal_current_id is not None and
                            hasattr(app, "_journal_body")):
                        app._save_current_journal_entry()
                except Exception: pass
                # Force-save the Eisenhower matrix too.
                try:
                    if app._eisenhower_widgets:
                        app._save_all_eisenhower()
                except Exception: pass
                # Force-save Study Notes if the tab was opened.
                try:
                    if app._study_notes_widget is not None:
                        app._save_study_notes()
                except Exception: pass
                app._study_win.destroy()
        except Exception: pass
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()


if __name__ == "__main__":
    # Under pythonw / pyw there is no console — any uncaught exception
    # would otherwise vanish into the void. Persist the traceback so the
    # next launch failure can be diagnosed without re-running by hand.
    try:
        main()
    except Exception:
        import traceback as _tb
        try:
            log_dir = os.path.expanduser(r"~\OneDrive\Documents\BookReader")
            os.makedirs(log_dir, exist_ok=True)
            log_path = os.path.join(log_dir, "startup-error.log")
            with open(log_path, "a", encoding="utf-8") as _f:
                _f.write(f"\n=== {datetime.now().isoformat()} ===\n")
                _tb.print_exc(file=_f)
        except Exception:
            pass
        raise
