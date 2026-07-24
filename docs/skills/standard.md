---
name: standard
description: "Reads any chat (live session or file on disk) and turns it into clean, structured Journal Entries, Instruction Entries, and a verbatim section of the user's direct instructions. High-precision signal extractor built for the Peacock organization pipeline. Version: 1.2. Triggered by: 'process this chat', 'make journal', 'journal this', 'make instruction', 'create instruction entry', 'upgrade this chat', 'peacock architect', 'architect this', or by providing a file path to a chat log/transcript. Uses precise forms for maximum signal. Extracts decisions, instructions, architecture points, pivots, failures, completions. Anti Vibe Coder compliant — no fluff. On completion, saves output as a .md file in a ./standard-skill/ subfolder and creates a termbin link for portability."
---

# Standard v1.2 - Peacock Journal Architect

## Activation Protocol

The skill activates in **two modes**:

**Mode A — Live Chat:** When the user utters any trigger phrase ("process this chat", "make journal", "journal this", "make instruction", "create instruction entry", "upgrade this chat", "peacock architect", "architect this"), immediately activate full processing mode on the entire current conversation history or any provided chat log.

**Mode B — File Input:** When the user provides a file path (absolute or relative) pointing to a chat log, transcript, or text file, read that file and process its contents with identical extraction logic. Detect file paths by patterns like `/path/to/file.txt`, `./file.md`, `~/logs/chat.txt`, or explicit instructions like "process this file: /path/to/file".

Analyze every message with surgical precision regardless of input source.

## Input Source Detection

Determine the input source in this priority order:

1. **Explicit file path provided** — If the user's message contains a recognizable file path (starts with `/`, `./`, `../`, or `~/`, or ends with `.txt`, `.md`, `.log`, `.json`, `.jsonl`), treat as **Mode B (File)**.
2. **Trigger phrase in current session** — If no file path is detected but a trigger phrase is present, treat as **Mode A (Live Chat)**.
3. **Ambiguous or missing** — If neither is clear, ask the user: "Process the current chat session, or provide a file path to process?"

## Core Rules (Non-Negotiable)

- Always analyze the entire input source (full chat history OR full file contents).
- Be extremely precise, detailed, and objective.
- Respect Anti Vibe Coder principles — maximum signal, zero bullshit or fluff.
- Output ONLY in the exact format below. No additional commentary, no intros, no explanations, no vibe outside the structure.
- Number entries sequentially (VI-001, JE-001, IE-001, etc.).
- Use intelligent, descriptive titles pulled directly from context. Pull language and intent faithfully — never invent or embellish.
- If no high-signal content exists (no explicit decisions, instructions, architecture points, pivots, failures, or completions), output exactly: "NO HIGH-SIGNAL CONTENT DETECTED. Nothing to journal or instruct."

## File Processing Protocol (Mode B)

When processing a file from disk:

1. **Read the file** using the `ReadFile` tool with the provided path.
2. **Parse the content** — Treat the entire file as the conversation transcript. If the file has structured formats (JSONL with message objects, markdown with headers, plain text with timestamps), adapt extraction accordingly but maintain the same output schema.
3. **Infer metadata**:
   - `Chat Length`: Number of messages/entries in the file (estimate if not explicit)
   - `Source File`: The file path provided
4. **Run identical extraction** — VI, JE, IE logic is identical to live chat mode.
5. **Subject slug**: Derive from the filename or inferred topic (e.g., `chat-log-05-16` → `chat-log`, `wire-chat.txt` → `wire-chat`).

## Exact Output Format (Strict)

Produce the report in this precise structure:

Peacock Journal Architect – Processing Report
Version: 1.2
Processed: [current ISO 8601 timestamp]
Source: [Live Chat Session / File: <path>]
Chat Length: X messages

DIRECT VERBATIM INSTRUCTIONS
VI-001: [Short Descriptive Title]
Original User Message (verbatim):[exact text the user typed]
(Repeat VI-XXX for every direct instruction or command the user explicitly gave in the chat)

JOURNAL ENTRIES
JE-001: [Title]
Category: [Decision / Progress / Experiment / Failure / Pivot / Architecture / Insight / Other]
Summary: [1-2 sentence summary]
Key Points:
- [bullet 1]
- [bullet 2]
(etc.)
Linked Messages: [message IDs or ranges, e.g. User:3-5 or "trigger message"]
Risks / Constraints: [bullet list or N/A]
Success Criteria: [bullet list or N/A]
(Repeat JE-XXX for each distinct high-signal moment)

INSTRUCTION ENTRIES
IE-001: [Title]
Target Agent: [Head Coach, Stat Analyst, Offensive Coordinator, Trainer, Scout, Architect, Operator, etc. — infer from context]
Instruction Type: [Behavior / Architecture / Rule / Workflow / Standard / Protocol / Decision Framework / Other]
Full Clear Instruction Text: [full precise instruction — rephrase only for clarity while preserving original intent exactly]
Must-Haves / Constraints: [bullet list]
Priority: [High / Medium / Low]
Linked Messages: [references]
(Repeat IE-XXX for each extracted instruction)

SUMMARY
Total Verbatim Instructions: X
Total Journal Entries: X
Total Instruction Entries: X
Key Themes Identified: [short comma-separated list of core themes]

Ready to copy into WALDO.

## Persistence & Delivery Protocol (Kimi CLI)

After emitting the full structured report in the response, you MUST also:

1. **Infer a short subject slug** from the chat topic or filename (2–4 words, kebab-case, e.g. `api-redesign`, `auth-overhaul`, `config-cleanup`, `chat-log`).

2. **Save the report as a .md file** using the WriteFile tool.
   - Create the subfolder if it does not exist: `./standard-skill/`
   - Filename format: `standard.created.from.chat.{subject-slug}.{MM-DD}.{YY}.md`
   - Example: `standard.created.from.chat.api-redesign.05-16.26.md`
   - Write the complete report content to this file.

3. **Create a termbin link** for easy access.
   - Use the Shell tool to run: `cat ./standard-skill/<filename>.md | nc termbin.com 9999`
   - The command will return a URL like `https://termbin.com/xxxxxx`.
   - Present this URL to the user in your final message.

## Processing Discipline

- Pre-fill every field intelligently and faithfully from source content only. Never invent details.
- Prioritize architecture points, explicit instructions, decisions, pivots, and failures as highest value.
- Maintain strict fidelity: if context is ambiguous, note it clearly in the relevant field rather than guessing.
- When processing ongoing conversation, include history up to and including the trigger message.
- When processing a file, include the entire file contents — do not truncate or skip sections.
- Every token must increase clarity or actionability for the Peacock pipeline. If it does not, it does not exist.

## Anti Vibe Coder Compliance

This skill exists for pure signal extraction only. Zero fluff. Zero padding. Zero narrative. The structure is the product.
