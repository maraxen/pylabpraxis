# REST API Reference

The Praxis backend provides a RESTful API for all operations.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

Most endpoints require authentication via JWT bearer token:

```bash
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/...
```

### Get Token

```
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "password"
}
```

Response:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

## Protocols

### List Protocols

```
GET /api/v1/protocols
```

Query parameters:
| Param | Type | Description |
|-------|------|-------------|
| `search` | string | Search by name/description |
| `category` | string | Filter by category |
| `skip` | int | Pagination offset |
| `limit` | int | Page size (default 20) |

Response:
```json
{
  "items": [
    {
      "id": "abc123",
      "accession_id": "PROTO-001",
      "name": "Simple Transfer",
      "description": "Transfer liquid between plates",
      "category": "Transfers",
      "parameters": {...},
      "created_at": "2025-01-01T00:00:00Z"
    }
  ],
  "total": 42,
  "skip": 0,
  "limit": 20
}
```

### Get Protocol

```
GET /api/v1/protocols/{id}
```

### Sync Protocols

```
POST /api/v1/discovery/sync-all
```

Triggers protocol discovery from configured directories.

## Protocol Execution

### Execute Protocol

```
POST /api/v1/execution/run
Content-Type: application/json

{
  "protocol_id": "abc123",
  "parameters": {
    "volume": 100,
    "wells": 96
  },
  "assets": {
    "machines": {
      "liquid_handler": "mach-001"
    },
    "resources": {
      "source_plate": "res-001",
      "dest_plate": "res-002",
      "tip_rack": "res-003"
    }
  },
  "simulation": false
}
```

Response:
```json
{
  "run_id": "run-xyz",
  "status": "RUNNING",
  "started_at": "2025-01-01T12:00:00Z"
}
```

### Get Run Status

```
GET /api/v1/execution/runs/{run_id}
```

Response:
```json
{
  "id": "run-xyz",
  "protocol_id": "abc123",
  "status": "RUNNING",
  "current_step": 3,
  "total_steps": 10,
  "progress": 30,
  "started_at": "2025-01-01T12:00:00Z"
}
```

### Control Run

```
POST /api/v1/execution/runs/{run_id}/pause
POST /api/v1/execution/runs/{run_id}/resume
POST /api/v1/execution/runs/{run_id}/cancel
```

### Schedule Run

```
POST /api/v1/execution/schedule
Content-Type: application/json

{
  "protocol_id": "abc123",
  "parameters": {...},
  "scheduled_for": "2025-01-02T09:00:00Z"
}
```

## Machines

### List Machines

```
GET /api/v1/machines
```

Query parameters:
| Param | Type | Description |
|-------|------|-------------|
| `status` | string | Filter by status (IDLE, RUNNING, OFFLINE) |
| `type` | string | Filter by machine type |

### Get Machine

```
GET /api/v1/machines/{id}
```

### Create Machine

```
POST /api/v1/machines
Content-Type: application/json

{
  "name": "Flex Lab A",
  "model": "Opentrons Flex",
  "manufacturer": "Opentrons",
  "status": "OFFLINE",
  "connection_info": {
    "host": "192.168.1.50",
    "port": 31950
  },
  "machine_definition_accession_id": "def-123"
}
```

### Update Machine

```
PUT /api/v1/machines/{id}
```

### Delete Machine

```
DELETE /api/v1/machines/{id}
```

## Resources

### List Resources

```
GET /api/v1/resources
```

Query parameters:
| Param | Type | Description |
|-------|------|-------------|
| `category` | string | Filter by category (Plate, TipRack, etc.) |
| `consumable` | boolean | Filter by consumable property |
| `available` | boolean | Filter by availability |

### Get Resource

```
GET /api/v1/resources/{id}
```

### Create Resource

```
POST /api/v1/resources
Content-Type: application/json

{
  "name": "96-Well Plate #1",
  "category": "Plate",
  "properties": {
    "consumable": false,
    "reusable": true
  },
  "resource_definition_accession_id": "def-456"
}
```

### Update Resource

```
PUT /api/v1/resources/{id}
```

### Delete Resource

```
DELETE /api/v1/resources/{id}
```

## Definitions

### List Machine Definitions

```
GET /api/v1/discovery/machines
```

### List Resource Definitions

```
GET /api/v1/discovery/resources
```

Query parameters:
| Param | Type | Description |
|-------|------|-------------|
| `category` | string | Filter by category |
| `search` | string | Search by name/FQN |

## Hardware Discovery

### Discover Serial Devices

```
GET /api/v1/hardware/discover/serial
```

### Discover USB Devices

```
GET /api/v1/hardware/discover/usb
```

### Register Device

```
POST /api/v1/hardware/register
Content-Type: application/json

{
  "name": "Device Name",
  "device_type": "serial",
  "port": "/dev/ttyUSB0",
  "fqn": "pylabrobot.backends.SomeBackend",
  "connection_info": {...}
}
```

## Data Outputs

### List Run Outputs

```
GET /api/v1/outputs?run_id={run_id}
```

### Get Output

```
GET /api/v1/outputs/{id}
```

### Export Output

```
GET /api/v1/outputs/{id}/export?format=csv
GET /api/v1/outputs/{id}/export?format=json
```

## Workcells

### List Workcells

```
GET /api/v1/workcells
```

### Get Workcell

```
GET /api/v1/workcells/{id}
```

### Get Workcell Deck

```
GET /api/v1/workcells/{id}/deck
```

## Error Responses

All errors follow a consistent format:

```json
{
  "error": "ErrorType",
  "message": "Human-readable description",
  "details": {...}
}
```

Common HTTP status codes:

| Code | Meaning |
|------|---------|
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Missing or invalid token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 409 | Conflict - Resource already exists or is in use |
| 422 | Unprocessable Entity - Validation error |
| 500 | Internal Server Error |

## Pagination

List endpoints support pagination:

```
GET /api/v1/protocols?skip=20&limit=10
```

Response includes pagination metadata:
```json
{
  "items": [...],
  "total": 100,
  "skip": 20,
  "limit": 10
}
```

## Filtering

Many endpoints support filtering via query parameters:

```
GET /api/v1/resources?category=Plate&consumable=true&status=AVAILABLE
```

## OpenAPI Schema

The full OpenAPI (Swagger) schema is available at:

```
GET /api/v1/openapi.json
```

Interactive documentation:
```
GET /docs      # Swagger UI
GET /redoc     # ReDoc
```
