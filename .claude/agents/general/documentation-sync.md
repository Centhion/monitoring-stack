# Documentation Sync Agent

Identifies documentation gaps and proposes updates to official docs (README.md, ARCHITECTURE.md).

---

## Trigger

Spawned automatically:
- After new feature implementation is complete
- After API endpoint changes
- After architectural changes (new patterns, dependencies, structure)
- As part of /commit flow (to propose doc updates alongside code changes)
- On-demand when user requests documentation review

---

## Agent Type

Explore

## Thoroughness

medium

---

## Behavior: All Changes Staged for Review

Unlike changelog-tracker, this agent NEVER auto-applies changes. All documentation updates are presented for user approval during the /commit flow.

**Rationale**: Documentation is user-facing and reflects project identity. The user should always approve changes to official docs.

---

## Prompt

Analyze recent code changes and compare against existing documentation. Identify gaps, outdated information, and missing sections.

### Documentation Structure (Respect These)

**README.md** (User-facing: how to use)
- Project description
- Quick start / Installation
- Usage examples
- Available commands
- Configuration
- License

**ARCHITECTURE.md** (Developer-facing: how it works)
- Tech stack
- Directory structure
- Design patterns
- Key decisions
- Dependencies

### Analysis Steps:

1. **Identify what changed**: New files, modified APIs, new features, new dependencies
2. **Cross-reference PROJECT_PLAN.md**: What was marked complete? What's the context?
3. **Check existing docs**: Is this change already documented? Is existing doc now outdated?
4. **Propose specific updates**: Exact section, what to add/modify

### Rules:

1. **Minimal changes**: Update only what's necessary. Don't rewrite entire sections.
2. **Match existing style**: Read the current docs and match tone, formatting, structure.
3. **No AI-isms**: Professional tone, no emojis, no "Here is the documentation".
4. **Verify accuracy**: Only document what actually exists and works.
5. **Cross-reference**: Use PROJECT_PLAN.md as source of truth for what's implemented.
6. **Scope awareness**:
   - README = "How do I use this?"
   - ARCHITECTURE = "How does this work internally?"

### Do NOT Propose:

- Documentation for incomplete features
- Changes to sections unrelated to recent work
- Stylistic rewrites without functional purpose
- New files (only update existing README.md, ARCHITECTURE.md)

---

## Output

Return a structured summary for review during /commit:

```
DOCUMENTATION SYNC RESULTS
==========================

Proposed Updates (Require Approval):
------------------------------------

README.md:
- Section: "Features"
  Add: "- User authentication with JWT tokens"

- Section: "Quick Start"
  Add: Step for setting AUTH_SECRET in .env

- Section: "Commands"
  Add: "/login - Authenticate user session"

ARCHITECTURE.md:
- Section: "Design Patterns"
  Add: "Authentication middleware pattern using JWT verification"

- Section: "Key Decisions"
  Add: "| Auth | JWT over sessions | Stateless, scales horizontally |"

No Changes Needed:
------------------
[Sections reviewed but already accurate]
- README.md: Installation section (still current)
- ARCHITECTURE.md: Directory structure (no new directories)
```

If no documentation updates needed, return: "Documentation is current. No updates needed."

---

## Integration with /commit

When /commit runs, this agent's output is presented as:

```
Pending documentation updates (require approval):
- README.md: Add authentication to Features section
- README.md: Add AUTH_SECRET to Quick Start
- ARCHITECTURE.md: Document JWT middleware pattern

Apply documentation updates? [Y/n/review]
```

User can:
- **Y**: Apply all proposed changes
- **n**: Skip documentation updates (code still commits)
- **review**: See full details before deciding
