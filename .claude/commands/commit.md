---
description: Generate a Conventional Commit message for staged changes.
allowed-tools:
    - Bash
    - Read
    - Edit
    - Write
    - Task
---

Execute the integrated commit workflow:

CRITICAL: Do NOT execute `git commit` until the user has reviewed and approved all pending changes in step 6. The commit happens ONLY in step 7, after explicit user approval.

1. Run the smart commit helper to analyze staged changes:
   !python3 skills/git_smart_commit.py

2. Spawn the pre-commit-check agent to scan for issues (secrets, debug code, TODOs).

3. Spawn the changelog-tracker agent to:
   - Auto-apply low-risk PROJECT_PLAN.md updates
   - Stage high-risk changes for user approval

4. Run the documentation sync check:
   !python3 skills/doc_sync_check.py

   This auto-detects project type and checks:
   - New services/modules not in ARCHITECTURE.md
   - New screens/routes not in ARCHITECTURE.md
   - New dependencies not in ARCHITECTURE.md

   If issues found, prompt user: "Update docs before commit? (y/skip)"
   - If yes: Update README.md and/or ARCHITECTURE.md as needed
   - If skip: Proceed without doc updates (for non-impactful changes)

5. Present the integrated review to the user:
   - Code changes summary
   - Auto-applied PROJECT_PLAN.md updates
   - Documentation sync findings
   - Pending changes requiring approval

6. After user approval, execute the commit using the Python script:
   - Run: python3 skills/git_smart_commit.py commit-and-push "Your commit message here"
   - This bypasses the Bash deny rule via subprocess (by design)
   - DO NOT run git commit directly via Bash (blocked by settings.json deny rule)

See "Integrated Review Flow" section in CLAUDE.md for the expected output format.
