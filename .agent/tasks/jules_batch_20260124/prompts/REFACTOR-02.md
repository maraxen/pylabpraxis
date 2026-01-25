# REFACTOR-02: Document SharedArrayBuffer Limitation

## Context

**Create**: `docs/troubleshooting/shared-array-buffer.md`
**Issue**: Python worker requires SharedArrayBuffer which needs COOP/COEP headers

## Requirements

Create documentation explaining the SharedArrayBuffer limitation:

```markdown
# SharedArrayBuffer Browser Requirements

## Problem

When running Praxis in browser mode, you may see this error:

```

python.worker.ts:17 Uncaught ReferenceError: SharedArrayBuffer is not defined

```

## Cause

The Python worker (Pyodide) uses `SharedArrayBuffer` for multi-threaded performance.
Modern browsers require specific security headers to enable `SharedArrayBuffer`:

- `Cross-Origin-Opener-Policy: same-origin` (COOP)
- `Cross-Origin-Embedder-Policy: require-corp` (COEP)

## Impact

Without these headers:
- Python code execution may be slower
- Some features may not work in browser mode

## Solutions

### Development Server

Headers are configured in `angular.json` under the dev server settings.

### Production Deployment

Ensure your web server sends the required headers:

**nginx:**
```nginx
add_header Cross-Origin-Opener-Policy same-origin;
add_header Cross-Origin-Embedder-Policy require-corp;
```

**Apache:**

```apache
Header set Cross-Origin-Opener-Policy "same-origin"
Header set Cross-Origin-Embedder-Policy "require-corp"
```

### GitHub Pages

GitHub Pages does not support custom headers. Praxis uses a service worker workaround. If you experience issues, try using a different hosting provider.

## Testing

Verify headers with browser DevTools → Network → check response headers.

```

Do NOT:
- Modify any code files
- Change server configurations
- Add complex workarounds

## Acceptance Criteria

- [ ] File created at `docs/troubleshooting/shared-array-buffer.md`
- [ ] Clear explanation of the problem
- [ ] Multiple solution options documented
- [ ] Follows existing docs formatting
