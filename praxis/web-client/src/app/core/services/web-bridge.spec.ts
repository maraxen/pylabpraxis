import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { PythonRuntimeService } from './python-runtime.service';
import { HardwareDiscoveryService } from './hardware-discovery.service';

// Mock Serial Port Interface
const mockReader = {
    read: vi.fn(),
    releaseLock: vi.fn(),
    cancel: vi.fn()
};

const mockWriter = {
    write: vi.fn(),
    releaseLock: vi.fn(),
    close: vi.fn(),
    abort: vi.fn()
};

const mockSerialPort = {
    open: vi.fn(),
    close: vi.fn(),
    readable: {
        getReader: vi.fn().mockReturnValue(mockReader)
    },
    writable: {
        getWriter: vi.fn().mockReturnValue(mockWriter)
    },
    getInfo: vi.fn().mockReturnValue({ usbVendorId: 1234, usbProductId: 5678 })
};

// Mock Worker
class MockWorker {
    onmessage: ((ev: MessageEvent) => any) | null = null;
    postMessage = vi.fn();
    addEventListener = vi.fn();
    removeEventListener = vi.fn();
    terminate = vi.fn();
}

describe('WebBridgeIO E2E Integration (Mocked)', () => {
    let pythonService: PythonRuntimeService;
    let hardwareService: HardwareDiscoveryService;
    let mockWorkerInstance: MockWorker;

    beforeEach(() => {
        console.log('Starting beforeEach setup...');

        // Setup Global Mocks
        mockWorkerInstance = new MockWorker();

        // Mock Worker globally
        vi.stubGlobal('Worker', class {
            constructor() { return mockWorkerInstance; }
        });

        // Mock Navigator Serial
        const mockNavigatorSerial = {
            requestPort: vi.fn().mockResolvedValue(mockSerialPort),
            getPorts: vi.fn().mockResolvedValue([mockSerialPort])
        };

        if (global.navigator) {
            Object.defineProperty(global.navigator, 'serial', {
                value: mockNavigatorSerial,
                writable: true,
                configurable: true
            });
            // We also need to mock USB since service checks it
            Object.defineProperty(global.navigator, 'usb', {
                value: { requestDevice: vi.fn(), getDevices: vi.fn() },
                writable: true,
                configurable: true
            });
        } else {
            vi.stubGlobal('navigator', {
                serial: mockNavigatorSerial,
                usb: { requestDevice: vi.fn(), getDevices: vi.fn() }
            });
        }

        console.log('Configuring TestBed...');
        TestBed.configureTestingModule({
            imports: [HttpClientTestingModule],
            providers: [
                PythonRuntimeService,
                HardwareDiscoveryService
            ]
        });

        console.log('Injecting services...');
        try {
            pythonService = TestBed.inject(PythonRuntimeService);
            hardwareService = TestBed.inject(HardwareDiscoveryService);
            console.log('Injection successful');
        } catch (e) {
            console.error('Injection failed:', e);
            throw e;
        }

        // Reset mocks
        vi.clearAllMocks();
        mockReader.read.mockReset();
        mockWriter.write.mockReset();
        mockSerialPort.open.mockReset();
        mockSerialPort.close.mockReset();
    });

    afterEach(() => {
        vi.restoreAllMocks();
    });

    // Minimal test to verify setup
    it('should initialize services', () => {
        expect(pythonService).toBeTruthy();
        expect(hardwareService).toBeTruthy();
        // Also verify mock connector
        expect(navigator.serial).toBeDefined();
    });

    const SIMULATED_DEVICE_ID = 'serial-test-device';

    async function simulateDeviceDiscovery() {
        const nav: any = navigator;
        nav.serial.requestPort.mockResolvedValue(mockSerialPort);

        const device = await hardwareService.requestSerialPort();

        if (device) {
            return device.id;
        }
        return null;
    }

    it('should open a serial port when receiving "OPEN" command from Python', async () => {
        const deviceId = await simulateDeviceDiscovery();
        expect(deviceId).toBeTruthy();

        const openPayload = {
            command: 'OPEN',
            port_id: deviceId,
            baudRate: 115200
        };

        if (mockWorkerInstance.onmessage) {
            mockWorkerInstance.onmessage({
                data: { type: 'RAW_IO', payload: openPayload }
            } as MessageEvent);
        }

        await new Promise(resolve => setTimeout(resolve, 10));

        expect(mockSerialPort.open).toHaveBeenCalledWith({ baudRate: 115200 });
        expect(hardwareService.isPortOpen(deviceId!)).toBe(true);
    });
});
