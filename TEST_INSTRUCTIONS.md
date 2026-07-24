# MultiClip V3 — Manual QA Test Instructions

> **How to use this:** Open this file in a text editor. Run `python3 test_logger.py` in a terminal beside it. Follow each step in order. The logger will prompt you after each action.

---

## PRE-FLIGHT

### Step 1 — Syntax Check
**Action:** In terminal, run `python3 -m py_compile multiclip.py gui/main_window.py`  
**Expected:** No output (silent pass)  
**Logger:** Will auto-verify this for you.

### Step 2 — Launch App
**Action:** Kill any old instance, then launch fresh:  
```bash
sudo kill -9 $(pgrep -f multiclip.py) 2>/dev/null; sudo /home/flintx/multiclip/.venv/bin/python3 multiclip.py &
```  
**Expected:** Window opens. Title bar says "MultiClip V2 - Industrial Workstation". No console errors.

### Step 3 — UI Element Check
**Action:** Look at the window. Verify these exist:  
**Expected:**
- [ ] 30 Workbench slots (left side, two columns)
- [ ] 8 Snippet rows (bottom-left, with red ✕ buttons)
- [ ] Clipman History panel (right side, with listbox)
- [ ] Top toolbar with Multiclip / Orderly / Vault / Sequential radios
- [ ] Bottom status bar showing "Ready | Target: Any"
- [ ] Block Bundle button, 1 slot per line button, Send to Snippet button, Lock Selection button
- [ ] Auto-Sequential / Manual Slot radios under 1 slot per line

---

## TRANSFER FEATURES

### Step 4 — Block Bundle
**Action:**
1. Clear all slots (click CLEAR ALL, confirm).
2. In Clipman History, Ctrl-click 3 different items.
3. Click **Block Bundle**.
**Expected:** First 3 empty slots fill with those items. Each slot flashes gold (~2 sec). Toast appears.

### Step 5 — 1 Slot Per Line (Auto)
**Action:**
1. Ensure "Auto-Sequential" is selected under 1 slot per line.
2. Select 2 items in Clipman History.
3. Click **1 slot per line**.
**Expected:** Slots fill from first empty slot (e.g., 1 and 2 if empty, or next available).

### Step 6 — 1 Slot Per Line (Manual)
**Action:**
1. Click **Manual Slot** radio.
2. Click **Slot 10** in Workbench — it turns blue.
3. Select 2 items in Clipman History.
4. Click **1 slot per line**.
**Expected:** Slots 10 and 11 fill.

### Step 7 — 1 Slot Per Line (Wrap)
**Action:**
1. Click Slot 29 in Workbench (Manual Slot mode).
2. Select 3 items in Clipman History.
3. Click **1 slot per line**.
**Expected:** Slots 29, 30, and 1 fill (wraps around).

### Step 8 — Slots Full Dialog
**Action:**
1. Fill all 30 slots (paste random text into each, or use Block Bundle repeatedly).
2. Select 1 item in Clipman History.
3. Click **Block Bundle**.
**Expected:** Dialog appears: "ALL 30 OG SLOTS ARE FULL" asking for a target slot or Cancel.

### Step 9 — Preview Transfer
**Action:**
1. Double-click any item in Clipman History.
2. In the popup, enter slot **15** in the spinbox.
3. Click **Transfer**.
**Expected:** Slot 15 fills. Popup stays open.

---

## ORDERLY MODE

### Step 10 — Orderly Activation
**Action:** Click the **Orderly** radio button in the top toolbar.
**Expected:**
- FIFO / LIFO / Paste Next buttons appear below the Clipman buttons.
- Status bar may update.
- No console errors.

### Step 11 — Orderly Capture
**Action:**
1. Ensure Orderly mode is active.
2. Open a text editor or browser **beside** MultiClip.
3. Copy 3 different pieces of text with Ctrl+C, waiting ~1 sec between each.
4. Switch back to MultiClip.
**Expected:** Each copy auto-fills the next slot (1, 2, 3). Slots flash gold.

### Step 12 — Orderly Wrap
**Action:**
1. With Orderly active, note the current "Next" slot shown in status bar.
2. Keep copying text until you pass slot 30.
**Expected:** After slot 30, next copy overwrites slot 1. No crash.

### Step 13 — Orderly FIFO Paste
**Action:**
1. Ensure FIFO is selected (green highlight).
2. Put your cursor in a text editor.
3. Click **Paste Next** in MultiClip 3 times.
**Expected:** Pastes slot 1, then slot 2, then slot 3.

### Step 14 — Orderly LIFO Paste
**Action:**
1. Click **LIFO** button (red highlight).
2. Click **Paste Next** 3 times.
**Expected:** Pastes slot 3, then slot 2, then slot 1.

### Step 15 — Next-Slot Highlight
**Action:** After an Orderly capture, look at the Workbench.
**Expected:** The slot that will receive the NEXT copy glows orange (#ff9966).

### Step 16 — Status Bar
**Action:** With Orderly active and some slots filled, read the bottom status bar.
**Expected:** Shows "Queue: N items | Next: Slot XX".

### Step 17 — Orderly Deactivation
**Action:** Click the **Multiclip** radio button.
**Expected:** FIFO/LIFO/Paste Next buttons disappear. Orange/green highlights clear.

### Step 18 — GUI Suppression
**Action:**
1. Activate Orderly mode.
2. Click inside a MultiClip text field (e.g., a Snippet entry).
3. Copy some text with Ctrl+C.
**Expected:** The copy is IGNORED — it does NOT appear in Workbench slots.

---

## SNIPPETS

### Step 19 — Send to Snippet
**Action:**
1. Select an item in Clipman History.
2. Click **Send to Snippet**.
**Expected:** Item lands in first empty snippet row. Row flashes green (~2 sec). Toast appears.

### Step 20 — Snippet X Remove
**Action:** Click the red **✕** next to a filled snippet.
**Expected:** Entry clears. `snippets.json` is updated.

### Step 21 — Snippet Persistence
**Action:**
1. Add text to snippet S3.
2. Close MultiClip.
3. Re-launch MultiClip.
**Expected:** S3 still contains the text.

### Step 22 — Snippets Full
**Action:**
1. Fill all 8 snippets with text.
2. Select an item in Clipman History.
3. Click **Send to Snippet**.
**Expected:** "Snippets Full" warning dialog appears.

---

## VISUAL FEEDBACK

### Step 23 — Slot Flash
**Action:** Perform any Workbench transfer (Block Bundle or 1 slot per line).
**Expected:** Destination slot background pulses gold for ~2 seconds.

### Step 24 — Snippet Flash
**Action:** Send an item to Snippet.
**Expected:** Destination snippet entry background pulses green for ~2 seconds.

### Step 25 — Flash Restart
**Action:** Rapidly transfer 3 items to the same slot in quick succession.
**Expected:** Flash restarts cleanly each time. No stacking glitches.

---

## REGRESSION — HOTKEYS

### Step 26 — Copy Hotkey
**Action:**
1. In any app, select text.
2. Press and hold **Left Ctrl + Left Alt**, then press **2**.
**Expected:** Toast appears: "LEFT COMBO → COPY SLOT 02". Slot 2 now contains that text.

### Step 27 — Paste Hotkey
**Action:**
1. Click where you want to paste.
2. Press and hold **Right Ctrl + Right Alt**, then press **2**.
**Expected:** Slot 2 content pastes at cursor. Toast appears.

### Step 28 — Terminal Paste
**Action:**
1. Open a terminal.
2. Press and hold **Right Ctrl + Right Alt**, then press **3**.
**Expected:** Slot 3 pastes using Ctrl+Shift+V (terminal-aware).

### Step 29 — Service Boot
**Action:** Run `sudo /etc/init.d/multiclip restart`
**Expected:** One instance starts. No display errors. Hotkeys work after restart.

---

## POST-TEST

### Step 30 — JSON Valid
**Action:** In terminal:  
```bash
python3 -c "import json; json.load(open('clipboard_dict.json')); json.load(open('snippets.json'))"
```  
**Expected:** No errors.

### Step 31 — Clean Exit
**Action:** Close MultiClip. Run `ps aux | grep multiclip`.
**Expected:** No dangling multiclip processes.

---

*End of test plan. Total steps: 31.*
