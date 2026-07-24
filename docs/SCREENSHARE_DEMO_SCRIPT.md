# MultiClip V3 — Live Demo Script
> Read this aloud while screensharing. Each section is ~30-60 seconds.

---

## 1. Opening (15 sec)

"This is **MultiClip** — it's a clipboard power tool I built for Linux. Instead of your system remembering just the last thing you copied, MultiClip gives you **30 hotkeyed slots**, **8 persistent snippets**, and a **live history panel** that pulls from xfce4-clipman. Think of it as a clipboard on steroids."

---

## 2. The Layout (30 sec)

*Point to each area on screen:*

- **Left side — Workbench**: 30 slots. Each one is a clipboard slot you can fill and paste from.
- **Bottom-left — Snippets**: 8 persistent text snippets that survive reboots. Good for emails, addresses, code snippets you use constantly.
- **Right side — Clipman History**: This pulls from your xfce4-clipman plugin. Every copy you've made today lives here.
- **Top toolbar**: Mode toggle — Multiclip, Orderly, Vault, Sequential.

---

## 3. The Basics — Hotkeys (45 sec)

*Do this live:*

1. **Open a text editor or browser.** Highlight some text.
2. **Press and hold Left Ctrl + Left Alt, then press 1.**
   - *Say:* "That just copied the selected text into Slot 1."
   - Watch the toast notification pop up bottom-right.
3. **Click somewhere else in the document.**
4. **Press and hold Right Ctrl + Right Alt, then press 1.**
   - *Say:* "That pasted Slot 1 at my cursor."
5. **Repeat with Slot 2, 3, 4.**
   - *Say:* "I have 10 slots mapped to digits 1-0. I can fill them all without touching the mouse."

*Bonus:* In a terminal, it automatically detects the window and pastes with **Ctrl+Shift+V** instead of Ctrl+V.

---

## 4. Clipman History Panel — The Right Side (60 sec)

*Say:* "Everything I copied before opening MultiClip is already here."

### Block Bundle
1. **Ctrl-click or Shift-click** 3 items in the Clipman list.
2. Click **"Block Bundle"**.
3. *Say:* "Those 3 items just filled the first 3 empty Workbench slots."

### 1 Slot Per Line
1. Select 2 items in Clipman.
2. Click **"1 slot per line"**.
3. *Say:* "Auto-Sequential mode fills from slot 1 upward."

### Manual Slot Mode
1. Click the **"Manual Slot"** radio under "1 slot per line".
2. **Click Slot 10** in the Workbench — it turns blue.
3. Select 2 items in Clipman, click **"1 slot per line"**.
4. *Say:* "Now it filled slots 10 and 11 instead. I chose the starting point."

---

## 5. Send to Snippets (30 sec)

1. Select an item in Clipman.
2. Click **"Send to Snippet"**.
3. *Say:* "That landed in the first empty snippet row. These survive reboots."
4. **Click the red ✕** next to a snippet.
5. *Say:* "Gone. Saved to disk instantly."

---

## 6. Orderly Mode — The Star Feature (90 sec)

*Say:* "This is the big new feature. Orderly mode watches my clipboard and auto-fills slots as I copy things."

1. Click the **"Orderly"** radio button at the top.
2. *Point:* "FIFO and LIFO buttons appear, plus Paste Next."
3. **Open a browser or document.** Copy 3 different pieces of text with Ctrl+C.
4. *Switch back to MultiClip.* *Say:* "Each copy automatically landed in the next slot — slot 1, then 2, then 3. The orange highlight shows where the next copy will go."
5. **Click "Paste Next"** in MultiClip.
6. *Say:* "FIFO mode pastes slot 1, then 2, then 3."
7. **Click "LIFO"**, then click **"Paste Next"** 3 times.
8. *Say:* "LIFO reverses it — pastes 3, then 2, then 1."

---

## 7. Preview Popup (30 sec)

1. **Double-click** any item in Clipman History.
2. *Say:* "This shows the full text. If it's huge, I can read it here instead of squinting at the list."
3. Enter **slot 15** in the spinbox, click **Transfer**.
4. *Say:* "Direct transfer to any slot without closing the popup."

---

## 8. Closing (15 sec)

*Say:* "That's MultiClip. 30 hotkeyed slots, persistent snippets, live history, auto-capture in Orderly mode, and zero mouse required once you learn the combos. It's built for people who copy-paste for a living."

---

## Pro Tips for the Demo

| Tip | Why |
|-----|-----|
| Have a browser + text editor open before starting | Smooth transitions between copy sources |
| Pre-load slots 1-3 with fun text | Instant paste demo without fumbling |
| Keep the toast visible | It's satisfying visual feedback |
| If Orderly mode feels fast, mention the 300ms timer | Shows you understand the internals |

---

*Total runtime: ~5-6 minutes*
