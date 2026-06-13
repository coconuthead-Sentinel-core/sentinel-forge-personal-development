"""Windows-scheduled appointment reminders.

The single mechanism behind appointment reminders: instead of an in-app timer
(which dies when the Book Reader closes), every warning is a real Windows
*scheduled task*. So a reminder fires whether or not the app is running, and we
ask Windows to wake the machine to run it.

For an appointment at time T we register up to three one-shot tasks at
T-60, T-30 and T-15 minutes (skipping any already in the past). Each task
launches ``reminder_flash.py`` — the light-teal OpenDyslexic alert — via
pythonw so no console window appears.

All registration goes through PowerShell's ScheduledTasks cmdlets because the
plain ``schtasks`` CLI can't set "wake the computer to run" (-WakeToRun).
Per-user interactive tasks need no admin elevation. Everything fails soft:
a reminder that can't be scheduled must never crash the save.
"""
from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime, timedelta

try:
    from lyceum.db.study_db import STUDY_DB as _STUDY_DB
except Exception:  # pragma: no cover - fallback if imported oddly
    _STUDY_DB = os.path.expanduser(r"~\OneDrive\Documents\BookReader\study.db")

DEFAULT_LEADS = (60, 30, 15)          # minutes before the appointment
TASK_FOLDER = "\\SentinelForge\\"     # all our tasks live under this path
_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def _pythonw() -> str:
    """pythonw.exe next to the running interpreter (no console flash)."""
    exe = sys.executable or "python.exe"
    cand = os.path.join(os.path.dirname(exe), "pythonw.exe")
    return cand if os.path.exists(cand) else exe


def _flash_script() -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "reminder_flash.py")


def _task_name(appt_id: int, lead: int) -> str:
    return f"Appt_{appt_id}_{lead}m"


def _run_ps(script: str) -> tuple[bool, str]:
    """Run a PowerShell snippet hidden; return (ok, message)."""
    try:
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            creationflags=_NO_WINDOW, timeout=60)
    except Exception as e:
        return False, str(e)
    if proc.returncode != 0:
        return False, (proc.stderr or proc.stdout or "PowerShell failed").strip()
    return True, (proc.stdout or "").strip()


def schedule_appointment(appt_id: int, when_dt: str,
                         leads: tuple[int, ...] = DEFAULT_LEADS,
                         db_path: str | None = None
                         ) -> tuple[list[int], str | None]:
    """Register reminder tasks for one appointment.

    when_dt is 'YYYY-MM-DD HH:MM' (local). Returns (scheduled_leads, error):
    the list of lead-times actually registered (past ones are skipped), and an
    error string if PowerShell registration failed (else None).
    """
    try:
        when = datetime.strptime(when_dt.strip(), "%Y-%m-%d %H:%M")
    except (ValueError, AttributeError):
        return [], f"Bad appointment time: {when_dt!r}"

    db = db_path or _STUDY_DB
    pyw = _pythonw()
    flash = _flash_script()
    now = datetime.now()

    # Clear any prior tasks for this appointment so re-saving doesn't duplicate.
    cancel_appointment(appt_id, leads)

    blocks: list[str] = []
    scheduled: list[int] = []
    for lead in leads:
        fire = when - timedelta(minutes=lead)
        if fire <= now + timedelta(seconds=30):
            continue  # too soon / already past — skip this warning
        at_iso = fire.strftime("%Y-%m-%dT%H:%M:%S")
        name = _task_name(appt_id, lead)
        arg = f'"{flash}" --id {appt_id} --lead {lead} --db "{db}"'
        blocks.append(
            "$a = New-ScheduledTaskAction -Execute '{pyw}' -Argument '{arg}';"
            "$t = New-ScheduledTaskTrigger -Once -At ([datetime]'{at}');"
            "$s = New-ScheduledTaskSettingsSet -WakeToRun "
            "-AllowStartIfOnBatteries -DontStopIfGoingOnBatteries "
            "-ExecutionTimeLimit (New-TimeSpan -Minutes 10);"
            "$p = New-ScheduledTaskPrincipal -UserId $env:USERNAME "
            "-LogonType Interactive -RunLevel Limited;"
            "Register-ScheduledTask -TaskName '{name}' -TaskPath '{folder}' "
            "-Action $a -Trigger $t -Settings $s -Principal $p -Force "
            "| Out-Null;".format(pyw=pyw, arg=arg, at=at_iso, name=name,
                                 folder=TASK_FOLDER))
        scheduled.append(lead)

    if not blocks:
        return [], None  # nothing in the future to schedule (e.g. set in past)

    ok, msg = _run_ps("".join(blocks))
    if not ok:
        return [], msg
    return scheduled, None


def cancel_appointment(appt_id: int,
                       leads: tuple[int, ...] = DEFAULT_LEADS) -> None:
    """Remove all reminder tasks for an appointment (best effort, silent)."""
    names = ",".join(f"'{_task_name(appt_id, lead)}'" for lead in leads)
    script = (
        f"@({names}) | ForEach-Object {{ "
        f"Unregister-ScheduledTask -TaskName $_ -TaskPath '{TASK_FOLDER}' "
        f"-Confirm:$false -ErrorAction SilentlyContinue }}")
    _run_ps(script)


def list_appointment_tasks(appt_id: int | None = None) -> list[str]:
    """Return registered reminder task names (for debugging / verification)."""
    flt = "" if appt_id is None else f" | Where-Object {{ $_.TaskName -like 'Appt_{appt_id}_*' }}"
    ok, out = _run_ps(
        f"Get-ScheduledTask -TaskPath '{TASK_FOLDER}' "
        f"-ErrorAction SilentlyContinue{flt} | "
        "Select-Object -ExpandProperty TaskName")
    if not ok or not out:
        return []
    return [ln.strip() for ln in out.splitlines() if ln.strip()]
