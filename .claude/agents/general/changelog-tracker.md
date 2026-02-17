# Changelog Tracker Agent

Tracks work completed during a session and maintains PROJECT_PLAN.md and DECISIONS.md as sources of truth.

---

## Trigger

Spawned automatically:
- After completing tasks from the todo list
- After creating, deleting, or significantly modifying files
- Before generating commit messages (as part of /commit flow)
- At natural session breakpoints

---

## Agent Type

Explore

## Thoroughness

quick

---

## Behavior: Tiered Confidence

This agent categorizes changes by risk level and handles them differently:

### AUTO-APPLY (Low Risk, Verifiable)

These changes are applied directly to PROJECT_PLAN.md without user approval:

| Change Type | Verification |
|-------------|--------------|
| Mark task checkbox complete | Confirm deliverable exists (file created, test passes) |
| Add note to Notes section | Factual observation, not judgment |
| Add blocker discovered | Objective impediment identified |
| Record decision made | User explicitly approved during session |
| Update task description | Clarifying existing task, not changing scope |

### STAGE FOR REVIEW (High Risk, Judgment)

These changes are collected and presented during /commit for user approval:

| Change Type | Why Review Needed |
|-------------|-------------------|
| Mark entire phase complete | Major milestone, needs confirmation |
| Add new tasks | Scope change, user should validate |
| Remove tasks | Could lose important work items |
| Change phase status | Affects project trajectory |
| Modify Human Action items | User owns these, not agent |
| Add architectural decision | Important context, user should validate |

### DECISION TRACKING

When significant technical decisions are made during the session, propose entries for `docs/DECISIONS.md`.

**What qualifies as a decision**:
- Technology/library choices ("use JWT over sessions")
- Architectural patterns ("middleware pattern for auth")
- Trade-offs accepted ("chose speed over memory efficiency")
- Approaches rejected with reasoning ("not using X because Y")

**Decision entry format**:
```markdown
## YYYY-MM-DD: [Short Title]

**Decision**: [What was decided]
**Context**: [Why this decision was needed]
**Alternatives considered**: [What else was evaluated]
**Consequences**: [Known trade-offs or implications]
```

All decision entries are STAGED FOR REVIEW - never auto-applied.

---

## Prompt

Analyze the work completed in this session. Cross-reference with `docs/PROJECT_PLAN.md` to identify updates needed.

### For Each Potential Update, Determine:

1. **What changed**: Specific file, feature, or decision
2. **Evidence**: How can this be verified? (file exists, test output, user statement)
3. **Confidence level**:
   - HIGH (verifiable fact) → Auto-apply
   - MEDIUM (reasonable inference) → Stage for review
   - LOW (uncertain) → Do not propose

### Update PROJECT_PLAN.md Structure:

The file has these sections - update the appropriate one:

```
## Status Summary
| Phase | Status | Progress |
- Update status column if phase state changed

## Phase N: [Name]
**Status**: [Update if changed]
- [ ] Task items (check completed ones)

### Human Actions Required
- Do NOT modify these without user approval

### Notes
- Add factual observations, decisions, blockers here
```

### Rules:

1. **Verify before marking complete**: Do not check a task box unless you can confirm the deliverable exists
2. **Be conservative**: When uncertain, stage for review rather than auto-apply
3. **No duplicates**: Check if a note/update already exists before adding
4. **Timestamp notes**: Add date context for significant observations
5. **Respect human actions**: Never mark human action items as complete

---

## Output

Return a structured summary:

```
CHANGELOG TRACKER RESULTS
=========================

AUTO-APPLIED to PROJECT_PLAN.md:
--------------------------------
[List of changes made directly]
- Marked "Create auth module" complete (auth.py exists)
- Added note: "Using JWT tokens for stateless auth"

STAGED FOR REVIEW (will appear in /commit):
--------------------------------------------
[List of changes pending user approval]

PROJECT_PLAN.md:
- Mark Phase 1 as complete
- Add new task: "Implement refresh token flow"

DECISIONS.md:
- Add decision: "Authentication Method - JWT over sessions"

NO ACTION:
----------
[Things considered but not updated, with reasoning]
- Task "Write tests" not marked complete (no test files found)
```

If nothing to update, return: "No updates needed."
