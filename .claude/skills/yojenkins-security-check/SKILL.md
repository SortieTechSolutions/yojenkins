---
name: yojenkins-security-check
description: Runs a focused security audit on changed or specified files. Use when asked to "check security", "audit credentials", or before PR review.
---

# yojenkins Security Check

Run a targeted security audit on the yojenkins codebase.

## Quick Checks (run on every invocation)

1. **Hardcoded credentials**: Search for patterns like `password=`, `token=`, `secret=`, `api_key=` with literal string values
2. **Credential logging**: Ensure logger calls don't include password, token, or api_key variables
3. **Unsafe XML parsing**: Check for `xml.etree.ElementTree.fromstring()` with unsanitized input (potential XXE)
4. **URL validation**: Check that user-provided URLs are validated before use
5. **Subprocess safety**: Verify subprocess calls use list args, not shell=True with string interpolation

## File-Specific Checks

### yo_jenkins/auth.py
- Verify credentials loaded from TOML are not logged
- Check that getpass is used for interactive password input
- Ensure API tokens are not exposed in error messages

### yo_jenkins/rest.py
- Verify TLS/SSL certificate verification is not disabled
- Check that auth headers are not logged at any level
- Ensure request URLs don't contain credentials

### yo_jenkins/credential.py
- Check XML parsing for XXE vulnerability
- Verify credential values are masked in output

### docker_container/docker_jenkins_server.py
- Flag default password usage
- Check container port exposure
- Verify no privileged mode

## Output Format

For each finding, report:
```
[SEVERITY] file:line - Description
  Recommendation: How to fix
```

Severity levels: CRITICAL, HIGH, MEDIUM, LOW, INFO

## Known Accepted Risks (don't re-flag these)

- B101 (assert statements) - accepted in project bandit config
- Plaintext credential storage in ~/.yojenkins/credentials - known architectural decision, tracked as tech debt
