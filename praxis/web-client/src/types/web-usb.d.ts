/**
 * WebUSB API Type Declarations
 *
 * These types extend the Navigator interface with WebUSB API support.
 * The WebUSB API allows web applications to communicate with USB devices.
 */

interface USBDeviceFilter {
    vendorId?: number;
    productId?: number;
    classCode?: number;
    subclassCode?: number;
    protocolCode?: number;
    serialNumber?: string;
}

interface USBDeviceRequestOptions {
    filters: USBDeviceFilter[];
}

interface USBConfiguration {
    configurationValue: number;
    configurationName?: string;
    interfaces: USBInterface[];
}

interface USBInterface {
    interfaceNumber: number;
    alternate: USBAlternateInterface;
    alternates: USBAlternateInterface[];
    claimed: boolean;
}

interface USBAlternateInterface {
    alternateSetting: number;
    interfaceClass: number;
    interfaceSubclass: number;
    interfaceProtocol: number;
    interfaceName?: string;
    endpoints: USBEndpoint[];
}

interface USBEndpoint {
    endpointNumber: number;
    direction: 'in' | 'out';
    type: 'bulk' | 'interrupt' | 'isochronous';
    packetSize: number;
}

interface USBInTransferResult {
    data?: DataView;
    status: 'ok' | 'stall' | 'babble';
}

interface USBOutTransferResult {
    bytesWritten: number;
    status: 'ok' | 'stall';
}

interface USBDevice {
    readonly usbVersionMajor: number;
    readonly usbVersionMinor: number;
    readonly usbVersionSubminor: number;
    readonly deviceClass: number;
    readonly deviceSubclass: number;
    readonly deviceProtocol: number;
    readonly vendorId: number;
    readonly productId: number;
    readonly deviceVersionMajor: number;
    readonly deviceVersionMinor: number;
    readonly deviceVersionSubminor: number;
    readonly manufacturerName?: string;
    readonly productName?: string;
    readonly serialNumber?: string;
    readonly configuration?: USBConfiguration;
    readonly configurations: USBConfiguration[];
    readonly opened: boolean;

    open(): Promise<void>;
    close(): Promise<void>;
    selectConfiguration(configurationValue: number): Promise<void>;
    claimInterface(interfaceNumber: number): Promise<void>;
    releaseInterface(interfaceNumber: number): Promise<void>;
    selectAlternateInterface(interfaceNumber: number, alternateSetting: number): Promise<void>;
    controlTransferIn(setup: USBControlTransferParameters, length: number): Promise<USBInTransferResult>;
    controlTransferOut(setup: USBControlTransferParameters, data?: BufferSource): Promise<USBOutTransferResult>;
    clearHalt(direction: 'in' | 'out', endpointNumber: number): Promise<void>;
    transferIn(endpointNumber: number, length: number): Promise<USBInTransferResult>;
    transferOut(endpointNumber: number, data: BufferSource): Promise<USBOutTransferResult>;
    isochronousTransferIn(endpointNumber: number, packetLengths: number[]): Promise<USBIsochronousInTransferResult>;
    isochronousTransferOut(endpointNumber: number, data: BufferSource, packetLengths: number[]): Promise<USBIsochronousOutTransferResult>;
    reset(): Promise<void>;
}

interface USBControlTransferParameters {
    requestType: 'standard' | 'class' | 'vendor';
    recipient: 'device' | 'interface' | 'endpoint' | 'other';
    request: number;
    value: number;
    index: number;
}

interface USBIsochronousInTransferPacket {
    data?: DataView;
    status: 'ok' | 'stall' | 'babble';
}

interface USBIsochronousInTransferResult {
    data?: DataView;
    packets: USBIsochronousInTransferPacket[];
}

interface USBIsochronousOutTransferPacket {
    bytesWritten: number;
    status: 'ok' | 'stall';
}

interface USBIsochronousOutTransferResult {
    packets: USBIsochronousOutTransferPacket[];
}

interface USB extends EventTarget {
    onconnect: ((this: USB, ev: USBConnectionEvent) => void) | null;
    ondisconnect: ((this: USB, ev: USBConnectionEvent) => void) | null;
    getDevices(): Promise<USBDevice[]>;
    requestDevice(options: USBDeviceRequestOptions): Promise<USBDevice>;
}

interface USBConnectionEvent extends Event {
    readonly device: USBDevice;
}

interface Navigator {
    readonly usb: USB;
}
