---
name: code-review-skill
description: Provides focused code review guidance with read-only access
allowed-tools:
  - Read
  - Grep
  - Glob
---

# Code Review Skill

Provides systematic code review capabilities with safety constraints (read-only access). This skill enhances Claude's code review behavior with structured analysis while preventing accidental modifications.

---

## When to Use

- User asks for code review of specific files or directories
- Reviewing pull request changes
- Analyzing code quality before refactoring
- Understanding unfamiliar code sections

Do NOT use for security-focused reviews - delegate to `security-review` agent instead.

---

## Review Methodology

### 1. Code Quality

- **Readability**: Are variable/function names clear and descriptive?
- **Complexity**: Are functions too long or deeply nested?
- **Dead Code**: Unused imports, variables, or functions?
- **Comments**: Are complex sections explained? Are comments accurate and necessary?

### 2. Best Practices

- **Error Handling**: Proper try/catch blocks and error messages?
- **Edge Cases**: Null checks, boundary conditions handled?
- **DRY Principle**: Repeated logic that could be extracted?
- **SOLID Principles**: Single responsibility, proper abstraction?

### 3. Language-Specific Patterns

**Python**:
- PEP 8 compliance
- Type hints present
- Context managers for resources
- List comprehensions vs loops appropriateness

**JavaScript/TypeScript**:
- Consistent async/await vs promises
- Proper TypeScript types (no `any` abuse)
- React hooks dependencies correct
- Modern ES6+ patterns

**Go**:
- Proper error handling (not ignoring errors)
- Interface usage appropriate
- Defer statements for cleanup
- Context usage for cancellation

### 4. Testing Gaps

- Are there unit tests for new logic?
- Are edge cases tested?
- Test descriptions clear and meaningful?

---

## Output Format

Provide feedback in this structure:

```
CODE REVIEW FINDINGS
====================

Files Reviewed: [list]

CRITICAL ISSUES:
- file:line - [Description and suggested fix]

IMPROVEMENTS:
- file:line - [Suggestion with rationale]

POSITIVE PATTERNS:
- [What's done well]

OVERALL ASSESSMENT:
[1-2 sentence summary]
```

---

## Constraints

- Read-only access (no Write, Edit, or Bash tools)
- Focus on constructive feedback with specific line references
- Prioritize critical issues over stylistic preferences
- Acknowledge good patterns, not just problems
- If security concerns found, recommend spawning security-review agent

---

## Example Usage

```
User: "Review the authentication logic in src/auth.py"

Claude uses code-review-skill:
1. Read src/auth.py
2. Analyze against methodology
3. Provide structured feedback
4. If security issues found: "I recommend spawning the security-review agent..."
```

---

*This skill complements agents by providing lightweight, automatic review guidance.*
