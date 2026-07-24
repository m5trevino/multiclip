---
name: deepdive
description: Universal project documentation with visual architecture, web design handoff specs, and conversation archaeology. Generates Mermaid diagrams, PNG renders, and pixel-perfect design instructions for developer handoff.
---

# DeepDive: Project Intelligence + Design Handoff System

## Capabilities

1. **Code Archaeology** - Full codebase analysis with risk scoring
2. **Visual Architecture** - Mermaid diagrams auto-rendered to PNG
3. **Web Design Handoff** - Complete design specs for any existing web app
4. **Conversation Mining** - Extract decisions and TODOs from chat logs

## Output Structure

/docs/
├── 00-EXECUTIVE_OVERVIEW.md
├── 01-BASIC_OVERVIEW.md
├── 02-DETAILED_OVERVIEW.md
├── 03-EXTENSIVE_OVERVIEW.md
├── 04-AI_HANDOFF_KEY.md
├── 05-LEGACY_TIMELINE.md
├── 06-DECISION_LOG.md
├── 07-RISK_HEATMAP.md
├── 08-TEST_COVERAGE_GAP.md
├── 09-API_CONTRACT.md
├── 10-ONBOARDING_CHECKLIST.md
├── 11-CONVERSATION_LOG.md (if --chatlogs)
├── 12-DISCUSSION_SYNTHESIS.md (if --chatlogs)
├── 13-IMPLEMENTATION_STATE.md (if --chatlogs)
├── 14-PROJECT_NARRATIVE.md (if --chatlogs)
├── 15-DESIGN_HANDOFF.md (if --design-handoff)
└── diagrams/
    ├── architecture.mmd → architecture.png
    ├── function_map.mmd → function_map.png
    ├── git_timeline.mmd → git_timeline.png
    ├── dependencies.mmd → dependencies.png
    ├── cognitive_load.mmd → cognitive_load.png
    ├── risk_heatmap.mmd → risk_heatmap.png
    ├── component_hierarchy.mmd → component_hierarchy.png (if --design-handoff)
    └── user_flow.mmd → user_flow.png (if --design-handoff)

## Design Handoff Mode (--design-handoff)

When this flag is set, DeepDive analyzes the existing web application and generates:

### 15-DESIGN_HANDOFF.md Contents:

**Section 1: Visual Inventory**
- Screenshot references (user provides)
- Color palette extraction (hex codes)
- Typography scale (fonts, sizes, weights)
- Spacing system (margins, padding, gaps)
- Component inventory (buttons, forms, cards, etc.)

**Section 2: Layout Architecture**
- Page structure breakdown
- Grid system specifications
- Responsive breakpoints
- Container max-widths
- Z-index layering

**Section 3: Component Specifications**
For each UI component:
- Purpose and usage context
- Props/attributes required
- State variations (default, hover, active, disabled)
- Accessibility requirements
- Implementation notes

**Section 4: Interaction Design**
- User flows (Mermaid diagram)
- State transitions
- Animation specifications (duration, easing, transforms)
- Loading states
- Error states

**Section 5: Asset Requirements**
- Icon set specifications
- Image dimensions and formats
- Logo variants
- Favicon requirements

**Section 6: Technical Implementation Notes**
- CSS methodology (BEM, CSS-in-JS, etc.)
- Framework recommendations
- Third-party library requirements
- Performance considerations

## Rules

1. ALWAYS generate Mermaid diagrams before attempting PNG render
2. ALWAYS check for mermaid-cli before rendering
3. If mermaid-cli missing, provide install command and continue with .mmd files
4. Design handoff requires user to specify: target framework (React, Vue, vanilla, etc.)
5. Design handoff assumes existing web app - analyze HTML/CSS/JS to extract specs

## Invocation

gemini deepdive
gemini deepdive --chatlogs ./chats
gemini deepdive --design-handoff --framework react
gemini deepdive --chatlogs ./chats --design-handoff --framework vue
