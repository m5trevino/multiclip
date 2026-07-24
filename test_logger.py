#!/usr/bin/env python3
"""
MultiClip V3 — Interactive Test Logger
========================================
Run this in a terminal while following TEST_INSTRUCTIONS.md.
It guides you step-by-step and auto-logs file changes + process state.

Usage:
    python3 test_logger.py

Output:
    test-log-YYYY-MM-DD-HHMMSS.md
"""

import os
import sys
import re
import time
import json
import hashlib
import threading
import subprocess
from datetime import datetime
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────
INSTRUCTIONS_FILE = "TEST_INSTRUCTIONS.md"
BASE_DIR = Path("/home/flintx/multiclip")
WATCH_FILES = [
    BASE_DIR / "clipboard_dict.json",
    BASE_DIR / "snippets.json",
]
POLL_INTERVAL = 2.0  # seconds

# ── Colors ──────────────────────────────────────────────────────────
class C:
    HEADER = "\033[95m"
    OK = "\033[92m"
    WARN = "\033[93m"
    FAIL = "\033[91m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    END = "\033[0m"

# ── Parse Instructions ──────────────────────────────────────────────
def parse_instructions(path):
    with open(path, "r") as f:
        text = f.read()

    steps = []
    # Split on "### Step N"
    chunks = re.split(r"(?=### Step \d+)", text)
    for chunk in chunks:
        m = re.match(r"### Step (\d+) — (.+)\n", chunk)
        if not m:
            continue
        num = int(m.group(1))
        title = m.group(2).strip()

        action = ""
        expected = ""
        in_action = False
        in_expected = False
        for line in chunk.splitlines()[1:]:
            if line.startswith("**Action:**"):
                in_action = True
                in_expected = False
                action = line.replace("**Action:**", "").strip()
            elif line.startswith("**Expected:**"):
                in_action = False
                in_expected = True
                expected = line.replace("**Expected:**", "").strip()
            elif line.startswith("### ") or line.startswith("## "):
                break
            elif in_action and line.strip():
                action += "\n" + line.strip()
            elif in_expected and line.strip():
                expected += "\n" + line.strip()

        steps.append({
            "num": num,
            "title": title,
            "action": action.strip(),
            "expected": expected.strip(),
        })
    return steps

# ── File Monitor ────────────────────────────────────────────────────
class FileMonitor:
    def __init__(self, files, interval=2.0):
        self.files = files
        self.interval = interval
        self.events = []
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._state = {str(p): self._snapshot(p) for p in files}

    def _snapshot(self, path):
        if not path.exists():
            return (0, "")
        mtime = path.stat().st_mtime
        try:
            with open(path, "rb") as f:
                h = hashlib.md5(f.read()).hexdigest()[:16]
        except:
            h = "err"
        return (mtime, h)

    def _loop(self):
        while not self._stop.is_set():
            time.sleep(self.interval)
            for path in self.files:
                old = self._state.get(str(path), (0, ""))
                new = self._snapshot(path)
                if new[0] != old[0] or new[1] != old[1]:
                    self._state[str(path)] = new
                    self.events.append({
                        "time": datetime.now().isoformat(timespec="seconds"),
                        "file": path.name,
                        "event": "modified",
                    })

    def start(self):
        self._thread.start()

    def stop(self):
        self._stop.set()
        self._thread.join(timeout=3)

    def flush_events(self):
        ev = self.events[:]
        self.events.clear()
        return ev

# ── Process Monitor ─────────────────────────────────────────────────
def is_multiclip_running():
    try:
        out = subprocess.check_output(["pgrep", "-f", "multiclip.py"], text=True)
        return len(out.strip().splitlines()) > 0
    except subprocess.CalledProcessError:
        return False

# ── Main ────────────────────────────────────────────────────────────
def main():
    if not os.path.exists(INSTRUCTIONS_FILE):
        print(f"{C.FAIL}ERROR: {INSTRUCTIONS_FILE} not found.{C.END}")
        print(f"Run from /home/flintx/multiclip directory.")
        sys.exit(1)

    steps = parse_instructions(INSTRUCTIONS_FILE)
    if not steps:
        print(f"{C.FAIL}ERROR: No steps found in {INSTRUCTIONS_FILE}{C.END}")
        sys.exit(1)

    log_name = f"test-log-{datetime.now().strftime('%Y-%m-%d-%H%M%S')}.md"
    log_path = BASE_DIR / log_name

    # Start file monitor
    monitor = FileMonitor(WATCH_FILES, POLL_INTERVAL)
    monitor.start()

    # Log header
    header = f"""# MultiClip V3 Test Log

**Date:** {datetime.now().isoformat(timespec='seconds')}
**Tester:** {os.environ.get('USER', 'unknown')}
**Instructions:** {INSTRUCTIONS_FILE}

---

"""
    with open(log_path, "w") as f:
        f.write(header)

    print(f"\n{C.HEADER}{'='*60}{C.END}")
    print(f"{C.BOLD}  MultiClip V3 — Interactive Test Logger{C.END}")
    print(f"{C.HEADER}{'='*60}{C.END}")
    print(f"\n  Steps loaded: {len(steps)}")
    print(f"  Log file: {log_path}")
    print(f"  Watching: {', '.join(p.name for p in WATCH_FILES)}")
    print(f"\n  Controls:")
    print(f"    {C.OK}y{C.END} = Pass    {C.FAIL}n{C.END} = Fail    {C.WARN}s{C.END} = Skip")
    print(f"    Any other text = Note (then press Enter)")
    print(f"    {C.CYAN}Ctrl+C{C.END} = Quit and save partial log")
    print(f"\n{C.HEADER}{'='*60}{C.END}\n")

    results = []
    try:
        for step in steps:
            num = step["num"]
            title = step["title"]
            action = step["action"]
            expected = step["expected"]

            # Show step
            print(f"\n{C.BOLD}Step {num}/{len(steps)} — {title}{C.END}")
            print(f"{C.CYAN}Action:{C.END}")
            for line in action.splitlines():
                print(f"  {line}")
            print(f"{C.CYAN}Expected:{C.END}")
            for line in expected.splitlines():
                print(f"  {line}")

            # Flush any file events that happened before this step
            pre_events = monitor.flush_events()

            # Prompt
            prompt = f"\n{C.BOLD}[y/n/s or note] > {C.END}"
            try:
                raw = input(prompt).strip()
            except EOFError:
                break

            result = raw.lower()
            if result == "y":
                status = "PASS"
                status_color = C.OK
                note = ""
            elif result == "n":
                status = "FAIL"
                status_color = C.FAIL
                note = ""
            elif result == "s":
                status = "SKIP"
                status_color = C.WARN
                note = ""
            else:
                status = "NOTE"
                status_color = C.WARN
                note = raw

            # Flush file events that happened during this step
            post_events = monitor.flush_events()
            all_events = pre_events + post_events

            running = is_multiclip_running()

            # Console feedback
            print(f"  {status_color}→ {status}{C.END}", end="")
            if note:
                print(f"  ({note})")
            else:
                print()
            if all_events:
                for ev in all_events:
                    print(f"  {C.CYAN}[AUTO] {ev['file']} {ev['event']} at {ev['time']}{C.END}")
            if not running:
                print(f"  {C.FAIL}[AUTO] WARNING: multiclip.py is NOT running{C.END}")

            # Write to log
            log_entry = f"""## Step {num} — {title}

**Status:** {status}
**Time:** {datetime.now().isoformat(timespec='seconds')}
**Action:**
{action}

**Expected:**
{expected}

"""
            if note:
                log_entry += f"**Note:** {note}\n\n"
            if all_events:
                log_entry += "**File Events:**\n"
                for ev in all_events:
                    log_entry += f"- `{ev['file']}` {ev['event']} at {ev['time']}\n"
                log_entry += "\n"
            if not running:
                log_entry += "**WARNING:** multiclip.py was not detected running during this step.\n\n"
            log_entry += "---\n\n"

            with open(log_path, "a") as f:
                f.write(log_entry)

            results.append({"num": num, "status": status})

    except KeyboardInterrupt:
        print(f"\n\n{C.WARN}Interrupted. Saving partial log...{C.END}")

    # Summary
    monitor.stop()
    total = len(results)
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    skipped = sum(1 for r in results if r["status"] == "SKIP")
    noted = sum(1 for r in results if r["status"] == "NOTE")

    summary = f"""## Summary

| Metric | Count |
|--------|-------|
| Total Steps | {total} |
| Passed | {passed} |
| Failed | {failed} |
| Skipped | {skipped} |
| Notes | {noted} |

**Completion:** {passed}/{total} passed ({100*passed//total if total else 0}%)

*Log generated by test_logger.py*
"""
    with open(log_path, "a") as f:
        f.write(summary)

    print(f"\n{C.HEADER}{'='*60}{C.END}")
    print(f"{C.BOLD}  DONE{C.END}")
    print(f"  Log saved: {log_path}")
    print(f"  Passed: {C.OK}{passed}{C.END}  Failed: {C.FAIL}{failed}{C.END}  Skipped: {C.WARN}{skipped}{C.END}  Notes: {noted}")
    print(f"{C.HEADER}{'='*60}{C.END}\n")

if __name__ == "__main__":
    main()
