# Sub-Agent System

This directory contains prompt templates for autonomous sub-agents that Claude spawns to handle specialized tasks. Sub-agents work invisibly - you communicate with the main Claude agent, which delegates to sub-agents as needed.

---

## How It Works

```
You (human)
    |
    v
Claude (main agent) <--- You only talk to this one
    |
    |---> Sub-agent A (works autonomously, returns result)
    |---> Sub-agent B (works autonomously, returns result)
    |---> Sub-agent C (works autonomously, returns result)
    |
    v
Claude synthesizes results, reports back to you
```

Sub-agents are spawned automatically based on workflow triggers defined in `CLAUDE.md`. You do not need to request them explicitly.

---

## Directory Structure

```
agents/
├── README.md              # This file
├── general/               # Universal agents (ship with template)
│   ├── security-review.md
│   ├── pre-commit-check.md
│   ├── dependency-audit.md
│   ├── code-quality.md
│   ├── changelog-tracker.md
│   └── documentation-sync.md
└── project/               # Project-specific agents (created during /setup)
    └── .gitkeep
```

---

## Agent Types

Claude Code provides these sub-agent types:

| Type | Use Case | Speed |
|------|----------|-------|
| `Explore` | Codebase discovery, file searches, pattern matching | Fast |
| `Plan` | Architecture design, implementation planning | Medium |
| `general-purpose` | Complex multi-step autonomous tasks | Slower |

---

## Agent File Format

Each agent file follows this structure:

```markdown
# Agent Name

## Trigger
When this agent should be automatically spawned.

## Agent Type
Which sub-agent type to use (Explore, Plan, general-purpose).

## Thoroughness
For Explore agents: quick, medium, or thorough.

## Prompt
The instructions passed to the sub-agent.

## Output
What the agent should return.
```

---

## General vs. Project Agents

### General Agents (`general/`)
- Ship with the template
- Apply to any project regardless of tech stack
- Focus on universal concerns: security, quality, dependencies, tracking, documentation

### Project Agents (`project/`)
- Created during `/setup` based on chosen tech stack
- Tailored to specific frameworks and patterns
- Examples: React component analyzer, API endpoint validator, SQL query optimizer

### Recommendation Patterns (No Agent File)

Some behaviors in `CLAUDE.md` are recommendation patterns rather than triggered agents:

- **Codebase Exploration**: When asked about code structure or "how does X work", Claude should prefer spawning an Explore agent over manual grep/glob commands. This is a behavioral guideline, not a triggered workflow with a dedicated agent file.

---

## Creating Project Agents

During `/setup`, Claude will recommend project-specific agents based on your tech stack. You can also create agents manually:

1. Create a new `.md` file in `agents/project/`
2. Follow the agent file format above
3. Add a workflow trigger in `CLAUDE.md` under "Agent Workflows"

### Example: React Component Agent

```markdown
# Component Analyzer

## Trigger
After creating or significantly modifying React components.

## Agent Type
Explore

## Thoroughness
medium

## Prompt
Analyze the modified React component for:
- Proper hook usage (dependencies, order)
- Props interface completeness
- Missing error boundaries
- Performance concerns (unnecessary re-renders)

Report findings with file:line references.

## Output
Structured summary of findings or confirmation of clean patterns.
```

---

## Parallel Execution

Multiple sub-agents can run simultaneously when their tasks are independent. For example, the pre-commit workflow spawns security and quality agents in parallel, reducing wait time.

---

## Overhead

Sub-agents add no communication overhead for you. Claude manages all delegation internally. The only visible difference is more thorough analysis in Claude's responses.

---

## Integrated Review Flow

The `changelog-tracker` and `documentation-sync` agents work together during `/commit` to maintain project documentation automatically.

### Tiered Confidence Model

**Auto-apply (no approval needed)**:
- Marking verifiable tasks complete
- Adding notes and observations
- Recording blockers and decisions

**Staged for review (approval required)**:
- Marking phases complete
- Adding/removing tasks
- All README.md and ARCHITECTURE.md changes

### Example Flow

```
/commit triggers:
1. pre-commit-check  --> Scans for secrets, debug code
2. changelog-tracker --> Updates PROJECT_PLAN.md (auto + staged)
3. documentation-sync --> Proposes doc updates (all staged)

User sees:
- Auto-applied changes (informational)
- Pending changes (approve/reject)
- Then commit proceeds
```

This ensures documentation stays current without requiring you to remember separate review steps.
