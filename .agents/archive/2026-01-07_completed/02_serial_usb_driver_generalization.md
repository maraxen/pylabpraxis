# Prompt 2: Serial/USB Driver Generalization (COMPLEX)

**Priority**: P1
**Difficulty**: Large
**Type**: Complex Architecture Change

> **IMPORTANT**: Do NOT use the browser agent. Verify with automated tests only.

---

## Context

The CLARIOstar FTDI driver currently runs entirely in the Pyodide worker, directly accessing `navigator.usb`. This works but is brittle. We need to:

1. Document the current approach for other machines
2. Create mock implementations for testing
3. Generalize the pattern for any serial-over-USB device

---

## Architecture Phases

This prompt covers **Phase A** (Interface + Mocking). The full migration has 2 phases:

| Phase | Scope | This Prompt |
|-------|-------|-------------|
| **A** | Interface abstraction, mock drivers, documentation | ✅ Yes |
| **B** | Move driver to TypeScript main thread, message-passing to Pyodide | ❌ Future |

**Phase B** (future) involves:

- Moving all USB I/O to TypeScript in the main browser thread
- Creating a message-passing protocol between main thread and Pyodide worker
- The Pyodide-side shim becomes a thin proxy that posts messages

---

## Background: Current CLARIOstar Implementation

Location: `praxis/web-client/src/app/features/repl/ftdi-web-serial.ts`

The current implementation:

- Uses WebUSB API to communicate with FTDI chip
- Runs in main thread, exposed to Pyodide worker
- Handles baud rate, data characteristics, status byte stripping

---

## Tasks

### 1. Document Current Driver Architecture

Create `praxis/web-client/src/app/features/repl/README.md`:

```markdown
# REPL Hardware Drivers

## WebUSB/WebSerial Architecture

### Overview
Browser mode supports hardware communication via WebUSB and WebSerial APIs.

### Supported Devices
| Device | Chip | Driver | Status |
|--------|------|--------|--------|
| CLARIOstar | FTDI | `ftdi-web-serial.ts` | ✅ Working |
| Hamilton STAR | CDC-ACM | WebSerial native | ⏳ Pending |
| Opentrons OT-2 | - | HTTP API | N/A |

### Driver Registration
Drivers are registered in `jupyterlite-repl.component.ts`:
- Exposed to `window` object
- Python shim imports via `js` module

### Adding New Drivers
1. Create driver class implementing `ISerial` interface
2. Register in `authorizeHardware()`
3. Update Python shim for device detection
```

### 2. Create ISerial Interface

In `praxis/web-client/src/app/features/repl/serial-interface.ts`:

```typescript
export interface ISerial {
  open(options?: { baudRate?: number }): Promise<void>;
  close(): Promise<void>;
  read(length: number): Promise<Uint8Array>;
  write(data: Uint8Array): Promise<void>;
  readonly isOpen: boolean;
}

export interface ISerialDriver {
  readonly driverName: string;
  readonly supportedDevices: Array<{ vendorId: number; productId: number }>;
  connect(device: USBDevice): Promise<ISerial>;
}
```

### 3. Create Mock Serial Driver for Tests

In `praxis/web-client/src/app/features/repl/mock-serial.ts`:

```typescript
import { ISerial, ISerialDriver } from './serial-interface';

export class MockSerial implements ISerial {
  private _isOpen = false;
  private responseQueue: Uint8Array[] = [];

  get isOpen(): boolean { return this._isOpen; }

  async open(): Promise<void> { this._isOpen = true; }
  async close(): Promise<void> { this._isOpen = false; }
  
  async read(length: number): Promise<Uint8Array> {
    if (this.responseQueue.length > 0) {
      return this.responseQueue.shift()!;
    }
    return new Uint8Array(length);
  }
  
  async write(data: Uint8Array): Promise<void> {
    // Log or record for testing
    console.debug('[MockSerial] Write:', data);
  }
  
  // Test helper
  queueResponse(data: Uint8Array): void {
    this.responseQueue.push(data);
  }
}

export class MockSerialDriver implements ISerialDriver {
  readonly driverName = 'MockSerial';
  readonly supportedDevices = [{ vendorId: 0xFFFF, productId: 0xFFFF }];
  
  async connect(): Promise<ISerial> {
    return new MockSerial();
  }
}
```

### 4. Refactor FTDI Driver to Implement Interface

Update `praxis/web-client/src/app/features/repl/ftdi-web-serial.ts`:

```typescript
import { ISerial, ISerialDriver } from './serial-interface';

export class FtdiSerial implements ISerial {
  // ... existing implementation
}

export class FtdiSerialDriver implements ISerialDriver {
  readonly driverName = 'FTDI';
  readonly supportedDevices = [
    { vendorId: 0x0403, productId: 0x6001 },  // FT232R
    { vendorId: 0x0403, productId: 0x6010 },  // FT2232
    { vendorId: 0x0403, productId: 0x6014 },  // FT232H
  ];
  
  async connect(device: USBDevice): Promise<ISerial> {
    const serial = new FtdiSerial(device);
    return serial;
  }
}
```

### 5. Create Driver Registry

In `praxis/web-client/src/app/features/repl/driver-registry.ts`:

```typescript
import { ISerialDriver } from './serial-interface';
import { FtdiSerialDriver } from './ftdi-web-serial';
import { MockSerialDriver } from './mock-serial';

const drivers: ISerialDriver[] = [
  new FtdiSerialDriver(),
];

// Add mock driver in test mode
if (typeof window !== 'undefined' && (window as any).__PRAXIS_TEST_MODE__) {
  drivers.push(new MockSerialDriver());
}

export function findDriverForDevice(vendorId: number, productId: number): ISerialDriver | undefined {
  return drivers.find(d => 
    d.supportedDevices.some(s => s.vendorId === vendorId && s.productId === productId)
  );
}

export function registerDriver(driver: ISerialDriver): void {
  drivers.push(driver);
}
```

### 6. Add Tests

Create `praxis/web-client/src/app/features/repl/serial-interface.spec.ts`:

```typescript
import { describe, it, expect, vi } from 'vitest';
import { MockSerial, MockSerialDriver } from './mock-serial';

describe('MockSerial', () => {
  it('should open and close', async () => {
    const serial = new MockSerial();
    expect(serial.isOpen).toBe(false);
    await serial.open();
    expect(serial.isOpen).toBe(true);
    await serial.close();
    expect(serial.isOpen).toBe(false);
  });

  it('should return queued responses', async () => {
    const serial = new MockSerial();
    const expected = new Uint8Array([0x01, 0x02, 0x03]);
    serial.queueResponse(expected);
    
    await serial.open();
    const result = await serial.read(3);
    expect(result).toEqual(expected);
  });
});

describe('MockSerialDriver', () => {
  it('should connect and return MockSerial', async () => {
    const driver = new MockSerialDriver();
    const serial = await driver.connect({} as USBDevice);
    expect(serial).toBeInstanceOf(MockSerial);
  });
});
```

---

## Verification

1. Run frontend tests:

   ```bash
   cd praxis/web-client && npm test -- --include='**/serial*'
   ```

2. Check TypeScript compilation:

   ```bash
   cd praxis/web-client && npm run build
   ```

---

## Success Criteria

- [x] `ISerial` interface defined
- [x] `MockSerial` implementation for testing
- [x] FTDI driver refactored to implement interface
- [x] Driver registry for device→driver mapping
- [x] Documentation in README
- [x] All tests pass
