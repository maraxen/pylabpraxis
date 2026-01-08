# FTDI Driver Architecture Refactor - Research & Implementation

## Current Status

**Working Solution:** CLARIOstar connectivity is functional using a Python-side FTDI driver in `web_serial_shim.py`.

**Problem:** The current implementation has architectural concerns:

1. **Security:** Python code directly accesses `navigator.usb` and performs low-level USB control transfers
2. **Portability:** Unclear if this works outside localhost (Pyodide security context)
3. **Maintainability:** FTDI protocol logic duplicated in Python instead of leveraging existing TypeScript/browser capabilities
4. **Generalizability:** Hard to extend to other non-CDC-ACM devices

## Proposed Solution: Frontend Driver Architecture

### Concept

Move the FTDI driver logic to TypeScript (Angular/UI thread) and expose a **message-passing interface** to Python.

### Architecture Options

#### Option 1: Remote Driver Pattern (Recommended)

```
┌─────────────────────────────────────────────────────────────┐
│ Pyodide Worker (Python)                                     │
│  ├─ WebSerial shim                                          │
│  │   └─ Sends JSON commands: {type: "write", data: [...]}  │
│  └─ Receives responses: {type: "read", data: [...]}        │
└──────────────────┬──────────────────────────────────────────┘
                   │ postMessage / BroadcastChannel
┌──────────────────▼──────────────────────────────────────────┐
│ Angular UI Thread                                           │
│  ├─ FtdiWebSerialDriver (TypeScript)                        │
│  │   ├─ Handles WebUSB device access                        │
│  │   ├─ Implements FTDI protocol (baud, control transfers)  │
│  │   └─ Manages device lifecycle                            │
│  └─ Message Router                                          │
│      └─ Routes commands to appropriate driver               │
└─────────────────────────────────────────────────────────────┘
```

**Pros:**

- ✅ No direct USB access from Python (safer)
- ✅ TypeScript can be tested/debugged independently
- ✅ Easier to extend to other device types
- ✅ Better separation of concerns

**Cons:**

- ❌ Async message passing adds latency
- ❌ More complex architecture
- ❌ Need to handle message serialization

#### Option 2: Hybrid Approach

Keep Python-side driver but add **validation layer** in TypeScript:

- TypeScript authorizes device and validates commands
- Python sends "intent" (e.g., "set_baud_rate")
- TypeScript approves and executes

**Pros:**

- ✅ Simpler than full remote driver
- ✅ Adds security validation

**Cons:**

- ❌ Still has Python USB access
- ❌ Doesn't solve portability concerns

#### Option 3: WebAssembly FTDI Driver

Compile a minimal FTDI driver to WASM and load it in Pyodide.

**Pros:**

- ✅ Native performance
- ✅ Can reuse existing C/C++ FTDI libraries

**Cons:**

- ❌ High complexity
- ❌ Still needs WebUSB access from Python context
- ❌ Overkill for this use case

## Research Questions

### 1. Pyodide Security Context

**Question:** Does `navigator.usb` work in Pyodide when NOT on localhost?

**Investigation:**

- Test current implementation on `https://` domain
- Check if WebUSB permissions persist across Worker boundary
- Review Pyodide security model documentation

**Expected Answer:** WebUSB requires secure context (HTTPS or localhost). Permissions granted in main thread *should* be accessible in Worker via `navigator.usb.getDevices()`, but this needs verification.

### 2. Message Passing Performance

**Question:** What is the latency overhead of postMessage for serial communication?

**Investigation:**

- Benchmark: Direct Python USB vs. postMessage round-trip
- Test with typical CLARIOstar command/response cycle
- Measure impact on protocol timing requirements

**Acceptable Threshold:** <10ms overhead per command (CLARIOstar typically has 100ms+ response times)

### 3. Existing Solutions

**Question:** Are there existing libraries/patterns for this?

**Investigation:**

- Research `webusb-ftdi` (mentioned in original handoff)
- Check if PyLabRobot has remote driver patterns
- Look for Pyodide + WebUSB examples

### 4. Generalization Strategy

**Question:** How do we support multiple device types (FTDI, CDC-ACM, CH340, etc.)?

**Proposed Design:**

```typescript
interface SerialDriver {
  open(device: USBDevice, options: SerialOptions): Promise<void>;
  write(data: Uint8Array): Promise<void>;
  read(length: number): Promise<Uint8Array>;
  close(): Promise<void>;
}

class FtdiDriver implements SerialDriver { /* ... */ }
class CdcAcmDriver implements SerialDriver { /* ... */ }

class DriverRegistry {
  static getDriver(device: USBDevice): SerialDriver {
    // Auto-detect based on VID/PID or device class
  }
}
```

## Implementation Plan

### Phase 1: Research & Prototyping (1-2 days)

1. Answer research questions above
2. Create proof-of-concept for Option 1 (Remote Driver)
3. Benchmark performance
4. Document findings

### Phase 2: TypeScript Driver Implementation (2-3 days)

1. Port FTDI logic from `web_serial_shim.py` to `ftdi-driver.ts`
2. Implement message passing protocol
3. Create driver registry/factory
4. Add CDC-ACM driver for comparison

### Phase 3: Python Shim Refactor (1 day)

1. Update `web_serial_shim.py` to use message passing
2. Remove direct USB access
3. Add fallback to current implementation (feature flag)

### Phase 4: Testing & Validation (1-2 days)

1. Test CLARIOstar connectivity
2. Test on non-localhost (if applicable)
3. Performance benchmarks
4. Add unit tests for drivers

### Phase 5: Documentation (1 day)

1. Update architecture docs
2. Add driver development guide
3. Document message protocol

## Security Considerations

### Current Implementation Risks

- **Arbitrary USB Access:** Python code can theoretically access any authorized USB device
- **No Sandboxing:** Control transfers are executed directly without validation
- **Injection Risk:** Malicious code in REPL could abuse USB access

### Proposed Mitigations (Option 1)

- **Whitelist:** TypeScript only accepts commands for pre-authorized devices
- **Command Validation:** Validate all control transfer parameters
- **Rate Limiting:** Prevent USB flooding
- **Audit Log:** Log all USB commands for debugging

## Open Questions for Discussion

1. **Deployment Context:** Will PyLabPraxis ever run on non-localhost? If not, current solution may be acceptable.
2. **Performance Requirements:** What are the latency/throughput requirements for different devices?
3. **Device Support:** Which other devices need support? (CH340, CP2102, etc.)
4. **Backward Compatibility:** Do we need to support the current Python-side driver during transition?

## Success Criteria

- [ ] CLARIOstar connectivity works via frontend driver
- [ ] No direct USB access from Python
- [ ] Performance within 10% of current implementation
- [ ] Extensible to at least 2 other device types
- [ ] Works on HTTPS (if applicable)
- [ ] Comprehensive tests and documentation

## References

- Current implementation: `praxis/web-client/src/assets/shims/web_serial_shim.py`
- WebUSB API: <https://developer.mozilla.org/en-US/docs/Web/API/USB>
- Pyodide Workers: <https://pyodide.org/en/stable/usage/webworker.html>
- FTDI Protocol: <https://www.ftdichip.com/Support/Documents/AppNotes.htm>
