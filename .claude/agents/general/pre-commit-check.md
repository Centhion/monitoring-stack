# Pre-Commit Check Agent

## Trigger

Automatically spawned when:
- User runs `/commit` command
- Claude is about to generate a commit message
- User explicitly requests a pre-commit check

---

## Agent Type

Explore

## Thoroughness

medium

---

## Prompt

Analyze all staged changes (files in git staging area) for common pre-commit issues:

### Secrets and Credentials
- API keys, tokens, passwords in code
- Private keys or certificates
- Connection strings with credentials
- Environment-specific values that should be in .env

### Debug and Development Artifacts
- console.log, print(), debugger statements
- Commented-out code blocks (more than 5 lines)
- TODO, FIXME, HACK, XXX comments that indicate incomplete work
- Temporary files or test data

### Code Quality Gates
- Syntax errors or obvious typos
- Unresolved merge conflict markers (<<<<<<, >>>>>>, ======)
- Files that appear incomplete (empty functions, placeholder text)
- Import statements for removed/non-existent modules

### File Hygiene
- Files larger than 1MB (potential binary/data file)
- Files matching patterns in .gitignore that were force-added
- Sensitive file types: .env, .pem, .key, credentials.json

Run `git diff --cached` mentally to understand what's being committed.

---

## Output

Return a structured report:

```
PRE-COMMIT CHECK RESULTS
========================

Staged Files: [count]

BLOCKING ISSUES (must fix before commit):
-----------------------------------------
[If found]
- file:line - Description
[If none]
None found.

WARNINGS (review recommended):
------------------------------
[If found]
- file:line - Description
[If none]
None found.

RECOMMENDATION:
- [PROCEED] Ready to commit
- [FIX REQUIRED] Address blocking issues first
- [REVIEW] No blockers, but warnings should be reviewed
```

Be strict about secrets and credentials - these should always block the commit. Be lenient about TODOs in feature branches.
