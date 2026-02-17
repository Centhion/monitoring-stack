---
description: Generate session summary for continuity across sessions.
allowed-tools:
    - Bash
    - Read
    - Write
    - Edit
    - Glob
    - Grep
    - Task
---

Execute the session handoff protocol to preserve context for future sessions.

## When to Use

- End of a work session
- Before stepping away from the project for a while
- When handing off to another person
- After completing a significant milestone

## Handoff Protocol

### Phase 1: Gather Session Context

1. Review recent activity:
   - Files created or modified this session
   - Git status (staged, unstaged, committed)
   - Todo list state

2. Read `docs/PROJECT_PLAN.md`:
   - Current phase status
   - Task progress
   - Recent notes added

3. Review conversation history for:
   - Decisions made
   - Blockers encountered
   - Important context discussed

### Phase 2: Generate Summary

Create a structured summary covering:

**COMPLETED THIS SESSION**
- What was finished? (Be specific: files, features, fixes)

**IN PROGRESS (not finished)**
- What was started but not completed?
- Current state of incomplete work
- Why it's incomplete (blocked, ran out of time, needs input)

**BLOCKERS**
- External dependencies (waiting on someone/something)
- Technical challenges unresolved
- Decisions pending

**DECISIONS MADE**
- Architectural choices
- Trade-offs accepted
- Approaches selected (with rationale)

**NEXT SESSION SHOULD**
- Priority tasks to continue
- Order of operations
- Any setup needed

**IMPORTANT CONTEXT**
- Non-obvious information that would be lost
- Relationships between components
- Gotchas or warnings for future self

### Phase 3: Save to Session Log

Append the summary to `docs/SESSION_LOG.md` with timestamp.

Format:
```markdown
---

## Session: YYYY-MM-DD HH:MM

### Completed
- [item]

### In Progress
- [item]: [status/notes]

### Blockers
- [blocker]: [what's needed]

### Decisions
- [decision]: [rationale]

### Next Session
1. [priority task]
2. [task]

### Context
- [important note]

---
```

### Phase 4: Update PROJECT_PLAN.md

Ensure PROJECT_PLAN.md reflects:
- Any tasks completed (checked off)
- Any new tasks discovered
- Current blockers in Notes section
- Phase status is accurate

### Phase 5: Confirm

Report to user:
```
Session summary saved to docs/SESSION_LOG.md

Key points for next session:
- [top 3 priorities]

PROJECT_PLAN.md updated: [yes/no changes needed]

Ready to end session.
```

---

## Important

- Be thorough - context loss is expensive
- Be specific - vague notes are useless later
- Include the "why" not just the "what"
- Do NOT skip the PROJECT_PLAN.md update
- This command should be the LAST thing run in a session
