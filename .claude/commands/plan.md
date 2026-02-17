---
description: Enter planning mode to design implementation approach before coding.
allowed-tools:
    - Bash
    - Read
    - Write
    - Edit
    - Glob
    - Grep
    - Task
---

Execute the structured planning protocol:

## When to Use

- After `/setup` completes (natural next step)
- Before starting a new major feature
- When pivoting or changing direction
- At the start of a new project phase

## Planning Protocol

### Phase 1: Context Gathering

1. Read `docs/PROJECT_PLAN.md` to understand:
   - Project goal and scope
   - Current phase status
   - Existing tasks and progress
   - Known blockers or constraints

2. Read `ARCHITECTURE.md` (if exists) to understand:
   - Tech stack decisions
   - Design patterns in use
   - Existing structure

3. Explore the codebase to understand current state:
   - What already exists?
   - What patterns are established?
   - What dependencies are in place?

### Phase 2: User Alignment

Ask the user clarifying questions:
- "What is the priority for this planning session?"
- "Are there constraints I should know about (timeline, resources, dependencies)?"
- "Should I plan the entire project or focus on a specific phase?"

### Phase 3: Design

For each phase/feature being planned:

1. **Break down into tasks**: Concrete, actionable items
2. **Identify dependencies**: What must happen before what?
3. **Flag risks**: Technical challenges, unknowns, external dependencies
4. **Estimate complexity**: Simple / Medium / Complex for each task
5. **Define done**: What does completion look like?

### Phase 4: Propose Plan

Present the plan in a clear structure:

```
IMPLEMENTATION PLAN
===================

Phase: [Name]
Goal: [What we're achieving]

Tasks (in order):
1. [ ] [Task] - [Complexity] - [Dependencies]
2. [ ] [Task] - [Complexity] - [Dependencies]
...

Risks:
- [Risk]: [Mitigation]

Human Actions Required:
- [Action]: [Why needed]

Success Criteria:
- [How we know it's done]
```

### Phase 5: User Approval

Ask: "Does this plan look correct? Any adjustments before I update PROJECT_PLAN.md?"

### Phase 6: Commit Plan

After user approval:
1. Update `docs/PROJECT_PLAN.md` with the detailed task breakdown
2. Update phase status to "In Progress" if starting immediately
3. Add any discovered blockers or dependencies to Notes section

### Phase 7: Ready to Execute

Confirm: "Plan is saved. Ready to begin implementation? Start with [first task]?"

---

## Output Format

Be thorough but concise. Use tables and checklists for scanability. Focus on actionable items, not abstract descriptions.

## Important

- Do NOT start implementing during planning
- Do NOT skip user approval
- Do NOT make assumptions about priorities - ask
- DO update PROJECT_PLAN.md with the approved plan
