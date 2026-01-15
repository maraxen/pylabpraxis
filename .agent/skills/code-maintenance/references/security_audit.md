# Maintenance Prompt: Security Audit

**Purpose:** Basic security review  
**Frequency:** Quarterly  

---

## Prompt

```markdown
Examine .agent/README.md for development context.

## Task

Perform a basic security audit of the codebase.

## Phase 1: Triage

1. **Search for Sensitive Patterns**:

   ```bash
   grep -rn "password\|secret\|api_key\|token" praxis/backend --include="*.py" | grep -v __pycache__ | head -n 30
   grep -rn "password\|secret\|api_key\|token" praxis/web-client/src --include="*.ts" | head -n 30
   ```

1. **Check for Hardcoded Credentials**:

   ```bash
   grep -rn "localhost\|127.0.0.1\|0.0.0.0" praxis/backend --include="*.py" | head -n 20
   ```

2. **Run Security Linters**:

   ```bash
   uv run ruff check praxis/backend --select S 2>&1 | head -n 30
   ```

## Phase 2: Categorize and Strategize

1. **Categorize Findings**:

   | Severity | Issue | Action |
   |:---------|:------|:-------|
   | **Critical** | Hardcoded secrets | Remove immediately |
   | **High** | Insecure defaults | Fix configuration |
   | **Medium** | Potential injection | Add validation |
   | **Low** | Information disclosure | Review necessity |

2. **Document Strategy** before making changes.

3. **Get User Input**: ⏸️ PAUSE for approval.

## Phase 3: Apply Fixes

1. **Remove Hardcoded Secrets**: Use environment variables.
2. **Add Input Validation**: Sanitize user inputs.
3. **Review Auth/Authz**: Check permission models.
4. **Update Dependencies**: Address vulnerabilities.

## Phase 4: Verify and Document

1. **Re-scan**: Verify issues resolved.
2. **Update Health Audits**.

## Security Checklist

- [ ] No hardcoded credentials
- [ ] Environment variables for secrets
- [ ] Input validation on API endpoints
- [ ] CORS properly configured
- [ ] Dependencies up to date
- [ ] No debug mode in production config

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- Ruff security rules (S category)

```

---

## Customization

This prompt is pre-configured for Praxis. No placeholders needed.
