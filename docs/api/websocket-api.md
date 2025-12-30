# WebSocket API

Praxis uses WebSocket for real-time updates during protocol execution.

## Connection

Connect to the WebSocket endpoint:

```
ws://localhost:8000/api/v1/ws
```

With authentication:
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws?token=<jwt_token>');
```

## Message Format

All messages are JSON with a consistent structure:

```json
{
  "type": "message_type",
  "run_id": "run-xyz",
  "data": {...},
  "timestamp": "2025-01-01T12:00:00Z"
}
```

## Subscribing to Runs

### Subscribe

```json
{
  "action": "subscribe",
  "channel": "run:run-xyz"
}
```

### Unsubscribe

```json
{
  "action": "unsubscribe",
  "channel": "run:run-xyz"
}
```

## Message Types

### Run Status Update

```json
{
  "type": "run_status",
  "run_id": "run-xyz",
  "data": {
    "status": "RUNNING",
    "current_step": 3,
    "total_steps": 10
  }
}
```

Status values:
- `PENDING` - Run created, not started
- `RUNNING` - Execution in progress
- `PAUSED` - Temporarily halted
- `COMPLETED` - Finished successfully
- `FAILED` - Finished with error
- `CANCELLED` - User cancelled

### Progress Update

```json
{
  "type": "progress",
  "run_id": "run-xyz",
  "data": {
    "current_step": 5,
    "total_steps": 10,
    "percentage": 50,
    "step_name": "Transfer to destination"
  }
}
```

### Log Entry

```json
{
  "type": "log",
  "run_id": "run-xyz",
  "data": {
    "level": "INFO",
    "message": "Picking up tips from A1:H1",
    "timestamp": "2025-01-01T12:00:05Z"
  }
}
```

Log levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`

### Telemetry Data

```json
{
  "type": "telemetry",
  "run_id": "run-xyz",
  "data": {
    "metric": "temperature",
    "value": 37.2,
    "unit": "celsius",
    "source": "incubator-1"
  }
}
```

### Run Complete

```json
{
  "type": "run_complete",
  "run_id": "run-xyz",
  "data": {
    "status": "COMPLETED",
    "result": {...},
    "duration_seconds": 1234
  }
}
```

### Run Error

```json
{
  "type": "run_error",
  "run_id": "run-xyz",
  "data": {
    "error_type": "HardwareConnectionError",
    "message": "Lost connection to liquid handler",
    "step": 7,
    "recoverable": false
  }
}
```

## Client Implementation

### JavaScript/TypeScript

```typescript
class PraxisWebSocket {
  private ws: WebSocket;
  private handlers = new Map<string, Function[]>();

  constructor(url: string, token: string) {
    this.ws = new WebSocket(`${url}?token=${token}`);
    this.ws.onmessage = (event) => this.handleMessage(event);
  }

  subscribe(runId: string): void {
    this.ws.send(JSON.stringify({
      action: 'subscribe',
      channel: `run:${runId}`
    }));
  }

  on(type: string, handler: Function): void {
    if (!this.handlers.has(type)) {
      this.handlers.set(type, []);
    }
    this.handlers.get(type)!.push(handler);
  }

  private handleMessage(event: MessageEvent): void {
    const message = JSON.parse(event.data);
    const handlers = this.handlers.get(message.type) || [];
    handlers.forEach(h => h(message));
  }
}

// Usage
const ws = new PraxisWebSocket('ws://localhost:8000/api/v1/ws', token);

ws.subscribe('run-xyz');

ws.on('progress', (msg) => {
  console.log(`Progress: ${msg.data.percentage}%`);
});

ws.on('log', (msg) => {
  console.log(`[${msg.data.level}] ${msg.data.message}`);
});
```

### Python

```python
import asyncio
import websockets
import json

async def monitor_run(run_id: str, token: str):
    uri = f"ws://localhost:8000/api/v1/ws?token={token}"

    async with websockets.connect(uri) as ws:
        # Subscribe to run
        await ws.send(json.dumps({
            "action": "subscribe",
            "channel": f"run:{run_id}"
        }))

        # Listen for messages
        async for message in ws:
            data = json.loads(message)

            if data["type"] == "progress":
                print(f"Progress: {data['data']['percentage']}%")

            elif data["type"] == "log":
                print(f"[{data['data']['level']}] {data['data']['message']}")

            elif data["type"] == "run_complete":
                print("Run completed!")
                break

# Run
asyncio.run(monitor_run("run-xyz", "your-jwt-token"))
```

## Angular Service

```typescript
@Injectable({ providedIn: 'root' })
export class WebSocketService {
  private socket$ = webSocket<WsMessage>({
    url: `${environment.wsUrl}/api/v1/ws`,
    openObserver: {
      next: () => console.log('WebSocket connected')
    }
  });

  subscribeToRun(runId: string): Observable<WsMessage> {
    this.socket$.next({
      action: 'subscribe',
      channel: `run:${runId}`
    } as any);

    return this.socket$.pipe(
      filter(msg => msg.run_id === runId)
    );
  }

  unsubscribeFromRun(runId: string): void {
    this.socket$.next({
      action: 'unsubscribe',
      channel: `run:${runId}`
    } as any);
  }
}
```

## Heartbeat

The server sends periodic heartbeat messages:

```json
{
  "type": "heartbeat",
  "timestamp": "2025-01-01T12:00:00Z"
}
```

Clients should respond with:

```json
{
  "type": "pong"
}
```

Connection is closed if no pong received within 30 seconds.

## Error Handling

### Connection Errors

```json
{
  "type": "error",
  "data": {
    "code": "AUTH_FAILED",
    "message": "Invalid or expired token"
  }
}
```

Error codes:
- `AUTH_FAILED` - Authentication error
- `INVALID_MESSAGE` - Malformed message
- `UNKNOWN_CHANNEL` - Invalid subscription channel
- `RATE_LIMITED` - Too many messages

### Reconnection

Clients should implement automatic reconnection:

```typescript
class ReconnectingWebSocket {
  private reconnectAttempts = 0;
  private maxAttempts = 10;

  private connect(): void {
    this.ws = new WebSocket(this.url);

    this.ws.onclose = () => {
      if (this.reconnectAttempts < this.maxAttempts) {
        const delay = Math.min(1000 * 2 ** this.reconnectAttempts, 30000);
        setTimeout(() => {
          this.reconnectAttempts++;
          this.connect();
        }, delay);
      }
    };

    this.ws.onopen = () => {
      this.reconnectAttempts = 0;
      // Re-subscribe to channels
      this.resubscribe();
    };
  }
}
```
