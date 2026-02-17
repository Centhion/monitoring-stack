---
name: architecture-review-skill
description: Validates architectural documentation stays current with codebase
allowed-tools:
  - Read
  - Grep
  - Glob
---

# Architecture Review Skill

Validates that ARCHITECTURE.md and README.md accurately reflect the current codebase structure, dependencies, and design decisions.

---

## When to Use

- After significant architectural changes
- Before major releases
- During `/commit` for architecture-impacting changes
- User explicitly requests architecture validation

Note: This skill is automatically invoked by the `documentation-sync` agent during commits.

---

## Validation Checklist

### 1. Tech Stack Alignment

**ARCHITECTURE.md Should Document**:
- All major dependencies in package.json/requirements.txt/go.mod
- Framework versions and justification
- Database systems in use
- External services integrated

**Validation Steps**:
1. Read ARCHITECTURE.md
2. Check package manifest files
3. Identify undocumented dependencies
4. Flag outdated version numbers

### 2. Directory Structure Accuracy

**ARCHITECTURE.md Should Show**:
```
Current directory tree matching actual structure
```

**Validation Steps**:
1. Compare documented structure to actual directories
2. Flag missing directories (new modules)
3. Flag documented directories that no longer exist
4. Verify descriptions match directory purpose

### 3. Design Patterns Documented

**ARCHITECTURE.md Should Explain**:
- Authentication/authorization approach
- State management pattern
- API design (REST, GraphQL, gRPC)
- Database access layer
- Error handling strategy
- Testing approach

**Validation Steps**:
1. Grep codebase for pattern implementation
2. Verify documentation matches actual implementation
3. Flag undocumented patterns discovered in code

### 4. Component Relationships

**ARCHITECTURE.md Should Diagram**:
- How major components interact
- Data flow between layers
- External service dependencies

**Validation Steps**:
1. Trace import statements to validate relationships
2. Check if new components are documented
3. Verify diagram accuracy

### 5. README Accuracy

**README.md Should Have**:
- Accurate feature list
- Correct setup instructions
- Valid example commands
- Updated screenshots (if applicable)

**Validation Steps**:
1. Verify feature list matches implemented capabilities
2. Check if setup instructions reference current dependencies
3. Test example commands are still valid

---

## Common Drift Patterns

### New Dependencies Not Documented

```python
# Found in code:
import redis
from celery import Celery
```

If ARCHITECTURE.md doesn't mention Redis or Celery, flag for documentation.

### Removed Components Still Documented

ARCHITECTURE.md references `/legacy-api` directory that no longer exists.

### Outdated Descriptions

```
ARCHITECTURE.md: "Uses Express.js 4.x"
package.json: "express": "^5.0.0"
```

Version mismatch indicates documentation drift.

### Missing Architectural Decisions

Code shows JWT-based auth, but ARCHITECTURE.md doesn't explain:
- Why JWT over sessions
- Token expiration strategy
- Refresh token handling

---

## Output Format

```
ARCHITECTURE REVIEW
===================

ALIGNMENT STATUS: [✓ Aligned | ⚠ Minor Drift | ✗ Significant Drift]

UNDOCUMENTED DEPENDENCIES:
- [dependency]: [detected in file]

OUTDATED DOCUMENTATION:
- [section]: [what's wrong]

MISSING ARCHITECTURAL DECISIONS:
- [pattern]: [where implemented, not documented]

REMOVED COMPONENTS STILL DOCUMENTED:
- [component]: [documented in line X]

README ACCURACY:
- [issue found]

RECOMMENDED UPDATES:
[Specific changes to make to ARCHITECTURE.md and README.md]
```

---

## Severity Guidelines

### Critical (Block Commit)
- Core architectural changes undocumented
- Setup instructions are broken
- Major dependencies missing from docs

### Warning (Review Recommended)
- Minor version drift
- New helper utilities not in structure diagram
- Feature list slightly outdated

### Informational
- Optimization details not documented
- Internal refactoring not user-facing

---

## Integration with Documentation Sync Agent

This skill provides the validation logic used by `documentation-sync` agent:

1. **Skill**: Validates current state and identifies drift
2. **Agent**: Proposes specific documentation updates
3. **User**: Reviews and approves changes

The skill focuses on WHAT is out of sync. The agent focuses on HOW to fix it.

---

## Example Usage

```
User: "Validate architecture documentation"

Claude uses architecture-review-skill:
1. Read ARCHITECTURE.md and README.md
2. Scan package manifests
3. Check directory structure
4. Grep for patterns
5. Report findings with specific line references
```

---

## Guidelines

- Be precise with file:line references
- Distinguish between critical gaps and nice-to-haves
- Acknowledge what IS documented correctly
- Provide specific recommendations, not vague suggestions
- If major drift found, recommend spawning documentation-sync agent to generate updates

---

*This skill helps maintain documentation accuracy as the codebase evolves.*
