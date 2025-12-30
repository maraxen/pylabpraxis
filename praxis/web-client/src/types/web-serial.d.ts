/**
 * WebSerial API Type Declarations
 *
 * These types extend the Navigator interface with WebSerial API support.
 * The WebSerial API allows web applications to communicate with serial devices.
 */

interface SerialPortInfo {
    usbVendorId?: number;
    usbProductId?: number;
}

interface SerialOptions {
    baudRate: number;
    dataBits?: 8 | 7;
    stopBits?: 1 | 2;
    parity?: 'none' | 'even' | 'odd';
    bufferSize?: number;
    flowControl?: 'none' | 'hardware';
}

interface SerialPort {
    readonly readable: ReadableStream<Uint8Array> | null;
    readonly writable: WritableStream<Uint8Array> | null;
    getInfo(): SerialPortInfo;
    open(options: SerialOptions): Promise<void>;
    close(): Promise<void>;
    setSignals(signals: SerialOutputSignals): Promise<void>;
    getSignals(): Promise<SerialInputSignals>;
}

interface SerialOutputSignals {
    dataTerminalReady?: boolean;
    requestToSend?: boolean;
    break?: boolean;
}

interface SerialInputSignals {
    dataCarrierDetect: boolean;
    clearToSend: boolean;
    ringIndicator: boolean;
    dataSetReady: boolean;
}

interface SerialPortRequestOptions {
    filters?: SerialPortFilter[];
}

interface SerialPortFilter {
    usbVendorId?: number;
    usbProductId?: number;
}

interface Serial extends EventTarget {
    onconnect: ((this: Serial, ev: Event) => void) | null;
    ondisconnect: ((this: Serial, ev: Event) => void) | null;
    getPorts(): Promise<SerialPort[]>;
    requestPort(options?: SerialPortRequestOptions): Promise<SerialPort>;
}

interface Navigator {
    readonly serial: Serial;
}
