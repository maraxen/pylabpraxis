# Browser Mode

Praxis supports a frontend-only browser mode that runs entirely in the browser without requiring a backend server.

## When to Use Browser Mode

- **Demonstrations**: Show Praxis to stakeholders without infrastructure setup
- **UI Development**: Work on frontend features without running the backend
- **Local Exploration**: Explore the app safely without connecting hardware
- **Offline Testing**: Test the UI when disconnected from the network

## Starting Browser Mode

```bash
cd praxis/web-client
npm run start:browser
```

This starts the Angular dev server with the browser configuration.

## How Browser Mode Works

### HTTP Interceptor

Browser mode uses an Angular HTTP interceptor that catches all API calls and returns mock data:

```typescript
// Simplified example of how the interceptor works
@Injectable()
export class BrowserModeInterceptor implements HttpInterceptor {
  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // Return mock data instead of making real HTTP requests
    if (req.url.includes('/api/v1/protocols')) {
      return of(new HttpResponse({ body: MOCK_PROTOCOLS }));
    }
    // ... other mock handlers
  }
}
```

### SQLite In-Browser Storage

For persistence across page reloads, browser mode uses SQL.js (SQLite compiled to WebAssembly):

- Pre-seeded with sample protocols, machines, and resources
- Supports full CRUD operations
- Data persists in browser storage (IndexedDB)

### Mock Protocol Execution

When running protocols in browser mode:

1. Execution is simulated with realistic timing
2. Progress updates are generated at intervals
3. Mock telemetry data is produced
4. No actual hardware communication occurs

## Pre-Seeded Data

Browser mode includes:

| Category | Items |
|----------|-------|
| **Protocols** | 3+ sample protocols (transfer, serial dilution, PCR setup) |
| **Machines** | Opentrons Flex, Hamilton STAR, plate readers |
| **Resources** | 60+ labware definitions (plates, tips, reservoirs) |
| **Workcell** | Pre-configured deck layout |

## Limitations

| Feature | Browser Mode Behavior |
|---------|-------------------|
| **Scheduled Runs** | Shows "Coming Soon" indicator |
| **Real-time WebSocket** | Uses polling simulation |
| **Hardware Discovery** | Returns mock device list |
| **Authentication** | Bypassed (auto-login as local user) |
| **Data Persistence** | Browser storage only (not synced to server) |

## Security Considerations

!!! warning "Browser Mode Security"

    Browser mode bypasses authentication and should **never** be enabled in production.

    Safeguards in place:

    1. **Environment check**: `NODE_ENV !== 'production'`
    2. **Separate build config**: Uses `environment.browser.ts`
    3. **Code exclusion**: Interceptor not included in production bundle

## Building for GitHub Pages

To deploy a static build to GitHub Pages:

```bash
cd praxis/web-client

# Build with gh-pages configuration
npm run build:gh-pages

# Output is in dist/web-client
# Deploy to gh-pages branch or configure GitHub Actions
```

### GitHub Actions Workflow

```yaml
name: Deploy Static Build
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
        working-directory: praxis/web-client
      - run: npm run build:gh-pages
        working-directory: praxis/web-client
      - uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: praxis/web-client/dist/web-client
```

## Customizing Browser Mode Data

To modify the pre-seeded browser mode data, edit the seed files:

```
praxis/web-client/src/app/core/
├── interceptors/
│   └── browser-mode.interceptor.ts  # HTTP mock handlers
├── services/
│   └── sqlite.service.ts            # SQLite initialization
└── assets/browser-data/             # Mock data files
```

After modifying, rebuild for browser mode:

```bash
npm run build:browser
```
