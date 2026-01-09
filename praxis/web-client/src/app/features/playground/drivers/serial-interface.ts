/**
 * Serial Interface Abstraction
 *
 * Provides a common interface for serial communication regardless of the
 * underlying transport (WebSerial, WebUSB/FTDI, mock, etc.).
 */

/**
 * Options for opening a serial connection.
 */
export interface SerialOpenOptions {
    baudRate?: number;
    dataBits?: 7 | 8;
    stopBits?: 1 | 2;
    parity?: 'none' | 'even' | 'odd';
    flowControl?: 'none' | 'hardware';
}

/**
 * Core serial port interface.
 *
 * Represents an open or openable serial connection. Implementations may wrap
 * WebSerial API, WebUSB with FTDI protocol, or mock data for testing.
 */
export interface ISerial {
    /**
     * Open the serial connection with the specified options.
     */
    open(options?: SerialOpenOptions): Promise<void>;

    /**
     * Close the serial connection.
     */
    close(): Promise<void>;

    /**
     * Read up to `length` bytes from the serial port.
     * Returns the data read (may be less than `length` if not enough data available).
     */
    read(length: number): Promise<Uint8Array>;

    /**
     * Write data to the serial port.
     */
    write(data: Uint8Array): Promise<void>;

    /**
     * Whether the serial port is currently open.
     */
    readonly isOpen: boolean;
}

/**
 * Device filter for matching USB devices.
 */
export interface DeviceFilter {
    vendorId: number;
    productId: number;
}

/**
 * Serial driver interface.
 *
 * A driver knows how to connect to specific USB devices and create ISerial
 * instances for communication.
 */
export interface ISerialDriver {
    /**
     * Human-readable name of this driver.
     */
    readonly driverName: string;

    /**
     * List of USB VID/PID pairs this driver supports.
     */
    readonly supportedDevices: DeviceFilter[];

    /**
     * Create a serial connection to the specified device.
     */
    connect(device: USBDevice): Promise<ISerial>;
}
