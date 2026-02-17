# Golden Template Testing Checklist

> Use this checklist to validate template functionality after cloning to a new project.

---

## Pre-Flight Checks

- [ ] Clone template to test location
- [ ] Verify `.claude/` directory structure intact
- [ ] Verify `_rename_to_*.md` files exist
- [ ] Check `.gitignore` excludes sensitive files

---

## Skills Validation

### 1. Skills Files Present
- [ ] `.claude/skills/README.md` exists
- [ ] `.claude/skills/code-review-skill.md` exists
- [ ] `.claude/skills/commit-message-skill.md` exists
- [ ] `.claude/skills/architecture-review-skill.md` exists

### 2. YAML Frontmatter Valid
Run for each skill file:
```bash
head -n 10 .claude/skills/code-review-skill.md
```
- [ ] Opens with `---`
- [ ] Contains `name:` field
- [ ] Contains `description:` field
- [ ] Contains `allowed-tools:` list
- [ ] Closes with `---`

### 3. Skills Invocation (Manual Test)
Start Claude Code session and test:
```
Ask Claude: "Can you review the code in .claude/CLAUDE.md using the code-review skill?"
```
- [ ] Claude mentions using code-review-skill
- [ ] Review is read-only (no edits made)
- [ ] Output follows structured format

---

## Agents Validation

### 1. Agent Files Present
- [ ] `.claude/agents/README.md` exists
- [ ] `.claude/agents/general/pre-commit-check.md` exists
- [ ] `.claude/agents/general/security-review.md` exists
- [ ] `.claude/agents/general/code-quality.md` exists
- [ ] `.claude/agents/general/dependency-audit.md` exists
- [ ] `.claude/agents/general/changelog-tracker.md` exists
- [ ] `.claude/agents/general/documentation-sync.md` exists

### 2. Agent Trigger Test
Make a small change to auth-related file:
```bash
mkdir -p src/auth
echo "// Test auth file" > src/auth/test.py
git add src/auth/test.py
```
- [ ] Security-review agent auto-spawns
- [ ] Agent returns structured findings

---

## Configuration Validation

### 1. Settings JSON Valid
```bash
python3 -m json.tool .claude/settings.json > /dev/null && echo "Valid JSON"
```
- [ ] Returns "Valid JSON"

### 2. Extended Thinking Enabled
```bash
grep -A1 '"alwaysThinkingEnabled"' .claude/settings.json
```
- [ ] Shows `"alwaysThinkingEnabled": true`

### 3. Permissions Deny List
```bash
grep -A10 '"deny"' .claude/settings.json
```
- [ ] Blocks `Bash(git commit:*)`
- [ ] Blocks reading `.env` files
- [ ] Blocks reading secrets directories

---

## Workflow Tests

### 1. Status Command
```bash
# In Claude Code session
/status
```
- [ ] Shows git status
- [ ] Shows current branch
- [ ] Shows task summary (if any)

### 2. Commit Workflow
```bash
# Make a test change
echo "# Test" >> test_file.md
git add test_file.md
# In Claude Code session
/commit
```
- [ ] Pre-commit-check agent runs
- [ ] Conventional commit message generated
- [ ] No secrets detected in test file
- [ ] Can approve and commit

### 3. Plan Command (if implemented)
```bash
# In Claude Code session
/plan
```
- [ ] Reads PROJECT_PLAN.md
- [ ] Asks clarifying questions
- [ ] Proposes structured plan

---

## Documentation Consistency

### 1. CLAUDE.md References
```bash
grep -E "skills|agents|Extended Thinking" .claude/CLAUDE.md
```
- [ ] Mentions `.claude/skills/`
- [ ] Explains Skills vs Agents
- [ ] Documents Extended Thinking
- [ ] Explains agent spawning mechanism

### 2. Template Files Intact
- [ ] `_rename_to_README.md` mentions Skills & Agents
- [ ] `_rename_to_ARCHITECTURE.md` documents hybrid approach
- [ ] Both reference Extended Thinking feature

### 3. README References (after rename)
After running `/setup` and renaming template files:
- [ ] README.md lists Skills & Agents as features
- [ ] ARCHITECTURE.md documents agent structure
- [ ] Directory structure shows `.claude/skills/` and `.claude/agents/`

---

## Integration Tests

### 1. Skills + Agents Working Together
Create a commit with multiple file types:
```bash
mkdir -p src/api
echo "def login(): pass" > src/api/auth.py
git add src/api/auth.py
/commit
```
- [ ] Security-review agent spawns (auth pattern trigger)
- [ ] Pre-commit-check agent runs
- [ ] Commit-message-skill formats message
- [ ] All complete without errors

### 2. Hook Execution (Optional)
If hooks configured in settings.json:
```bash
# Edit a file
echo "test" >> .claude/CLAUDE.md
```
- [ ] PostToolUse hook triggers (if configured)
- [ ] No errors in hook execution

---

## Cleanup

After testing:
```bash
# Remove test files
rm -rf src/
rm test_file.md
git reset --hard HEAD
```

---

## Expected Results

**All checks passing means**:
- Skills are properly formatted and invocable
- Agents spawn correctly on triggers
- Configuration is valid
- Workflows function as designed
- Documentation is consistent

**If checks fail**:
- Review TEMPLATE_DEVELOPMENT.md for known issues
- Check Claude Code version compatibility
- Verify template wasn't modified during clone

---

## Version Compatibility

Tested with:
- Claude Code CLI: (Add version after testing)
- Claude Model: Sonnet 4.5
- Python: 3.8+

---

*This checklist validates the Golden Template's readiness for production use.*
