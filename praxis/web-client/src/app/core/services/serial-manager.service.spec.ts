import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { SerialManagerService, SerialRequest, SerialResponse } from './serial-manager.service';
import { MockSerial, MockSerialDriver } from '../../features/playground/drivers/mock-serial';
import { registerDriver, resetRegistry, enableTestMode, findDriverByName, unregisterDriver } from '../../features/playground/drivers/driver-registry';

// Mock BroadcastChannel
class MockBroadcastChannel {
    name: string;
    onmessage: ((event: MessageEvent) => void) | null = null;
    private static channels: Map<string, MockBroadcastChannel[]> = new Map();
    private static testChannels: Set<MockBroadcastChannel> = new Set();

    constructor(name: string) {
        this.name = name;
        const existing = MockBroadcastChannel.channels.get(name) || [];
        existing.push(this);
        MockBroadcastChannel.channels.set(name, existing);
    }

    postMessage(data: unknown): void {
        const channels = MockBroadcastChannel.channels.get(this.name) || [];
        for (const ch of channels) {
            if (ch !== this && ch.onmessage) {
                ch.onmessage(new MessageEvent('message', { data }));
            }
        }
    }

    close(): void {
        const channels = MockBroadcastChannel.channels.get(this.name) || [];
        const idx = channels.indexOf(this);
        if (idx >= 0) channels.splice(idx, 1);
        MockBroadcastChannel.testChannels.delete(this);
    }

    static reset(): void {
        this.channels.clear();
        this.testChannels.clear();
    }

    // Mark this channel as a test channel (for filtering in simulateMessage)
    markAsTestChannel(): this {
        MockBroadcastChannel.testChannels.add(this);
        return this;
    }

    // Helper to simulate message only to non-test channels (i.e., the service)
    static simulateMessage(channelName: string, data: unknown): void {
        const channels = this.channels.get(channelName) || [];
        for (const ch of channels) {
            // Only send to service channels, not test channels
            if (!this.testChannels.has(ch) && ch.onmessage) {
                ch.onmessage(new MessageEvent('message', { data }));
            }
        }
    }
}

// Mock navigator.usb
const mockUsbDevice = {
    vendorId: 0xFFFF,
    productId: 0xFFFF,
    open: vi.fn(),
    close: vi.fn(),
    configuration: {
        interfaces: [{
            alternate: {
                endpoints: [
                    { direction: 'in', endpointNumber: 1 },
                    { direction: 'out', endpointNumber: 2 },
                ]
            }
        }]
    },
    selectConfiguration: vi.fn(),
    claimInterface: vi.fn(),
    controlTransferOut: vi.fn(),
    transferIn: vi.fn().mockResolvedValue({ status: 'ok', data: new DataView(new ArrayBuffer(0)) }),
    transferOut: vi.fn().mockResolvedValue({ status: 'ok' }),
} as unknown as USBDevice;

describe('SerialManagerService', () => {
    let service: SerialManagerService;
    let mockDriver: MockSerialDriver;

    beforeEach(() => {
        // Setup mocks
        vi.stubGlobal('BroadcastChannel', MockBroadcastChannel);
        vi.stubGlobal('navigator', {
            usb: {
                getDevices: vi.fn().mockResolvedValue([mockUsbDevice]),
                requestDevice: vi.fn().mockResolvedValue(mockUsbDevice),
            }
        });

        MockBroadcastChannel.reset();
        resetRegistry();

        // Create and register our mock driver with the test VID/PID
        mockDriver = new MockSerialDriver();
        registerDriver(mockDriver);

        // Create service
        service = new SerialManagerService();
    });

    afterEach(() => {
        service.ngOnDestroy();
        vi.unstubAllGlobals();
    });

    describe('initialization', () => {
        it('should initialize with BroadcastChannel', () => {
            expect(service).toBeDefined();
        });

        it('should have no active connections initially', () => {
            expect(service.getActiveConnections()).toHaveLength(0);
        });
    });

    describe('connection management', () => {
        it('should connect to a device', async () => {
            const deviceId = await service.connect(0xFFFF, 0xFFFF, { baudRate: 9600 });

            expect(deviceId).toBe('usb-ffff-ffff');
            expect(service.isConnected(deviceId)).toBe(true);
        });

        it('should emit status events on connect', async () => {
            const statuses: string[] = [];
            service.status$.subscribe(event => statuses.push(event.status));

            await service.connect(0xFFFF, 0xFFFF);

            expect(statuses).toContain('connecting');
            expect(statuses).toContain('connected');
        });

        it('should disconnect from a device', async () => {
            const deviceId = await service.connect(0xFFFF, 0xFFFF);
            await service.disconnect(deviceId);

            expect(service.isConnected(deviceId)).toBe(false);
        });

        it('should emit disconnected status on disconnect', async () => {
            const statuses: string[] = [];
            service.status$.subscribe(event => statuses.push(event.status));

            const deviceId = await service.connect(0xFFFF, 0xFFFF);
            await service.disconnect(deviceId);

            expect(statuses).toContain('disconnected');
        });

        it('should not throw when disconnecting non-existent device', async () => {
            await expect(service.disconnect('non-existent')).resolves.not.toThrow();
        });
    });

    describe('read/write operations', () => {
        it('should throw when writing to disconnected device', async () => {
            await expect(
                service.write('non-existent', new Uint8Array([0x01]))
            ).rejects.toThrow('not connected');
        });

        it('should throw when reading from disconnected device', async () => {
            await expect(
                service.read('non-existent', 10)
            ).rejects.toThrow('not connected');
        });

        it('should write to connected device', async () => {
            const deviceId = await service.connect(0xFFFF, 0xFFFF);
            const mockSerial = mockDriver.getLastMockSerial()!;

            await service.write(deviceId, new Uint8Array([0x01, 0x02]));

            expect(mockSerial.getWriteLog()).toHaveLength(1);
        });

        it('should read from connected device', async () => {
            const deviceId = await service.connect(0xFFFF, 0xFFFF);
            const mockSerial = mockDriver.getLastMockSerial()!;
            mockSerial.queueResponse(new Uint8Array([0x01, 0x02, 0x03]));

            const result = await service.read(deviceId, 10);

            expect(result).toEqual(new Uint8Array([0x01, 0x02, 0x03]));
        });
    });

    describe('worker message handling', () => {
        it('should respond to serial:open request', async () => {
            const responses: SerialResponse[] = [];
            const workerChannel = new MockBroadcastChannel('praxis_serial').markAsTestChannel();
            workerChannel.onmessage = (e) => responses.push(e.data);

            const request: SerialRequest = {
                type: 'serial:open',
                requestId: 'test-1',
                vendorId: 0xFFFF,
                productId: 0xFFFF,
                options: { baudRate: 9600 },
            };

            MockBroadcastChannel.simulateMessage('praxis_serial', request);

            // Wait for async processing
            await new Promise(resolve => setTimeout(resolve, 50));

            expect(responses).toHaveLength(1);
            expect(responses[0].success).toBe(true);
            expect(responses[0].requestId).toBe('test-1');
        });

        it('should respond to serial:write request', async () => {
            // First connect
            await service.connect(0xFFFF, 0xFFFF);

            const responses: SerialResponse[] = [];
            const workerChannel = new MockBroadcastChannel('praxis_serial').markAsTestChannel();
            workerChannel.onmessage = (e) => responses.push(e.data);

            const request: SerialRequest = {
                type: 'serial:write',
                requestId: 'test-2',
                deviceId: 'usb-ffff-ffff',
                data: [0x01, 0x02, 0x03],
            };

            MockBroadcastChannel.simulateMessage('praxis_serial', request);

            await new Promise(resolve => setTimeout(resolve, 50));

            expect(responses).toHaveLength(1);
            expect(responses[0].success).toBe(true);
        });

        it('should respond to serial:read request', async () => {
            await service.connect(0xFFFF, 0xFFFF);
            const mockSerial = mockDriver.getLastMockSerial()!;
            mockSerial.queueResponse(new Uint8Array([0xAA, 0xBB]));

            const responses: SerialResponse[] = [];
            const workerChannel = new MockBroadcastChannel('praxis_serial').markAsTestChannel();
            workerChannel.onmessage = (e) => responses.push(e.data);

            const request: SerialRequest = {
                type: 'serial:read',
                requestId: 'test-3',
                deviceId: 'usb-ffff-ffff',
                length: 10,
            };

            MockBroadcastChannel.simulateMessage('praxis_serial', request);

            await new Promise(resolve => setTimeout(resolve, 50));

            expect(responses).toHaveLength(1);
            expect(responses[0].success).toBe(true);
            expect(responses[0].data).toEqual([0xAA, 0xBB]);
        });

        it('should respond with error for failed request', async () => {
            const responses: SerialResponse[] = [];
            const workerChannel = new MockBroadcastChannel('praxis_serial').markAsTestChannel();
            workerChannel.onmessage = (e) => responses.push(e.data);

            const request: SerialRequest = {
                type: 'serial:write',
                requestId: 'test-error',
                deviceId: 'non-existent',
                data: [0x01],
            };

            MockBroadcastChannel.simulateMessage('praxis_serial', request);

            await new Promise(resolve => setTimeout(resolve, 50));

            expect(responses).toHaveLength(1);
            expect(responses[0].success).toBe(false);
            expect(responses[0].error).toContain('not connected');
        });
    });

    describe('getActiveConnections', () => {
        it('should return all active connections', async () => {
            await service.connect(0xFFFF, 0xFFFF);

            const connections = service.getActiveConnections();

            expect(connections).toHaveLength(1);
            expect(connections[0].status).toBe('connected');
            expect(connections[0].vendorId).toBe(0xFFFF);
        });

        it('should update when connections change', async () => {
            const deviceId = await service.connect(0xFFFF, 0xFFFF);
            expect(service.getActiveConnections()).toHaveLength(1);

            await service.disconnect(deviceId);
            expect(service.getActiveConnections()).toHaveLength(0);
        });
    });
});
