/**
 * Serial Interface Tests
 *
 * Unit tests for MockSerial, MockSerialDriver, and driver registry.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { MockSerial, MockSerialDriver } from './mock-serial';
import {
    findDriverForDevice,
    findDriverByName,
    registerDriver,
    unregisterDriver,
    getAllDrivers,
    resetRegistry,
    enableTestMode,
} from './driver-registry';
import { ISerialDriver } from './serial-interface';

describe('MockSerial', () => {
    let serial: MockSerial;

    beforeEach(() => {
        serial = new MockSerial();
    });

    describe('open/close', () => {
        it('should start closed', () => {
            expect(serial.isOpen).toBe(false);
        });

        it('should open successfully', async () => {
            await serial.open();
            expect(serial.isOpen).toBe(true);
        });

        it('should close successfully after opening', async () => {
            await serial.open();
            await serial.close();
            expect(serial.isOpen).toBe(false);
        });

        it('should throw when opening twice', async () => {
            await serial.open();
            await expect(serial.open()).rejects.toThrow('already open');
        });

        it('should throw when closing without opening', async () => {
            await expect(serial.close()).rejects.toThrow('not open');
        });
    });

    describe('read', () => {
        it('should throw when reading without opening', async () => {
            await expect(serial.read(10)).rejects.toThrow('not open');
        });

        it('should return empty when no responses queued', async () => {
            await serial.open();
            const result = await serial.read(10);
            expect(result.length).toBe(0);
        });

        it('should return queued responses', async () => {
            const expected = new Uint8Array([0x01, 0x02, 0x03]);
            serial.queueResponse(expected);

            await serial.open();
            const result = await serial.read(10);
            expect(result).toEqual(expected);
        });

        it('should return responses in FIFO order', async () => {
            const first = new Uint8Array([0x01]);
            const second = new Uint8Array([0x02]);
            serial.queueResponses([first, second]);

            await serial.open();
            expect(await serial.read(10)).toEqual(first);
            expect(await serial.read(10)).toEqual(second);
        });

        it('should truncate response to requested length', async () => {
            serial.queueResponse(new Uint8Array([0x01, 0x02, 0x03, 0x04, 0x05]));

            await serial.open();
            const result = await serial.read(3);
            expect(result.length).toBe(3);
            expect(result).toEqual(new Uint8Array([0x01, 0x02, 0x03]));
        });
    });

    describe('write', () => {
        it('should throw when writing without opening', async () => {
            await expect(serial.write(new Uint8Array([0x01]))).rejects.toThrow('not open');
        });

        it('should log writes', async () => {
            const data = new Uint8Array([0x01, 0x02, 0x03]);

            await serial.open();
            await serial.write(data);

            const log = serial.getWriteLog();
            expect(log.length).toBe(1);
            expect(log[0]).toEqual(data);
        });

        it('should accumulate writes in log', async () => {
            await serial.open();
            await serial.write(new Uint8Array([0x01]));
            await serial.write(new Uint8Array([0x02]));

            expect(serial.getWriteLog().length).toBe(2);
        });
    });

    describe('reset', () => {
        it('should reset all state', async () => {
            serial.queueResponse(new Uint8Array([0x01]));
            await serial.open();
            await serial.write(new Uint8Array([0x02]));

            serial.reset();

            expect(serial.isOpen).toBe(false);
            expect(serial.getWriteLog().length).toBe(0);
        });
    });
});

describe('MockSerialDriver', () => {
    it('should have correct driver name', () => {
        const driver = new MockSerialDriver();
        expect(driver.driverName).toBe('MockSerial');
    });

    it('should have fictional VID/PID', () => {
        const driver = new MockSerialDriver();
        expect(driver.supportedDevices).toEqual([
            { vendorId: 0xffff, productId: 0xffff },
        ]);
    });

    it('should return MockSerial instance on connect', async () => {
        const driver = new MockSerialDriver();
        const mockDevice = {} as USBDevice;

        const serial = await driver.connect(mockDevice);
        expect(serial).toBeInstanceOf(MockSerial);
    });

    it('should track last created mock serial', async () => {
        const driver = new MockSerialDriver();
        const mockDevice = {} as USBDevice;

        await driver.connect(mockDevice);
        expect(driver.getLastMockSerial()).toBeInstanceOf(MockSerial);
    });
});

describe('DriverRegistry', () => {
    beforeEach(() => {
        resetRegistry();
    });

    describe('findDriverForDevice', () => {
        it('should find FTDI driver for known VID/PID', () => {
            const driver = findDriverForDevice(0x0403, 0x6001);
            expect(driver).toBeDefined();
            expect(driver?.driverName).toBe('FTDI');
        });

        it('should return undefined for unknown VID/PID', () => {
            const driver = findDriverForDevice(0x1234, 0x5678);
            expect(driver).toBeUndefined();
        });
    });

    describe('findDriverByName', () => {
        it('should find driver by name', () => {
            const driver = findDriverByName('FTDI');
            expect(driver).toBeDefined();
            expect(driver?.driverName).toBe('FTDI');
        });

        it('should return undefined for unknown name', () => {
            const driver = findDriverByName('UnknownDriver');
            expect(driver).toBeUndefined();
        });
    });

    describe('registerDriver', () => {
        it('should register custom driver', () => {
            const customDriver: ISerialDriver = {
                driverName: 'CustomDriver',
                supportedDevices: [{ vendorId: 0x1234, productId: 0x5678 }],
                connect: vi.fn(),
            };

            registerDriver(customDriver);

            expect(findDriverByName('CustomDriver')).toBe(customDriver);
        });

        it('should not register duplicate driver names', () => {
            const customDriver: ISerialDriver = {
                driverName: 'FTDI', // Already registered
                supportedDevices: [],
                connect: vi.fn(),
            };

            const countBefore = getAllDrivers().length;
            registerDriver(customDriver);
            const countAfter = getAllDrivers().length;

            expect(countAfter).toBe(countBefore);
        });
    });

    describe('unregisterDriver', () => {
        it('should unregister driver by name', () => {
            expect(findDriverByName('FTDI')).toBeDefined();

            const result = unregisterDriver('FTDI');

            expect(result).toBe(true);
            expect(findDriverByName('FTDI')).toBeUndefined();
        });

        it('should return false for non-existent driver', () => {
            const result = unregisterDriver('NonExistent');
            expect(result).toBe(false);
        });
    });

    describe('enableTestMode', () => {
        it('should register MockSerialDriver', () => {
            expect(findDriverByName('MockSerial')).toBeUndefined();

            enableTestMode();

            expect(findDriverByName('MockSerial')).toBeDefined();
        });

        it('should find mock driver for mock VID/PID', () => {
            enableTestMode();

            const driver = findDriverForDevice(0xffff, 0xffff);
            expect(driver?.driverName).toBe('MockSerial');
        });
    });
});
