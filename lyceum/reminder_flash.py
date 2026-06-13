"""Standalone appointment-reminder flash.

Launched by a Windows scheduled task (see ``lyceum/reminders.py``) at each
warning time — so it runs even when the main Book Reader is closed. It reads
one appointment from study.db, then shows a full-screen, top-most, gently
pulsing LIGHT-TEAL alert in the OpenDyslexic font naming WHO / WHERE and how
long until the appointment, wakes the screen if it's off, and plays a soft
chime. Dismiss with a click, Esc, or it auto-closes after a couple of minutes.

Usage:
    pythonw reminder_flash.py --id <appointment_id> --lead <60|30|15|0> \
            --db "<path to study.db>"

It is deliberately dependency-free (stdlib + tkinter only) and fails quietly:
a reminder that can't render should never pop a traceback on the user.
"""
from __future__ import annotations

import argparse
import os
import sqlite3
import sys

# ----- gentle palette (light teal, never red/green — this is a reminder) -----
TEAL_LIGHT = "#6FD0C9"   # primary background
TEAL_DEEP = "#4FB8B1"    # pulse partner — close enough to feel like breathing
INK = "#06292B"          # dark teal-navy text: high contrast, easy on the eyes
INK_SOFT = "#0C3F42"

LEAD_PHRASE = {
    60: "in 1 hour",
    30: "in 30 minutes",
    15: "in 15 minutes",
    0: "now",
}


def _read_appointment(db_path: str, appt_id: int):
    """Return (title, who, location, when_dt, status) or None."""
    try:
        con = sqlite3.connect(db_path)
        row = con.execute(
            "SELECT title, who, location, when_dt, status "
            "FROM appointments WHERE id=?", (appt_id,)).fetchone()
        con.close()
    except sqlite3.Error:
        return None
    return row


def _wake_screen() -> None:
    """Best-effort: keep the display on and nudge it awake if it was off.

    SetThreadExecutionState asks Windows to keep the display powered; a tiny
    mouse jiggle is what actually turns a display back ON if it had slept.
    Both are wrapped — failure here must never stop the reminder showing.
    """
    try:
        import ctypes
        ES_CONTINUOUS = 0x80000000
        ES_DISPLAY_REQUIRED = 0x00000002
        ES_SYSTEM_REQUIRED = 0x00000001
        ctypes.windll.kernel32.SetThreadExecutionState(
            ES_CONTINUOUS | ES_DISPLAY_REQUIRED | ES_SYSTEM_REQUIRED)
    except Exception:
        pass
    try:
        import ctypes
        MOUSEEVENTF_MOVE = 0x0001
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_MOVE, 1, 0, 0, 0)
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_MOVE, -1, 0, 0, 0)
    except Exception:
        pass


def _chime() -> None:
    try:
        import winsound
        winsound.MessageBeep(winsound.MB_ICONASTERISK)
    except Exception:
        pass


def _pick_font(root) -> str:
    """Use OpenDyslexic if installed, else a clear, wide fallback."""
    try:
        import tkinter.font as tkfont
        fams = {f.lower(): f for f in tkfont.families(root)}
        for want in ("opendyslexic", "open dyslexic", "opendyslexic three"):
            if want in fams:
                return fams[want]
        for fb in ("verdana", "segoe ui", "tahoma"):
            if fb in fams:
                return fams[fb]
    except Exception:
        pass
    return "Verdana"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", type=int, required=True)
    ap.add_argument("--lead", type=int, default=0)
    ap.add_argument("--db", default="")
    args = ap.parse_args()

    db_path = args.db or os.path.expanduser(
        r"~\OneDrive\Documents\BookReader\study.db")

    appt = _read_appointment(db_path, args.id)
    if appt is None:
        return 0  # appointment vanished — nothing to remind about
    title, who, location, when_dt, status = appt
    if (status or "open") != "open":
        return 0  # done/cancelled — don't nag

    # Pull the clock time out of when_dt ('YYYY-MM-DD HH:MM') for display.
    clock = ""
    if when_dt and " " in when_dt:
        clock = when_dt.split(" ", 1)[1]

    try:
        import tkinter as tk
    except Exception:
        return 0

    _wake_screen()

    try:
        root = tk.Tk()
    except Exception:
        return 0
    root.title("Sentinel Forge — Reminder")
    try:
        root.attributes("-fullscreen", True)
    except tk.TclError:
        sw = root.winfo_screenwidth(); sh = root.winfo_screenheight()
        root.geometry(f"{sw}x{sh}+0+0")
        root.overrideredirect(True)
    try:
        root.attributes("-topmost", True)
    except tk.TclError:
        pass
    root.configure(bg=TEAL_LIGHT)
    root.configure(cursor="hand2")

    fam = _pick_font(root)
    try:
        sh = root.winfo_screenheight()
    except tk.TclError:
        sh = 800
    big = max(48, int(sh * 0.11))
    med = max(28, int(sh * 0.055))
    small = max(18, int(sh * 0.032))
    tiny = max(13, int(sh * 0.022))

    wrap = tk.Frame(root, bg=TEAL_LIGHT)
    wrap.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(wrap, text="⏰  REMINDER", bg=TEAL_LIGHT, fg=INK_SOFT,
             font=(fam, small, "bold")).pack(pady=(0, 6))

    lead_txt = LEAD_PHRASE.get(args.lead, f"in {args.lead} minutes")
    head = tk.Label(wrap, text=(title or "Appointment"), bg=TEAL_LIGHT, fg=INK,
                    font=(fam, big, "bold"), wraplength=int(
                        root.winfo_screenwidth() * 0.85), justify="center")
    head.pack(pady=(0, 4))

    when_line = lead_txt if not clock else f"{lead_txt}  —  at {clock}"
    tk.Label(wrap, text=when_line, bg=TEAL_LIGHT, fg=INK,
             font=(fam, med, "bold")).pack(pady=(0, 18))

    if who:
        tk.Label(wrap, text=f"\U0001f465  Who:  {who}", bg=TEAL_LIGHT, fg=INK_SOFT,
                 font=(fam, small)).pack(pady=2)
    if location:
        tk.Label(wrap, text=f"\U0001f4cd  Where:  {location}", bg=TEAL_LIGHT,
                 fg=INK_SOFT, font=(fam, small)).pack(pady=2)

    tk.Label(wrap, text="Click anywhere, or press Esc, to dismiss",
             bg=TEAL_LIGHT, fg=INK_SOFT, font=(fam, tiny, "italic")
             ).pack(pady=(28, 0))

    _chime()

    # ---- gentle pulse: breathe the background between two close teals ----
    pulse = {"on": True}

    def _breathe():
        if not root.winfo_exists():
            return
        pulse["on"] = not pulse["on"]
        bg = TEAL_LIGHT if pulse["on"] else TEAL_DEEP
        root.configure(bg=bg)
        wrap.configure(bg=bg)
        for child in wrap.winfo_children():
            try:
                child.configure(bg=bg)
            except tk.TclError:
                pass
        root.after(900, _breathe)

    def _dismiss(*_):
        try:
            # release the display-keep-awake request on the way out
            import ctypes
            ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)
        except Exception:
            pass
        try:
            root.destroy()
        except tk.TclError:
            pass

    root.bind("<Button-1>", _dismiss)
    root.bind("<Escape>", _dismiss)
    root.bind("<Key>", _dismiss)
    root.after(900, _breathe)
    root.after(120_000, _dismiss)   # auto-close after 2 minutes
    try:
        root.focus_force()
    except tk.TclError:
        pass
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
