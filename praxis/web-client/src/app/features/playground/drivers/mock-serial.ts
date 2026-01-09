/**
 * Mock Serial Driver for Testing
 *
 * Provides a mock implementation of ISerial and ISerialDriver for unit tests
 * and development without physical hardware.
 */

import { ISerial, ISerialDriver, SerialOpenOptions, DeviceFilter } from './serial-interface';

/**
 * Mock serial port implementation.
 *
 * Supports queuing responses that will be returned by read() calls.
 * Useful for testing device communication protocols.
 */
export class MockSerial implements ISerial {
    private _isOpen = false;
    private responseQueue: Uint8Array[] = [];
    private writeLog: Uint8Array[] = [];

    get isOpen(): boolean {
        return this._isOpen;
    }

    async open(_options?: SerialOpenOptions): Promise<void> {
        if (this._isOpen) {
            throw new Error('Port is already open');
        }
        this._isOpen = true;
    }

    async close(): Promise<void> {
        if (!this._isOpen) {
            throw new Error('Port is not open');
        }
        this._isOpen = false;
    }

    async read(length: number): Promise<Uint8Array> {
        if (!this._isOpen) {
            throw new Error('Port is not open');
        }

        if (this.responseQueue.length > 0) {
            const response = this.responseQueue.shift()!;
            // Return up to `length` bytes
            return response.slice(0, length);
        }

        // Return empty array if no queued responses
        return new Uint8Array(0);
    }

    async write(data: Uint8Array): Promise<void> {
        if (!this._isOpen) {
            throw new Error('Port is not open');
        }

        // Log writes for test verification
        this.writeLog.push(new Uint8Array(data));
        console.debug('[MockSerial] Write:', data);
    }

    // ==================== Test Helpers ====================

    /**
     * Queue a response to be returned by the next read() call.
     */
    queueResponse(data: Uint8Array): void {
        this.responseQueue.push(data);
    }

    /**
     * Queue multiple responses.
     */
    queueResponses(responses: Uint8Array[]): void {
        this.responseQueue.push(...responses);
    }

    /**
     * Get all data that has been written to this port.
     */
    getWriteLog(): Uint8Array[] {
        return [...this.writeLog];
    }

    /**
     * Clear the write log.
     */
    clearWriteLog(): void {
        this.writeLog = [];
    }

    /**
     * Clear all queued responses.
     */
    clearResponseQueue(): void {
        this.responseQueue = [];
    }

    /**
     * Reset the mock to initial state.
     */
    reset(): void {
        this._isOpen = false;
        this.responseQueue = [];
        this.writeLog = [];
    }
}

/**
 * Mock serial driver for testing.
 *
 * Uses a fictional VID/PID that won't conflict with real devices.
 */
export class MockSerialDriver implements ISerialDriver {
    readonly driverName = 'MockSerial';

    // Fictional VID/PID for test devices
    readonly supportedDevices: DeviceFilter[] = [
        { vendorId: 0xffff, productId: 0xffff },
    ];

    private mockSerial: MockSerial | null = null;

    async connect(_device: USBDevice): Promise<ISerial> {
        this.mockSerial = new MockSerial();
        return this.mockSerial;
    }

    /**
     * Get the last created mock serial instance for test verification.
     */
    getLastMockSerial(): MockSerial | null {
        return this.mockSerial;
    }
}
