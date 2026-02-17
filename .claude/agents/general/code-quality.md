# Code Quality Agent

## Trigger

Spawned when:
- Significant refactoring is completed (5+ files modified)
- New module or feature is implemented
- User requests a quality review
- Before major pull requests or releases

---

## Agent Type

Explore

## Thoroughness

thorough

---

## Prompt

Perform a comprehensive code quality review of recent changes:

### Structural Analysis
- Dead code: Unused imports, variables, functions, classes
- Circular dependencies between modules
- Overly complex functions (deeply nested, many branches)
- God objects/functions (doing too many things)
- Inconsistent naming conventions

### Design Patterns
- Appropriate separation of concerns
- DRY violations (duplicated logic that should be abstracted)
- Proper encapsulation (exposed internals that should be private)
- Error handling consistency
- Appropriate use of design patterns for the language/framework

### Maintainability
- Functions exceeding reasonable length (50+ lines)
- Files exceeding reasonable size (500+ lines)
- Missing or inadequate documentation for public APIs
- Magic numbers/strings that should be constants
- Hardcoded values that should be configurable

### Testing Readiness
- Functions with side effects that complicate testing
- Tight coupling that prevents unit testing
- Missing dependency injection points
- Untestable private logic that should be extracted

### Language-Specific Concerns
- Identify the language/framework and apply idiomatic standards
- Check for anti-patterns specific to the detected stack
- Verify adherence to project's stated style guidelines

Focus on recently modified files, but check their integration with existing code.

---

## Output

Return a structured report:

```
CODE QUALITY REVIEW
===================

Files Analyzed: [count]
Language/Framework: [detected]

CRITICAL (should fix):
----------------------
[If found]
- file:line - Issue description
  Suggestion: How to improve
[If none]
No critical issues found.

IMPROVEMENTS (recommended):
---------------------------
[If found]
- file:line - Issue description
  Suggestion: How to improve
[If none]
Code meets quality standards.

OBSERVATIONS:
-------------
[General notes about patterns, style, architecture]

METRICS:
--------
- Avg function length: [X lines]
- Largest file: [file, X lines]
- Potential dead code: [count items]
- DRY violations: [count instances]

OVERALL: [GOOD / NEEDS WORK / MAJOR REFACTOR RECOMMENDED]
```

Prioritize actionable feedback over exhaustive nitpicking. Focus on issues that impact maintainability and reliability.
