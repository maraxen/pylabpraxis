/**
 * FTDI WebUSB Serial Driver
 *
 * Implements serial communication over FTDI USB-to-Serial chips using WebUSB.
 * This is a TypeScript interface layer that complements the Python-side driver
 * in web_serial_shim.py.
 *
 * Supported FTDI chips:
 * - FT232R (0x0403:0x6001)
 * - FT2232 (0x0403:0x6010)
 * - FT232H (0x0403:0x6014)
 * - FT232BM (0x0403:0x6001)
 *
 * Note: The actual FTDI protocol implementation currently runs in Python/Pyodide.
 * This TypeScript driver provides the interface layer for future migration to
 * main-thread execution (Phase B).
 */

import { ISerial, ISerialDriver, SerialOpenOptions, DeviceFilter } from './serial-interface';

// FTDI USB Vendor ID
const FTDI_VENDOR_ID = 0x0403;

// Common FTDI baud rate divisors
const BAUD_RATE_DIVISORS: Record<number, [number, number]> = {
    9600: [0x4138, 0x0000],
    19200: [0x809c, 0x0000],
    38400: [0xc04e, 0x0000],
    57600: [0x0034, 0x0000],
    115200: [0x001a, 0x0000],
    125000: [0x0018, 0x0000], // CLARIOstar uses this
    230400: [0x000d, 0x0000],
};

/**
 * FTDI Serial implementation using WebUSB.
 */
export class FtdiSerial implements ISerial {
    private device: USBDevice;
    private _isOpen = false;
    private endpointIn = 1;
    private endpointOut = 2;
    private baudRate = 9600;

    constructor(device: USBDevice) {
        this.device = device;
    }

    get isOpen(): boolean {
        return this._isOpen;
    }

    async open(options?: SerialOpenOptions): Promise<void> {
        if (this._isOpen) {
            throw new Error('FTDI port is already open');
        }

        this.baudRate = options?.baudRate ?? 9600;

        try {
            // Open device
            await this.device.open();

            // Select configuration
            if (this.device.configuration === null) {
                await this.device.selectConfiguration(1);
            }

            // Claim interface 0
            await this.device.claimInterface(0);

            // Reset device
            await this.device.controlTransferOut({
                requestType: 'vendor',
                recipient: 'device',
                request: 0, // SIO_RESET
                value: 0,
                index: 0,
            });

            // Set baud rate
            await this.setBaudRate(this.baudRate);

            // Set data characteristics (8N1)
            await this.setDataCharacteristics(
                options?.dataBits ?? 8,
                options?.stopBits ?? 1,
                options?.parity ?? 'none'
            );

            // Find endpoints
            this.discoverEndpoints();

            this._isOpen = true;
            console.log(`[FtdiSerial] Opened device at ${this.baudRate} baud`);
        } catch (error) {
            // Clean up on error
            try {
                await this.device.close();
            } catch {
                // Ignore cleanup errors
            }
            throw new Error(`Failed to open FTDI device: ${error}`);
        }
    }

    async close(): Promise<void> {
        if (!this._isOpen) {
            return;
        }

        try {
            await this.device.releaseInterface(0);
            await this.device.close();
        } finally {
            this._isOpen = false;
        }
    }

    async read(length: number): Promise<Uint8Array> {
        if (!this._isOpen) {
            throw new Error('Port is not open');
        }

        try {
            const result = await this.device.transferIn(this.endpointIn, length + 2);

            if (result.status === 'ok' && result.data && result.data.byteLength > 2) {
                // FTDI adds 2 modem status bytes at the start of each packet
                const dataView = result.data;
                const payload = new Uint8Array(dataView.byteLength - 2);
                for (let i = 2; i < dataView.byteLength; i++) {
                    payload[i - 2] = dataView.getUint8(i);
                }
                return payload;
            }

            return new Uint8Array(0);
        } catch (error) {
            console.error('[FtdiSerial] Read error:', error);
            return new Uint8Array(0);
        }
    }

    async write(data: Uint8Array): Promise<void> {
        if (!this._isOpen) {
            throw new Error('Port is not open');
        }

        try {
            // Cast to BufferSource for WebUSB API compatibility
            const result = await this.device.transferOut(this.endpointOut, data as any);
            if (result.status !== 'ok') {
                throw new Error(`Write failed with status: ${result.status}`);
            }
        } catch (error) {
            throw new Error(`FTDI write failed: ${error}`);
        }
    }


    // ==================== Private Methods ====================

    private async setBaudRate(baudRate: number): Promise<void> {
        const divisor = BAUD_RATE_DIVISORS[baudRate] ?? BAUD_RATE_DIVISORS[9600];

        await this.device.controlTransferOut({
            requestType: 'vendor',
            recipient: 'device',
            request: 3, // SIO_SET_BAUD_RATE
            value: divisor[0],
            index: divisor[1],
        });
    }

    private async setDataCharacteristics(
        dataBits: 7 | 8,
        stopBits: 1 | 2,
        parity: 'none' | 'even' | 'odd'
    ): Promise<void> {
        let value = dataBits;

        // Parity
        if (parity === 'odd') {
            value |= 1 << 8;
        } else if (parity === 'even') {
            value |= 2 << 8;
        }

        // Stop bits
        if (stopBits === 2) {
            value |= 2 << 11;
        }

        await this.device.controlTransferOut({
            requestType: 'vendor',
            recipient: 'device',
            request: 4, // SIO_SET_DATA
            value: value,
            index: 0,
        });
    }

    private discoverEndpoints(): void {
        const config = this.device.configuration;
        if (!config?.interfaces) return;

        const iface = config.interfaces[0];
        if (!iface?.alternate?.endpoints) return;

        for (const endpoint of iface.alternate.endpoints) {
            if (endpoint.direction === 'in') {
                this.endpointIn = endpoint.endpointNumber;
            } else if (endpoint.direction === 'out') {
                this.endpointOut = endpoint.endpointNumber;
            }
        }
    }
}

/**
 * FTDI Serial Driver.
 *
 * Supports common FTDI USB-to-Serial chips.
 */
export class FtdiSerialDriver implements ISerialDriver {
    readonly driverName = 'FTDI';

    readonly supportedDevices: DeviceFilter[] = [
        { vendorId: FTDI_VENDOR_ID, productId: 0x6001 }, // FT232R, FT232BM
        { vendorId: FTDI_VENDOR_ID, productId: 0x6010 }, // FT2232
        { vendorId: FTDI_VENDOR_ID, productId: 0x6014 }, // FT232H
        { vendorId: FTDI_VENDOR_ID, productId: 0x6015 }, // FT-X series
        { vendorId: FTDI_VENDOR_ID, productId: 0xbb68 }, // CLARIOstar (custom PID)
    ];

    async connect(device: USBDevice): Promise<ISerial> {
        return new FtdiSerial(device);
    }

    /**
     * Check if a device is an FTDI device.
     */
    static isFtdiDevice(vendorId: number): boolean {
        return vendorId === FTDI_VENDOR_ID;
    }
}
