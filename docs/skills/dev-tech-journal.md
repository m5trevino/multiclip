---
name: dev-tech-journal
description: Use this skill to extract, analyze, and document the development history of a project from chat transcripts. It captures pivots, design decisions, feature requests, and architectural changes into "bad ass" Markdown and beautiful HTML reports. Trigger this skill when the user asks for a "dev log", "technical journal", "session summary", or wants to document the "why" behind the build.
---

# dev-tech-journal: The Soul of the Build

This skill transforms messy chat history into a high-fidelity technical archive. It is designed to capture not just *what* was built, but the *why*, the *pivots*, and the *failures* that led to the final architecture.

## Mission Parameters

1. **Deep Analysis**: Scan the entire chat history for:
   - **Feature Requests**: What did the user want?
   - **Architectural Pivots**: What changed and why?
   - **"The Old Way"**: Document legacy approaches that were discarded.
   - **Technical Invariants**: Key rules or constraints discovered.
   - **User Sentiment & Tone**: Capture the energy of the build (e.g., "fire", "bad ass", "stunting").
   - **Future Goals**: What's next on the horizon?

2. **Output Artifacts**:
   - Create a directory named `dev-log-YYYY-MM-DD`.
   - **Markdown File (`.md`)**: A structured, technical deep-dive.
   - **HTML File (`.html`)**: A beautiful, "bad ass" visual report with glassmorphism, glowing accents, and clear navigation for analysis.

## Markdown Structure
ALWAYS use this technical template:
# DEV JOURNAL: [Project Name] - [Date]
## 🎯 Mission Objective
The ultimate goal of this session/project.
## 🏗️ Architectural Evolution
- **The Legacy**: How it was done before.
- **The Pivot**: Why it changed (The "Fuckin' Ugh" moments).
- **The Current State**: The new tactical reality.
## 🧪 Technical Invariants & Rules
The ground truth laws governing the app (e.g., 21 Tax Laws, Nexus Doctrine).
## 🔥 Feature Arsenal
List of implemented features with technical rationale.
## 📡 Tactical Stack
Models, ports, proxies, and external integrations (Karbon, ai-handler).
## 🚀 Future Recon
What's left to conquer.

## HTML report Style
- **Aesthetic**: Peacock Engine style (Dark mode, #00F3FF cyan accents, neon glows).
- **Organization**: Use a sticky sidebar for navigation.
- **Visuals**: Use callout boxes for "Pivots" and "Breakthroughs."
- **Interactive**: Ensure it's easy to read and reference during code reviews.

## Execution Flow
1. **Analyze**: Ingest the chat transcript.
2. **Synthesize**: Group related thoughts into logical technical blocks.
3. **Execute**: Create the directory and write both files.
4. **Finalize**: Provide the paths to the user.
