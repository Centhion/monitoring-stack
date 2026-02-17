# Security Review Agent

## Trigger

Automatically spawned after editing files that match any of these patterns:
- `**/auth/**` or `**/authentication/**`
- `**/payment/**` or `**/billing/**`
- `**/user/**` or `**/users/**`
- `**/admin/**`
- Files containing: password, token, credential, secret, api_key, apiKey

Also triggered on-demand when requested by the user.

---

## Agent Type

Explore

## Thoroughness

thorough

---

## Prompt

Perform a security review of the recently modified code. Analyze for:

### Injection Vulnerabilities
- SQL injection: Unsanitized user input in database queries
- Command injection: User input passed to shell commands
- XSS: Unsanitized output rendered in HTML/templates
- Path traversal: User input used in file paths

### Authentication and Authorization
- Hardcoded credentials or secrets
- Weak password handling (plaintext storage, weak hashing)
- Missing authentication checks on protected routes
- Broken access control (horizontal/vertical privilege escalation)
- Session management flaws

### Data Exposure
- Sensitive data in logs or error messages
- Overly permissive CORS configuration
- Missing encryption for sensitive data at rest or in transit
- API responses exposing internal details

### Configuration Issues
- Debug mode enabled in production code
- Insecure default configurations
- Missing security headers
- Verbose error messages exposing internals

Search the modified files and their immediate dependencies. Cross-reference with common vulnerability patterns (OWASP Top 10).

---

## Output

Return a structured report:

```
SECURITY REVIEW RESULTS
=======================

Files Analyzed: [list]

FINDINGS:
---------
[If issues found]
- [SEVERITY: HIGH/MEDIUM/LOW] file:line - Description of vulnerability
  Recommendation: How to fix

[If no issues]
No security vulnerabilities detected.

CHECKS PERFORMED:
- [x] Injection vulnerabilities
- [x] Authentication/authorization
- [x] Data exposure
- [x] Configuration issues
```

If critical vulnerabilities are found, clearly mark them and recommend blocking the commit until resolved.
