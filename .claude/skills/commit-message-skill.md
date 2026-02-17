---
name: commit-message-skill
description: Generates conventional commit messages following best practices
allowed-tools:
  - Read
  - Bash
---

# Commit Message Skill

Provides automatic guidance for generating conventional commit messages that are clear, consistent, and follow the project's established patterns.

---

## When to Use

- During `/commit` workflow
- User asks to generate a commit message
- Creating pull request descriptions

Note: The `/commit` command already integrates this guidance, so manual invocation is rarely needed.

---

## Conventional Commits Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type (Required)

| Type | Use Case |
|------|----------|
| `feat` | New feature or capability |
| `fix` | Bug fix |
| `docs` | Documentation only changes |
| `style` | Code style changes (formatting, no logic change) |
| `refactor` | Code refactoring (no behavior change) |
| `perf` | Performance improvement |
| `test` | Adding or updating tests |
| `chore` | Build process, tooling, dependencies |
| `ci` | CI/CD configuration changes |
| `revert` | Reverting a previous commit |

### Scope (Optional)

The scope specifies what part of the codebase is affected:

- `auth` - Authentication system
- `api` - API endpoints
- `ui` - User interface
- `db` - Database layer
- `docs` - Documentation
- Component/module name for specific areas

### Subject (Required)

- Use imperative mood: "add feature" not "added feature"
- Lowercase first letter
- No period at end
- Maximum 50 characters
- Focus on WHY not WHAT (code shows what)

### Body (Optional)

- Explain motivation for change
- Contrast with previous behavior
- Wrap at 72 characters

### Footer (Optional)

- Breaking changes: `BREAKING CHANGE: <description>`
- Issue references: `Fixes #123`, `Closes #456`
- Co-authors: `Co-authored-by: Name <email>`

---

## Examples

### Good Commit Messages

```
feat(auth): add OAuth2 token refresh mechanism

Implements automatic token refresh to prevent session expiration.
Tokens are refreshed 5 minutes before expiry using refresh tokens
stored in httpOnly cookies.

Fixes #234
```

```
fix(api): handle null values in user profile response

Previously crashed when optional fields were null. Now safely
defaults to empty string for display.
```

```
docs: update SSH authentication guide for 1Password

Clarifies that users should use existing SSH keys from 1Password
rather than generating new ones.
```

```
refactor(db): extract query builder into separate module

Improves testability and reusability of query construction logic.
No behavior changes.
```

### Bad Commit Messages

```
update stuff
```
(Too vague, no type, no context)

```
Fixed bug
```
(What bug? Where? Why did it happen?)

```
feat: Added new feature that allows users to do X and also fixed Y and updated Z
```
(Multiple changes in one commit, too long)

---

## Workflow Integration

This skill is automatically applied during `/commit` workflow:

1. Analyze staged changes (`git diff --cached`)
2. Review recent commits for style consistency (`git log`)
3. Identify type and scope from changes
4. Generate subject line focused on WHY
5. Add body if changes need explanation
6. Include footer for breaking changes or issue refs

---

## Guidelines

### DO:
- Keep commits atomic (one logical change)
- Write subject lines that complete: "This commit will..."
- Explain WHY in body, not WHAT (code shows what)
- Reference issues when applicable
- Follow project's established patterns

### DON'T:
- Mix unrelated changes in one commit
- Write vague subjects like "updates" or "changes"
- Include implementation details in subject
- Use past tense ("added" instead of "add")
- Exceed character limits

---

## Scope Detection

Automatically detect scope from file paths:

| File Pattern | Scope |
|-------------|-------|
| `**/auth/**` | auth |
| `**/api/**` | api |
| `**/components/**` | ui |
| `**/db/**`, `**/models/**` | db |
| `**/docs/**`, `*.md` | docs |
| `**/test/**`, `*.test.*` | test |

If multiple scopes affected, use the most significant one or omit scope.

---

## Breaking Changes

Detect breaking changes from:
- Removed public functions/methods
- Changed function signatures
- Removed configuration options
- Modified API response structures

Always include `BREAKING CHANGE:` in footer with migration guidance.

---

## Output

Generate commit message and present to user:

```
PROPOSED COMMIT MESSAGE:
------------------------
[Generated message]

REASONING:
- Type: [Why this type]
- Scope: [Why this scope]
- Subject: [What it accomplishes]

Approve? [Y/n]
```

---

*This skill ensures consistent, high-quality commit messages across the project.*
