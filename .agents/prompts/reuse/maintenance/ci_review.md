# Maintenance Prompt: CI Review

**Purpose:** Review CI/CD pipeline health  
**Frequency:** Quarterly  

---

## Prompt

```markdown
Examine .agents/README.md for development context.

## Task

Review CI/CD pipeline configuration and health.

## Phase 1: Triage

1. **Review CI Configuration**:

   ```bash
   ls -la .github/workflows/ 2>/dev/null || echo "No GitHub workflows"
   cat Makefile | head -n 50
   ```

1. **Check Recent CI Status**: Review GitHub Actions or CI dashboard.

## Phase 2: Categorize and Strategize

1. **Review Workflows**:

   | Aspect | Check |
   |:-------|:------|
   | **Build** | Does it build successfully? |
   | **Tests** | Are all tests running? |
   | **Linting** | Is linting enforced? |
   | **Coverage** | Is coverage reported? |
   | **Dependencies** | Are deps cached? |

2. **Identify Issues**:

   | Issue | Priority |
   |:------|:---------|
   | Failing builds | High |
   | Flaky tests | Medium |
   | Missing checks | Medium |
   | Slow pipelines | Low |

3. **Document Strategy** before making changes.

4. **Get User Input**: ⏸️ PAUSE for approval.

## Phase 3: Apply Fixes

1. **Fix Workflow Issues**: Update workflow YAML files.
2. **Optimize Pipelines**: Add caching, parallelize steps.
3. **Add Missing Checks**: Linting, type checking, coverage.

## Phase 4: Verify and Document

1. **Test Pipeline**: Push a test commit.
2. **Update Health Audits**.

## References

- GitHub Actions documentation
- Current workflow files

```

---

## Customization

This prompt is pre-configured for Praxis. No placeholders needed.
