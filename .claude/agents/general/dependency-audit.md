# Dependency Audit Agent

## Trigger

Spawned when:
- Package manifest files are modified (package.json, requirements.txt, Cargo.toml, go.mod, etc.)
- User adds new dependencies to the project
- User explicitly requests a dependency audit
- Periodically recommended during major version updates

---

## Agent Type

Explore

## Thoroughness

thorough

---

## Prompt

Analyze the project's dependencies for security, licensing, and maintenance concerns:

### Security Vulnerabilities
- Check for known vulnerabilities in direct dependencies
- Identify dependencies with poor security track records
- Flag dependencies that haven't been updated in 2+ years
- Note any dependencies with active CVEs mentioned in their repos

### Licensing Compliance
- Identify license types for all direct dependencies
- Flag copyleft licenses (GPL, AGPL) that may have implications
- Note any dependencies with unclear or missing licenses
- Check for license compatibility with project's intended use

### Maintenance Health
- Dependencies with no updates in 12+ months
- Projects marked as deprecated or archived
- Single-maintainer projects with low activity
- Dependencies with many open security issues

### Bundle/Size Concerns
- Large dependencies that may have lighter alternatives
- Dependencies that duplicate functionality
- Transitive dependency bloat

Search for:
- Package manifest files (package.json, requirements.txt, pyproject.toml, Cargo.toml, go.mod, Gemfile, etc.)
- Lock files for version pinning status
- Any security advisory files or audit logs

---

## Output

Return a structured report:

```
DEPENDENCY AUDIT RESULTS
========================

Manifest Files Found: [list]
Total Direct Dependencies: [count]

SECURITY CONCERNS:
------------------
[If found]
- [package@version] - Description of concern
  Recommendation: Upgrade to X.X.X / Replace with Y
[If none]
No known security issues in direct dependencies.

LICENSING:
----------
- MIT/Apache/BSD (permissive): [count]
- GPL/LGPL/AGPL (copyleft): [count] [list if any]
- Unknown/Custom: [count] [list if any]

MAINTENANCE FLAGS:
------------------
[If found]
- [package] - Last updated [date], [concern]
[If none]
All dependencies appear actively maintained.

RECOMMENDATIONS:
----------------
[Prioritized list of suggested actions]
```

Note: This agent performs static analysis only. For comprehensive vulnerability scanning, recommend running dedicated tools (npm audit, pip-audit, cargo-audit, etc.).
