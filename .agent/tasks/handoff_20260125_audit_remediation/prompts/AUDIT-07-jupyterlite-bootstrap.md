# AUDIT-07: Fix JupyterLite Bootstrap URL Length

## Problem

Bootstrap code is passed via URL parameter, risking 431 errors when code grows too large.

## Target Files

- `praxis/web-client/src/app/features/playground/playground.component.ts`
- `praxis/web-client/src/assets/jupyterlite/bootstrap.py` (NEW)

## Requirements

### 1. Create Static Bootstrap File

Create `praxis/web-client/src/assets/jupyterlite/bootstrap.py`:

```python
# Praxis JupyterLite Bootstrap
# This file is loaded after kernel initialization

import sys
import micropip

async def setup_praxis():
    """Initialize Praxis environment in JupyterLite."""
    # Install pylabrobot
    await micropip.install('pylabrobot')
    
    # Setup I/O patching for browser environment
    # ... existing bootstrap code from playground.component.ts ...
    
    print("Praxis environment ready!")

# Auto-run setup
import asyncio
asyncio.ensure_future(setup_praxis())
```

### 2. Modify Playground Component

In `playground.component.ts`, replace URL parameter approach with postMessage:

```typescript
// Instead of encoding bootstrap in URL:
private async initKernel() {
  // Wait for kernel ready signal
  this.jupyterChannel.onReady$.pipe(first()).subscribe(() => {
    this.sendBootstrapCode();
  });
}

private async sendBootstrapCode() {
  // Fetch bootstrap from static file
  const response = await fetch(this.assetService.getJupyterAssetPath('bootstrap.py'));
  const bootstrapCode = await response.text();
  
  // Send via postMessage to kernel
  this.jupyterChannel.sendMessage({
    type: 'execute',
    code: bootstrapCode
  });
}
```

### 3. Update URL Builder

Remove bootstrap code from `buildJupyterliteUrl()`:

```typescript
buildJupyterliteUrl(): string {
  const basePath = this.getJupyterliteBasePath();
  // No longer include bootstrap in URL
  return `${basePath}/repl/index.html`;
}
```

### 4. Handle GH-Pages Path

Ensure bootstrap.py is included in build and path works for both dev and production:

```typescript
getBootstrapPath(): string {
  return this.assetService.resolve('jupyterlite/bootstrap.py');
}
```

## Configuration Matrix

| Config | Dev | GH-Pages |
|--------|-----|----------|
| Bootstrap Path | `./assets/jupyterlite/bootstrap.py` | `/praxis/assets/jupyterlite/bootstrap.py` |

## Reference

See `docs/audits/AUDIT-07-jupyterlite.md` for architecture diagram.

## Verification

```bash
npm run build:gh-pages --prefix praxis/web-client
npm run test --prefix praxis/web-client
```

Manual test:

1. Open playground in browser
2. Verify kernel initializes without URL length errors
3. Verify pylabrobot is available in kernel
