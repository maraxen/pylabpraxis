/**
 * Serial Driver Registry
 *
 * Central registry for device→driver mapping. Automatically loads known drivers
 * and provides lookup functionality to find the appropriate driver for a given
 * USB device.
 */

import { ISerialDriver, DeviceFilter } from './serial-interface';
import { FtdiSerialDriver } from './ftdi-web-serial';
import { MockSerialDriver } from './mock-serial';

// Registry of all available drivers
const drivers: ISerialDriver[] = [];

// Track if we've been initialized
let initialized = false;

/**
 * Initialize the driver registry with default drivers.
 */
function initializeRegistry(): void {
    if (initialized) return;

    // Register FTDI driver
    drivers.push(new FtdiSerialDriver());

    // Add mock driver in test mode
    if (isTestMode()) {
        drivers.push(new MockSerialDriver());
        console.debug('[DriverRegistry] Test mode: MockSerialDriver registered');
    }

    initialized = true;
    console.debug(`[DriverRegistry] Initialized with ${drivers.length} drivers`);
}

/**
 * Check if we're in test mode.
 */
function isTestMode(): boolean {
    if (typeof window === 'undefined') {
        return false;
    }
    return !!(window as unknown as { __PRAXIS_TEST_MODE__?: boolean }).__PRAXIS_TEST_MODE__;
}

/**
 * Find a driver that supports the given device.
 *
 * @param vendorId USB Vendor ID
 * @param productId USB Product ID
 * @returns The matching driver, or undefined if none found
 */
export function findDriverForDevice(
    vendorId: number,
    productId: number
): ISerialDriver | undefined {
    initializeRegistry();

    return drivers.find((driver) =>
        driver.supportedDevices.some(
            (filter) => filter.vendorId === vendorId && filter.productId === productId
        )
    );
}

/**
 * Find a driver by its name.
 *
 * @param name Driver name (e.g., 'FTDI', 'MockSerial')
 * @returns The matching driver, or undefined if none found
 */
export function findDriverByName(name: string): ISerialDriver | undefined {
    initializeRegistry();
    return drivers.find((driver) => driver.driverName === name);
}

/**
 * Register a custom driver.
 *
 * @param driver The driver to register
 */
export function registerDriver(driver: ISerialDriver): void {
    initializeRegistry();

    // Check for duplicate names
    if (drivers.some((d) => d.driverName === driver.driverName)) {
        console.warn(`[DriverRegistry] Driver "${driver.driverName}" already registered`);
        return;
    }

    drivers.push(driver);
    console.debug(`[DriverRegistry] Registered driver: ${driver.driverName}`);
}

/**
 * Unregister a driver by name.
 *
 * @param name Driver name to remove
 * @returns true if driver was found and removed
 */
export function unregisterDriver(name: string): boolean {
    const index = drivers.findIndex((d) => d.driverName === name);
    if (index >= 0) {
        drivers.splice(index, 1);
        return true;
    }
    return false;
}

/**
 * Get all registered drivers.
 */
export function getAllDrivers(): readonly ISerialDriver[] {
    initializeRegistry();
    return [...drivers];
}

/**
 * Get all supported device filters across all drivers.
 */
export function getAllSupportedDevices(): DeviceFilter[] {
    initializeRegistry();
    return drivers.flatMap((driver) => driver.supportedDevices);
}

/**
 * Enable test mode programmatically.
 * This registers the MockSerialDriver if not already registered.
 */
export function enableTestMode(): void {
    if (typeof window !== 'undefined') {
        (window as unknown as { __PRAXIS_TEST_MODE__: boolean }).__PRAXIS_TEST_MODE__ = true;
    }

    // Register mock driver if not already present
    if (!drivers.some((d) => d.driverName === 'MockSerial')) {
        drivers.push(new MockSerialDriver());
        console.debug('[DriverRegistry] Test mode enabled: MockSerialDriver registered');
    }
}

/**
 * Reset the registry (primarily for testing).
 */
export function resetRegistry(): void {
    drivers.length = 0;
    initialized = false;
}
