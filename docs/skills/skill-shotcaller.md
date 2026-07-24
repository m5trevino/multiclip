---
name: skill-shotcaller
description: "High-level orchestrator for the Syndicate Skill Lifecycle. Manages the end-to-end production of agent skills: Intel (Planning), Fabrication (Authoring), Tricorder (Audit), Runway (Deployment), and Watchtower (Governance)."
category: meta
risk: safe
source: community
tags: "[orchestrator, meta-skill, workflow, automation]"
allowed-tools: "*"
date_added: "2026-05-18"
---

# skill-shotcaller

## Purpose

To manage the full lifecycle of agent skill production with industrial precision. This skill sequences the Syndicate's top-tier specialist skills into a deterministic pipeline, ensuring all assets are built to "Sand Hill Road" standards.

## When to Use This Skill

This skill should be used when:
- User wants to create a new high-quality agent skill
- User wants to update or refactor an existing skill
- User needs to audit a collection of skills for quality and security
- User wants to ensure a skill is correctly installed and registered

## The Syndicate Playbook (Master Itinerary)

Follow these phases in exact sequence. Do not skip steps.

### Phase 1: THE INTEL PHASE (Path Selection)
**Agent:** @skill-writer
1. Invoke @skill-writer to resolve the target skill path and intended operation (create or update).
2. Follow the "Step 1: Resolve target and path" logic to select the required path(s) and classify the skill (Workflow, Integration, Security, etc.).
3. Ask clarifying questions only if depth requirements are ambiguous.

### Phase 2: THE FABRICATION PHASE (Industrial Authoring)
**Agent:** @skill-generate
1. Once the plan is set, invoke @skill-generate to author the SKILL.md and supporting files.
2. Ensure the skill follows the "Progressive Disclosure" pattern (SKILL.md < 500 lines, details in references/).
3. Include real code blocks, concrete examples, and high-value "Common Mistakes" sections.

### Phase 3: THE TRICORDER PHASE (Zero-Trust Audit)
**Agents:** @skill-check + @skill-scanner
1. Invoke @skill-check to validate the new asset against the agentskills specification.
2. Target: 100/100 score. Fix all critical and major issues immediately.
3. Simultaneously invoke @skill-scanner to check for security holes, hardcoded secrets, and unsafe bash patterns.

### Phase 4: THE RUNWAY PHASE (Deployment)
**Agent:** @skill-installer
1. Invoke @skill-installer to handle the physical deployment.
2. Perform global installation with absolute path symlinks.
3. Update the Syndicate Skill Registry and package the asset as a ZIP for the Web UI.

### Phase 5: THE WATCHTOWER PHASE (Governance)
**Agent:** @skill-sentinel
1. Invoke @skill-sentinel to register the new skill for automated health monitoring.
2. Perform a token-cost audit to verify context efficiency.
3. Add the skill to the 7-dimension audit rotation (Quality, Security, Performance, Governance, Documentation, Dependencies, Cross-Skill).

## Operational Guidelines

- **Stop the Line:** If Phase 3 (skill-check) returns a failing score or critical security risk, do not proceed to Phase 4. Fix the asset first.
- **Context Efficiency:** Use references/ for detailed itineraries or checklists to keep the core SKILL.md lean.
- **Verification:** Always confirm the success of each phase before triggering the next agent in the sequence.

## Example Trigger Phrases
- "shotcaller: manifest a new skill for PDF extraction"
- "orchestrate the build for a jira-integration skill"
- "shotcaller: update the existing color-expert asset"
- "run the full syndicate pipeline for my-test-skill"
