# Task: Pluggable Storage Layer for GitHub Pages Demo

**Created**: 2025-12-29  
**Priority**: High  
**Goal**: Enable PyLabPraxis to run entirely in-browser via GitHub Pages by abstracting storage dependencies.

---

## 📋 Overview

Currently, PyLabPraxis requires:

- **PostgreSQL** - Data persistence (via SQLAlchemy)
- **Redis** - Pub/sub for WebSocket events, Celery task queue broker

For a GitHub Pages demo (pure static hosting), we need the backend to run without these external services. Rather than creating a "mock mode" fork, we should **abstract the storage layer** so different implementations can be swapped.

---

## 🎯 Success Criteria

1. Backend can run with `STORAGE_BACKEND=memory` (no PostgreSQL, no Redis)
2. Frontend demo works on GitHub Pages with pre-seeded data
3. No code duplication - same business logic, different storage adapters
4. Existing production setup (`postgresql+redis`) continues to work unchanged

---

## 🏗️ Architecture

### Current State

```
main.py
├── AsyncSessionLocal (SQLAlchemy PostgreSQL)
├── Redis client (direct redis-py)
└── Celery (Redis broker)
```

### Target State

```
main.py
├── StorageFactory.create_session_factory()
│   ├── PostgreSQL (production)
│   └── SQLite in-memory (demo/test)
├── StorageFactory.create_key_value_store()
│   ├── Redis (production)
│   └── InMemory dict (demo/test)
├── StorageFactory.create_pubsub()
│   ├── Redis pub/sub (production)
│   └── In-process EventEmitter (demo/test)
└── StorageFactory.create_task_queue()
    ├── Celery (production)
    └── AsyncIO queue (demo/test)
```

---

## 📝 Implementation Plan

### Phase 1: Storage Abstractions (Backend)

#### 1.1 Create Protocol Definitions

**File**: `praxis/backend/core/storage/protocols.py`

```python
from typing import Protocol, Any, AsyncIterator

class KeyValueStore(Protocol):
    """Abstract key-value storage (Redis replacement)."""
    async def get(self, key: str) -> Any | None: ...
    async def set(self, key: str, value: Any, ttl: int | None = None) -> None: ...
    async def delete(self, key: str) -> None: ...
    async def exists(self, key: str) -> bool: ...

class PubSubChannel(Protocol):
    """Abstract pub/sub channel."""
    async def publish(self, channel: str, message: Any) -> None: ...
    async def subscribe(self, channel: str) -> AsyncIterator[Any]: ...
    async def unsubscribe(self, channel: str) -> None: ...

class TaskQueue(Protocol):
    """Abstract async task queue."""
    def send_task(self, name: str, args: list[Any]) -> TaskResult: ...
    async def get_result(self, task_id: str) -> Any: ...
```

#### 1.2 Implement Redis Adapter

**File**: `praxis/backend/core/storage/redis_adapter.py`

Wrap existing Redis usage to conform to the protocols.

#### 1.3 Implement In-Memory Adapter

**File**: `praxis/backend/core/storage/memory_adapter.py`

Simple Python dict-based implementation for demo/testing.

#### 1.4 Create Storage Factory

**File**: `praxis/backend/core/storage/factory.py`

```python
def create_storage_backend(backend_type: str = "postgresql"):
    if backend_type == "memory":
        return MemoryStorageBackend()
    elif backend_type == "postgresql":
        return PostgreSQLStorageBackend()
    else:
        raise ValueError(f"Unknown backend: {backend_type}")
```

### Phase 2: SQLAlchemy Dialect Compatibility

#### 2.1 Identify PostgreSQL-specific Features

Audit codebase for:

- `JSONB` columns → Replace with `JSON` (SQLite compatible)
- `ARRAY` types → Replace with `JSON` serialization
- PostgreSQL-specific SQL functions

#### 2.2 Create Dialect-Agnostic Models

Update ORM models to use portable column types:

```python
from sqlalchemy import JSON  # Not JSONB

class ProtocolRunOrm(Base):
    output_data_json: Mapped[dict] = mapped_column(JSON, nullable=True)
```

### Phase 3: Frontend Demo Mode

#### 3.1 Create Demo Environment

**File**: `praxis/web-client/src/environments/environment.demo.ts`

```typescript
export const environment = {
  production: false,
  demo: true,
  apiUrl: '/api',  // Will be intercepted
  keycloakEnabled: false,
};
```

#### 3.2 Create Mock HTTP Interceptor

**File**: `praxis/web-client/src/app/core/interceptors/demo.interceptor.ts`

Intercepts HTTP requests and routes to in-browser mock backend.

#### 3.3 Pre-seed Demo Data

**File**: `praxis/web-client/src/assets/demo-data/`

Static JSON files:

- `protocols.json` - Protocol definitions
- `assets.json` - Sample machines/resources
- `runs.json` - Sample completed runs

### Phase 4: GitHub Pages Deployment

#### 4.1 GitHub Actions Workflow

**File**: `.github/workflows/deploy-demo.yml`

```yaml
name: Deploy Demo to GitHub Pages
on:
  push:
    branches: [main]
    paths:
      - 'praxis/web-client/**'
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm run build:demo
      - uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./dist/praxis-web-client
```

---

## 📊 Effort Estimates

| Phase | Effort | Risk |
|-------|--------|------|
| 1. Storage Abstractions | 4-6 hours | Low |
| 2. SQLAlchemy Compatibility | 2-4 hours | Medium (edge cases) |
| 3. Frontend Demo Mode | 3-4 hours | Low |
| 4. GitHub Pages Deploy | 1-2 hours | Low |
| **Total** | **10-16 hours** | |

---

## ⚠️ Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| JSONB queries break on SQLite | Use portable `JSON` type; test with SQLite |
| Celery requires broker | In-memory mode uses `asyncio.Queue` directly |
| Session management differs | Use `async_scoped_session` consistently |

---

## 🔗 Related Files

| Purpose | Path |
|---------|------|
| Database config | `praxis/backend/utils/db.py` |
| Redis usage | `praxis/backend/api/websockets.py` |
| Celery config | `praxis/backend/core/celery.py` |
| Main lifespan | `main.py` |

---

## 📚 References

- [Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html)
- [SQLAlchemy JSON Type](https://docs.sqlalchemy.org/en/20/core/type_basics.html#sqlalchemy.types.JSON)
- [sql.js (SQLite WASM)](https://sql.js.org/)

---

## 🧪 Testing & Validation Strategy

### Unit Tests

#### Storage Adapters

**File**: `tests/core/storage/test_adapters.py`

```python
import pytest
from praxis.backend.core.storage.memory_adapter import InMemoryKeyValueStore
from praxis.backend.core.storage.redis_adapter import RedisKeyValueStore

@pytest.fixture
def memory_store():
    return InMemoryKeyValueStore()

@pytest.fixture
def redis_store():
    # Only run if Redis available
    pytest.importorskip("redis")
    return RedisKeyValueStore(url="redis://localhost:6379")

class TestKeyValueStoreContract:
    """Test that all adapters conform to the same interface."""
    
    @pytest.mark.parametrize("store_fixture", ["memory_store", "redis_store"])
    async def test_set_and_get(self, store_fixture, request):
        store = request.getfixturevalue(store_fixture)
        await store.set("key1", {"data": "value"})
        result = await store.get("key1")
        assert result == {"data": "value"}
    
    @pytest.mark.parametrize("store_fixture", ["memory_store", "redis_store"])
    async def test_delete(self, store_fixture, request):
        store = request.getfixturevalue(store_fixture)
        await store.set("key1", "value")
        await store.delete("key1")
        assert await store.get("key1") is None
    
    @pytest.mark.parametrize("store_fixture", ["memory_store", "redis_store"])
    async def test_ttl_expiration(self, store_fixture, request):
        store = request.getfixturevalue(store_fixture)
        await store.set("key1", "value", ttl=1)
        await asyncio.sleep(1.5)
        assert await store.get("key1") is None
```

#### SQLAlchemy Dialect Tests

**File**: `tests/models/test_dialect_compatibility.py`

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

@pytest.mark.parametrize("dialect", ["sqlite", "postgresql"])
def test_protocol_run_orm_works_on_dialect(dialect, tmp_path):
    if dialect == "sqlite":
        url = f"sqlite:///{tmp_path}/test.db"
    else:
        url = "postgresql+asyncpg://test_user:test_password@localhost:5433/test_db"
        pytest.importorskip("asyncpg")
    
    # Create engine and tables
    engine = create_engine(url)
    Base.metadata.create_all(engine)
    
    # Test CRUD operations
    with Session(engine) as session:
        run = ProtocolRunOrm(name="test", output_data_json={"key": "value"})
        session.add(run)
        session.commit()
        
        # Verify JSON query works
        result = session.query(ProtocolRunOrm).filter(
            ProtocolRunOrm.output_data_json["key"].astext == "value"
        ).first()
        assert result is not None
```

### Integration Tests

#### In-Memory Backend E2E

**File**: `tests/integration/test_memory_backend.py`

```python
import pytest
from fastapi.testclient import TestClient
from main import create_app

@pytest.fixture
def memory_app():
    """Create app with in-memory storage."""
    import os
    os.environ["STORAGE_BACKEND"] = "memory"
    app = create_app()
    return app

def test_protocol_crud_with_memory_backend(memory_app):
    client = TestClient(memory_app)
    
    # Create protocol definition
    response = client.post("/api/v1/protocols/definitions", json={...})
    assert response.status_code == 201
    
    # List protocols
    response = client.get("/api/v1/protocols/definitions")
    assert len(response.json()) >= 1
```

### Frontend Tests

#### Demo Mode Interceptor

**File**: `praxis/web-client/src/app/core/interceptors/demo.interceptor.spec.ts`

```typescript
describe('DemoInterceptor', () => {
  it('should return mock protocols when in demo mode', () => {
    const interceptor = new DemoInterceptor();
    const req = new HttpRequest('GET', '/api/v1/protocols/definitions');
    
    interceptor.intercept(req, mockHandler).subscribe(response => {
      expect(response.body.length).toBeGreaterThan(0);
    });
  });
  
  it('should pass through when not in demo mode', () => {
    environment.demo = false;
    const interceptor = new DemoInterceptor();
    // Should call next.handle()
  });
});
```

### Validation Checklist

#### Phase 1 Validation

- [ ] `InMemoryKeyValueStore` passes all contract tests
- [ ] `RedisKeyValueStore` passes all contract tests  
- [ ] Both implementations are interchangeable

#### Phase 2 Validation

- [ ] All ORM models work with SQLite
- [ ] JSON queries work on both dialects
- [ ] No ARRAY or JSONB-specific code remains

#### Phase 3 Validation

- [ ] `ng build --configuration demo` succeeds
- [ ] Demo interceptor returns correct mock data
- [ ] Keycloak is bypassed in demo mode

#### Phase 4 Validation

- [ ] GitHub Actions workflow runs successfully
- [ ] Demo site loads at `https://<user>.github.io/pylabpraxis`
- [ ] All demo features work (protocol list, run wizard, deck visualizer)

### CI Integration

Add to `.github/workflows/test.yml`:

```yaml
jobs:
  test-memory-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: uv sync
      - run: STORAGE_BACKEND=memory uv run pytest tests/ -m "not requires_postgres"
  
  test-postgres-backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_password
          POSTGRES_DB: test_db
    steps:
      - uses: actions/checkout@v4
      - run: uv sync
      - run: uv run pytest tests/
```

---

## ✅ Definition of Done

- [ ] `uv run pytest` passes with `STORAGE_BACKEND=memory`
- [ ] `ng build --configuration demo` produces working static bundle
- [ ] Demo deployed to GitHub Pages with sample data
- [ ] Production setup unchanged - all existing tests pass
