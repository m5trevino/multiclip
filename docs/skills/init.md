---
name: Init
description: "# Init Skill - Project Initialization for AI Agents"
---

# Init Skill - Project Initialization for AI Agents

> **Version:** 1.0.0  
> **Purpose:** Analyze codebase and generate `AGENTS.md` for AI coding agents  
> **Pattern:** Temporary subagent isolation → Exploration → File generation → Context injection

---

## Quick Start

```bash
# Run init on current project
/init

# Or programmatically
from skills.init import run_init
result = await run_init(work_dir="/path/to/project")
```

---

## What It Does

The `init` skill analyzes your project directory and creates an `AGENTS.md` file containing:

- **Project overview** - What the project does
- **Architecture** - How it's structured
- **Tech stack** - Languages, frameworks, tools
- **Build commands** - How to run/test/build
- **Code conventions** - Style guidelines, patterns
- **Key files** - Important configuration and entry points

---

## How It Works

```
┌────────────────────────────────────────────────────────────────┐
│                      INIT PROCESS                              │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  1. CREATE TEMP SUBAGENT                                       │
│     └── Isolated context (no conversation pollution)           │
│                                                                │
│  2. RUN EXPLORATION                                            │
│     ├── Glob("*.py") → Find source files                       │
│     ├── ReadFile("README.md") → Understand project             │
│     ├── ReadFile("requirements.txt") → Tech stack              │
│     └── ... continues exploring ...                            │
│                                                                │
│  3. GENERATE AGENTS.MD                                         │
│     └── Subagent writes comprehensive documentation            │
│                                                                │
│  4. LOAD & INJECT RESULT                                       │
│     └── Read AGENTS.md and add to main conversation            │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### Why Temporary Subagent?

- **No context pollution** - Exploration tool calls don't clutter your conversation
- **Efficient** - Only the final AGENTS.md enters your context
- **Clean** - Auto-cleanup after completion

---

## Usage

### As Slash Command

```
/init
```

Analyzes current working directory and generates `AGENTS.md`.

### As Function

```python
from skills.init import run_init

# Basic usage
result = await run_init()

# Custom working directory
result = await run_init(work_dir="/path/to/project")

# Custom output file
result = await run_init(output_file="PROJECT_GUIDE.md")

# Custom prompt additions
result = await run_init(extra_instructions="Focus on API endpoints")
```

### Response Format

```python
{
    "success": True,
    "output_file": "/path/to/project/AGENTS.md",
    "content": "# Project Name\n\n...",
    "summary": "Analyzed 42 Python files, 5 config files"
}
```

---

## The Exploration Prompt

The subagent receives this prompt (customizable):

```markdown
You are a software engineering expert with many years of programming experience. 
Please explore the current project directory to understand the project's architecture 
and main details.

Task requirements:
1. Analyze the project structure and identify key configuration files
2. Understand the project's technology stack, build process and runtime architecture
3. Identify how the code is organized and main module divisions
4. Discover project-specific development conventions, testing strategies, 
   and deployment processes

After the exploration, write a thorough summary to `AGENTS.md` file.

Popular sections:
- Project overview
- Build and test commands
- Code style guidelines
- Testing instructions
- Security considerations
```

---

## Tool Usage Pattern

During exploration, the subagent typically uses:

| Tool | Purpose |
|------|---------|
| `Glob("*.py")` | Find Python files |
| `Glob("package.json")` | Find Node.js projects |
| `ReadFile("README.md")` | Read documentation |
| `ReadFile("pyproject.toml")` | Python configuration |
| `Shell("find . -type f -name '*.py' | head -20")` | Deep exploration |
| `WriteFile("AGENTS.md", ...)` | Generate output |

---

## Implementation

### Core Function

```python
async def run_init(
    work_dir: str = None,
    output_file: str = "AGENTS.md",
    extra_instructions: str = None
) -> dict:
    """
    Run init analysis on a project directory.
    
    Args:
        work_dir: Project directory to analyze (default: current)
        output_file: Output file name (default: AGENTS.md)
        extra_instructions: Additional prompt instructions
    
    Returns:
        dict with success status, output file path, content, and summary
    """
    import tempfile
    from pathlib import Path
    
    # 1. Determine working directory
    work_dir = Path(work_dir or os.getcwd()).resolve()
    
    # 2. Create temporary subagent for isolated exploration
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create subagent with isolated context
        subagent = Agent(
            name="init-explorer",
            context=IsolatedContext(temp_dir),
            tools=[Glob, ReadFile, WriteFile, Shell]
        )
        
        # 3. Build exploration prompt
        prompt = build_init_prompt(
            work_dir=work_dir,
            output_file=output_file,
            extra_instructions=extra_instructions
        )
        
        # 4. Run exploration
        await subagent.run(prompt)
        
    # 5. Load results (subagent auto-cleaned up)
    output_path = work_dir / output_file
    content = output_path.read_text() if output_path.exists() else ""
    
    # 6. Return result
    return {
        "success": output_path.exists(),
        "output_file": str(output_path),
        "content": content,
        "summary": extract_summary(content)
    }
```

### Context Injection

After running init, inject the result into the main conversation:

```python
# Create system message with AGENTS.md content
system_message = system(
    f"The user just ran `/init` command. "
    f"The system has analyzed the codebase and generated an `AGENTS.md` file. "
    f"Latest AGENTS.md file content:\n{result['content']}"
)

# Inject as user message (appears as context you provided)
await context.append_message(
    Message(role="user", content=[system_message])
)
```

---

## Customization

### Change What Gets Analyzed

Edit the exploration prompt:

```python
prompt = """
You are analyzing a Python project.

Additional focus areas:
- API endpoint documentation
- Database schema analysis
- Security audit
- Performance bottlenecks

Write findings to API_GUIDE.md
"""
```

### Change Output Format

```python
result = await run_init(
    output_file="ARCHITECTURE.md",
    extra_instructions="""
    Format:
    # Architecture Overview
    ## System Diagram
    ## Component Index
    ## Data Flow
    """
)
```

### Post-Processing

```python
result = await run_init()

# Custom processing
if result["success"]:
    summary = generate_summary(result["content"])
    await write_summary_file(summary)
```

---

## File Structure

```
skills_master_vault/init/
├── SKILL.md           # This documentation
├── __init__.py        # Package exports
├── init.py            # Core implementation
└── prompts/
    ├── __init__.py    # Prompt loader
    └── init.md        # Default exploration prompt
```

---

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| AGENTS.md not created | Subagent didn't call WriteFile | Re-run `/init` |
| Empty AGENTS.md | Project has no recognizable structure | Check working directory |
| Wrong analysis | Prompt not specific enough | Use `extra_instructions` |
| Missing key info | Subagent didn't explore deep enough | Add specific instructions |

---

## Extension Ideas

```python
# /analyze-tests - Test coverage analysis
async def analyze_tests(work_dir):
    return await run_init(
        output_file="TEST_COVERAGE.md",
        extra_instructions="Analyze test files and coverage"
    )

# /security-audit - Security analysis
async def security_audit(work_dir):
    return await run_init(
        output_file="SECURITY.md",
        extra_instructions="Audit for security vulnerabilities"
    )

# /api-docs - API documentation
async def api_docs(work_dir):
    return await run_init(
        output_file="API.md",
        extra_instructions="Document all API endpoints"
    )
```

---

## Dependencies

- `tempfile` - For temporary directory
- `pathlib` - For file operations
- `Agent` - Subagent for isolated exploration
- `Glob`, `ReadFile`, `WriteFile`, `Shell` - Exploration tools

---

## Related

- `/compact` - Similar pattern for context compaction
- `/plan` - Enter plan mode for structured implementation
- `/clear` - Clear conversation context

---

**END OF DOCUMENTATION**