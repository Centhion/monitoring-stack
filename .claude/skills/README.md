# Skills

Skills provide focused, automatic capabilities that enhance Claude's behavior without requiring explicit delegation. They complement the agent system by handling straightforward guidance and constraints.

---

## Skills vs. Agents: When to Use Which

### Use Skills When:
- Providing automatic guidance or constraints
- Task is straightforward and procedural
- No complex delegation or autonomous research needed
- Want behavior to feel "built-in" rather than spawned
- Tool restrictions improve safety (allowed-tools)

### Use Agents When:
- Complex, multi-step analysis required
- Need autonomous research and exploration
- Task benefits from isolated context
- Requires chaining multiple operations
- Output needs human review before proceeding

---

## Skill File Format

Each skill uses YAML frontmatter:

```markdown
---
name: skill-name
description: Brief description of what this skill does
allowed-tools:
  - Read
  - Grep
  - Glob
---

# Skill Name

Detailed instructions for how Claude should behave when this skill is active.

## Guidelines

Specific guidelines or constraints.

## Output Format

Expected output structure if applicable.
```

---

## Directory Structure

```
skills/
├── README.md                    # This file
├── code-review-skill.md         # Focused code review with read-only tools
├── commit-message-skill.md      # Generate conventional commit messages
└── architecture-review-skill.md # Validate architectural documentation
```

---

## Example: Hybrid Workflow

A typical workflow might use both:

1. **Skill**: `code-review-skill` provides automatic guidance when reviewing code (read-only)
2. **Agent**: `security-review` agent spawns for deep security analysis after auth changes (autonomous)
3. **Skill**: `commit-message-skill` formats the commit message (automatic)
4. **Agent**: `pre-commit-check` agent validates staged changes (research + validation)

Skills handle the automatic, procedural parts. Agents handle the complex, analytical parts.

---

## Tool Restrictions

Skills use `allowed-tools` to restrict which tools Claude can use, improving safety and focus:

```yaml
allowed-tools:
  - Read    # Read files
  - Grep    # Search content
  - Glob    # Find files by pattern
```

This prevents accidental modifications during review or analysis tasks.

---

## Creating Custom Skills

1. Create a new `.md` file in `.claude/skills/`
2. Add YAML frontmatter with `name`, `description`, and `allowed-tools`
3. Write clear, focused instructions
4. Keep skills simple - if it requires complex logic, use an agent instead

---

## Invocation

Skills are invoked by Claude automatically based on context, or explicitly via the Skill tool:

```
Skill(name="code-review-skill")
```

Users do not invoke skills directly - Claude decides when to use them.

---

*Skills are a modern Claude Code feature that complement the agent system. Both are valuable for different use cases.*
