/**
 * REPL Drivers Module
 *
 * Provides serial/USB driver abstractions for hardware communication in the browser.
 */

// Interfaces
export type {
    ISerial,
    ISerialDriver,
    SerialOpenOptions,
    DeviceFilter,
} from './serial-interface';

// Implementations
export { MockSerial, MockSerialDriver } from './mock-serial';
export { FtdiSerial, FtdiSerialDriver } from './ftdi-web-serial';

// Registry
export {
    findDriverForDevice,
    findDriverByName,
    registerDriver,
    unregisterDriver,
    getAllDrivers,
    getAllSupportedDevices,
    enableTestMode,
    resetRegistry,
} from './driver-registry';
