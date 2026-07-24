---
name: Init Pinpoint
description: "# Deep Dive Documentation Skill"
---

# Deep Dive Documentation Skill

> **Version:** 1.0  
> **Purpose:** Create comprehensive technical documentation from chat conversation history, with user quotes, architecture diagrams, and implementation details.

## Overview

This skill creates detailed technical documentation for any specific function, feature, or system component of your application. Unlike the standard `init` flow which creates a general AGENTS.md, this skill dives deep into one specific area with:

- Full conversation context (user quotes)
- Architecture diagrams
- Technical implementation details
- File structures
- Step-by-step flows
- Current status and issues
- Troubleshooting guides

## When to Use

Use this skill when:
- You've just built a complex feature and want it documented
- You need to onboard someone to a specific system component
- You want to capture decision-making context from chat
- The standard AGENTS.md isn't detailed enough for a specific function
- You need to reference how something works months later

## Workflow

### Step 1: Identify the Target

Determine what specific function/feature you want documented:
- API endpoint system
- Authentication flow
- Database architecture
- Third-party integrations
- Deployment pipeline
- WebSocket handling
- File upload system
- etc.

### Step 2: Run Deep Dive

Activate this skill by saying something like:

> "Deep dive document the [feature name] system we just built"

> "Create comprehensive docs for how [function] works"

> "Document the [component] architecture with all our chat context"

### Step 3: Skill Execution

The skill will:

1. **Analyze the conversation history** to extract:
   - User requirements and quotes
   - Decision points
   - Technical choices made
   - Files created/modified

2. **Create documentation** including:
   - Problem statement
   - User requirements (with quotes)
   - Architecture diagrams (ASCII)
   - Technical implementation
   - File structure
   - Step-by-step flows
   - Current status
   - Troubleshooting

3. **Save to file** at:
   ```
   [project-root]/docs/deep-dives/[feature-name].md
   ```

## Output Format

The generated documentation follows this structure:

```markdown
# [Feature Name] - Deep Dive Documentation

> Version: 1.0
> Created: [date]
> Status: [working/needs-fix/in-progress]

## 1. The Problem
[What problem this feature solves]

## 2. User Requirements (with quotes)
> **User:** "[actual quote from conversation]"

[Explanation of what this means]

## 3. Architecture
[ASCII diagram showing components and data flow]

## 4. Technical Implementation
[Code snippets, file locations, key functions]

## 5. File Structure
[Tree view of relevant files]

## 6. How It Works - Step by Step
[Numbered flow from trigger to completion]

## 7. Decision Points
[Key choices made during development]

## 8. Current Status
[What's working, what's broken, known issues]

## 9. Troubleshooting
[Common issues and fixes]
```

## Example Usage

### Example 1: API Endpoint System

**User:** "Deep dive document our /v1/chat API system"

**Skill Output:** `docs/deep-dives/api-chat-endpoint.md`

Contains:
- Request/response formats
- Authentication flow
- Rate limiting implementation
- Error handling
- Streaming vs non-streaming
- User quotes about requirements

### Example 2: Ngrok Redirect System

**User:** "Document the ngrok tunnel redirect system with all our chat context"

**Skill Output:** `docs/deep-dives/ngrok-redirect-system.md`

Contains:
- Why dynamic URLs are a problem
- How the redirect HTML works
- The automation script flow
- File locations
- URLs and access points
- User's original vision quotes

### Example 3: Database Layer

**User:** "Create comprehensive docs for our database architecture"

**Skill Output:** `docs/deep-dives/database-architecture.md`

Contains:
- Schema design decisions
- Migration strategy
- Query patterns
- Connection pooling
- User requirements about scale

## Best Practices

### 1. Be Specific

Good: *"Deep dive the Stripe payment webhook handler"*

Too broad: *"Document the app"* (use standard init instead)

### 2. Reference Recent Work

This skill works best when the conversation about the feature is fresh. It analyzes chat history to extract context.

### 3. Review Generated Docs

After generation, review the document and ask for additions:

> "Add more detail about the error handling in section 4"

> "Include the API endpoint table in the architecture section"

### 4. Keep Updated

When the feature changes, run the skill again:

> "Update the ngrok redirect docs with the new token rotation logic"

## Integration with Standard Init

This skill complements (not replaces) the standard `init` flow:

- **Standard init:** Creates general AGENTS.md for the whole project
- **Deep dive:** Creates detailed docs for specific features

Typical workflow:
1. Run standard init for general project docs
2. Run deep dive for each major feature
3. Result: AGENTS.md + docs/deep-dives/*.md

## File Locations

By default, saves to:
```
[project-root]/
├── AGENTS.md              (standard init output)
├── docs/
│   └── deep-dives/
│       ├── feature-one.md
│       ├── feature-two.md
│       └── ngrok-redirect-system.md
```

## Customization

You can customize the output by requesting specific sections:

> "Deep dive the auth system but focus on the JWT implementation"

> "Document the deployment pipeline with extra focus on rollback procedures"

> "Create docs for the WebSocket system including all my quotes about real-time requirements"

## Benefits

1. **Preserves Context:** Captures why decisions were made, not just what was built
2. **User Quotes:** Shows original requirements in user's own words
3. **Technical + Human:** Combines code details with conversation history
4. **Searchable:** Markdown files easy to search and reference
5. **Onboarding:** New team members can understand complex features quickly

## Limitations

- Requires recent chat history about the feature
- Best for completed or mostly-completed features
- Not a replacement for code comments or API docs
- One feature per document (not entire systems)

## Example Output Structure

See the ngrok redirect documentation we just created for a real-world example of this skill's output format.

---

**END OF SKILL DOCUMENTATION**