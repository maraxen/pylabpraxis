/**
 * Hardware Discovery Service
 *
 * Provides browser-based hardware discovery using WebSerial and WebUSB APIs.
 * Integrates with backend API for machine registration and PLR backend inference.
 */

import { Injectable, inject, signal, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { PLR_MACHINE_DEFINITIONS, PlrMachineDefinition } from '@assets/demo-data/plr-definitions';

export type ConnectionType = 'serial' | 'usb' | 'network' | 'simulator';
export type DeviceStatus = 'available' | 'connected' | 'connecting' | 'disconnected' | 'busy' | 'error' | 'requires_config' | 'unknown';

export interface DiscoveredDevice {
    id: string;
    name: string;
    connectionType: ConnectionType;
    status: DeviceStatus;
    port?: SerialPort;
    usbDevice?: USBDevice;
    manufacturer?: string;
    productName?: string;
    serialNumber?: string;
    vendorId?: number;
    productId?: number;
    plrBackend?: string;
    plrMachineDefinition?: PlrMachineDefinition;
    requiresConfiguration?: boolean;
    configurationSchema?: Record<string, ConfigurationField>;
    configuration?: Record<string, unknown>;
    errorMessage?: string;
    ipAddress?: string;
}

export interface ConfigurationField {
    type: 'string' | 'number' | 'boolean' | 'select';
    label: string;
    required: boolean;
    default?: unknown;
    options?: { value: string; label: string }[];
    description?: string;
}

export interface BackendDevice {
    id: string;
    name: string;
    connection_type: string;
    status: string;
    port?: string;
    ip_address?: string;
    manufacturer?: string;
    model?: string;
    serial_number?: string;
    plr_backend?: string;
    properties?: Record<string, unknown>;
}

export interface RegisterMachineRequest {
    device_id: string;
    name: string;
    plr_backend: string;
    connection_type: string;
    port?: string;
    ip_address?: string;
    configuration?: Record<string, unknown>;
}

export interface RegisterMachineResponse {
    accession_id: string;
    name: string;
    status: string;
    message: string;
}

// Known USB Vendor/Product IDs for lab equipment
const KNOWN_DEVICES: Record<string, { manufacturer: string; model: string; plrBackend: string; configSchema?: Record<string, ConfigurationField> }> = {
    // Hamilton devices
    '0x08BB:0x0106': {
        manufacturer: 'Hamilton',
        model: 'STAR',
        plrBackend: 'pylabrobot.liquid_handling.backends.hamilton.STAR',
        configSchema: {
            deck_layout: { type: 'string', label: 'Deck Layout', required: false, description: 'Custom deck layout file' },
        },
    },
    '0x08BB:0x0107': {
        manufacturer: 'Hamilton',
        model: 'Starlet',
        plrBackend: 'pylabrobot.liquid_handling.backends.hamilton.Starlet',
    },
    // Opentrons devices
    '0x04D8:0xE11A': {
        manufacturer: 'Opentrons',
        model: 'OT-2',
        plrBackend: 'pylabrobot.liquid_handling.backends.opentrons.OT2',
        configSchema: {
            simulate: { type: 'boolean', label: 'Simulation Mode', required: false, default: false },
        },
    },
    // Generic USB-Serial adapters
    '0x1A86:0x7523': { manufacturer: 'Generic', model: 'USB-Serial (CH340)', plrBackend: '' },
    '0x0403:0x6001': { manufacturer: 'FTDI', model: 'USB-Serial (FT232)', plrBackend: '' },
    '0x067B:0x2303': { manufacturer: 'Prolific', model: 'USB-Serial (PL2303)', plrBackend: '' },
};

@Injectable({
    providedIn: 'root'
})
export class HardwareDiscoveryService {
    private readonly http = inject(HttpClient);

    // Reactive state
    readonly discoveredDevices = signal<DiscoveredDevice[]>([]);
    readonly isDiscovering = signal(false);
    readonly webSerialSupported = signal(false);
    readonly webUsbSupported = signal(false);

    // Computed signals
    readonly supportedDevices = computed(() =>
        this.discoveredDevices().filter(d => d.plrBackend && d.plrBackend.length > 0)
    );
    readonly unconfiguredDevices = computed(() =>
        this.discoveredDevices().filter(d => d.status === 'requires_config')
    );
    readonly connectedDevices = computed(() =>
        this.discoveredDevices().filter(d => d.status === 'connected')
    );

    constructor() {
        // Check browser API support
        this.webSerialSupported.set('serial' in navigator);
        this.webUsbSupported.set('usb' in navigator);
    }

    /**
     * Check if WebSerial API is available
     */
    hasWebSerialSupport(): boolean {
        return 'serial' in navigator;
    }

    /**
     * Check if WebUSB API is available
     */
    hasWebUsbSupport(): boolean {
        return 'usb' in navigator;
    }

    /**
     * Request access to a serial port via WebSerial API
     * This prompts the user to select a device
     */
    async requestSerialPort(): Promise<DiscoveredDevice | null> {
        if (!this.hasWebSerialSupport()) {
            console.warn('WebSerial not supported in this browser');
            return null;
        }

        try {
            const port = await navigator.serial.requestPort();
            const device = this.createDeviceFromSerialPort(port, `serial-${Date.now()}`);

            // Add to discovered devices
            this.discoveredDevices.update(devices => [...devices, device]);

            return device;
        } catch (error) {
            if ((error as Error).name !== 'NotAllowedError') {
                console.error('Error requesting serial port:', error);
            }
            return null;
        }
    }

    /**
     * Request access to a USB device via WebUSB API
     */
    async requestUsbDevice(): Promise<DiscoveredDevice | null> {
        if (!this.hasWebUsbSupport()) {
            console.warn('WebUSB not supported in this browser');
            return null;
        }

        try {
            const usbDevice = await navigator.usb.requestDevice({
                filters: [] // Allow all devices
            });

            const device = this.createDeviceFromUSB(usbDevice, `usb-${Date.now()}`);
            this.discoveredDevices.update(devices => [...devices, device]);

            return device;
        } catch (error) {
            if ((error as Error).name !== 'NotAllowedError') {
                console.error('Error requesting USB device:', error);
            }
            return null;
        }
    }

    /**
     * Create a DiscoveredDevice from a SerialPort
     */
    private createDeviceFromSerialPort(port: SerialPort, id: string): DiscoveredDevice {
        const info = port.getInfo();
        const deviceKey = this.formatDeviceKey(info.usbVendorId, info.usbProductId);
        const knownDevice = KNOWN_DEVICES[deviceKey];
        const plrDef = this.inferPlrDefinition(knownDevice?.plrBackend, info.usbVendorId, info.usbProductId);

        const hasConfig = !!(knownDevice?.configSchema && Object.keys(knownDevice.configSchema).length > 0);

        return {
            id,
            name: knownDevice?.model || plrDef?.name || 'Serial Device',
            connectionType: 'serial',
            status: hasConfig ? 'requires_config' : 'available',
            port,
            vendorId: info.usbVendorId,
            productId: info.usbProductId,
            manufacturer: knownDevice?.manufacturer || plrDef?.vendor,
            productName: knownDevice?.model || plrDef?.name,
            plrBackend: knownDevice?.plrBackend || plrDef?.fqn,
            plrMachineDefinition: plrDef,
            requiresConfiguration: hasConfig,
            configurationSchema: knownDevice?.configSchema,
        };
    }

    /**
     * Create a DiscoveredDevice from a USBDevice
     */
    private createDeviceFromUSB(usbDevice: USBDevice, id: string): DiscoveredDevice {
        const deviceKey = this.formatDeviceKey(usbDevice.vendorId, usbDevice.productId);
        const knownDevice = KNOWN_DEVICES[deviceKey];
        const plrDef = this.inferPlrDefinition(knownDevice?.plrBackend, usbDevice.vendorId, usbDevice.productId);

        const hasConfig = !!(knownDevice?.configSchema && Object.keys(knownDevice.configSchema).length > 0);

        return {
            id,
            name: usbDevice.productName || knownDevice?.model || plrDef?.name || 'USB Device',
            connectionType: 'usb',
            status: hasConfig ? 'requires_config' : 'available',
            usbDevice,
            vendorId: usbDevice.vendorId,
            productId: usbDevice.productId,
            manufacturer: usbDevice.manufacturerName || knownDevice?.manufacturer || plrDef?.vendor,
            productName: usbDevice.productName || knownDevice?.model || plrDef?.name,
            serialNumber: usbDevice.serialNumber,
            plrBackend: knownDevice?.plrBackend || plrDef?.fqn,
            plrMachineDefinition: plrDef,
            requiresConfiguration: hasConfig,
            configurationSchema: knownDevice?.configSchema,
        };
    }

    /**
     * Format device key from vendor/product IDs
     */
    private formatDeviceKey(vendorId?: number, productId?: number): string {
        if (vendorId === undefined || productId === undefined) return '';
        return `0x${vendorId.toString(16).toUpperCase().padStart(4, '0')}:0x${productId.toString(16).toUpperCase().padStart(4, '0')}`;
    }

    /**
     * Infer PLR machine definition from backend class or VID/PID
     */
    private inferPlrDefinition(plrBackend?: string, vendorId?: number, productId?: number): PlrMachineDefinition | undefined {
        if (plrBackend) {
            return PLR_MACHINE_DEFINITIONS.find(m => m.fqn === plrBackend);
        }
        // Could extend to match by vendor name or other heuristics
        return undefined;
    }

    /**
     * Get previously authorized serial ports
     */
    async getAuthorizedSerialPorts(): Promise<DiscoveredDevice[]> {
        if (!this.hasWebSerialSupport()) {
            return [];
        }

        try {
            const ports = await navigator.serial.getPorts();
            return ports.map((port: SerialPort, index: number) =>
                this.createDeviceFromSerialPort(port, `serial-authorized-${index}`)
            );
        } catch (error) {
            console.error('Error getting authorized serial ports:', error);
            return [];
        }
    }

    /**
     * Get previously authorized USB devices
     */
    async getAuthorizedUsbDevices(): Promise<DiscoveredDevice[]> {
        if (!this.hasWebUsbSupport()) {
            return [];
        }

        try {
            const devices = await navigator.usb.getDevices();
            return devices.map((device: USBDevice, index: number) =>
                this.createDeviceFromUSB(device, `usb-authorized-${index}`)
            );
        } catch (error) {
            console.error('Error getting authorized USB devices:', error);
            return [];
        }
    }

    /**
     * Discover all available hardware
     * Combines browser APIs and backend discovery
     */
    async discoverAll(): Promise<DiscoveredDevice[]> {
        this.isDiscovering.set(true);
        const allDevices: DiscoveredDevice[] = [];

        try {
            // Get authorized devices from browser APIs (parallel)
            const [serialDevices, usbDevices, backendDevices] = await Promise.all([
                this.getAuthorizedSerialPorts(),
                this.getAuthorizedUsbDevices(),
                this.fetchBackendDevices(),
            ]);

            // Merge and deduplicate
            allDevices.push(...serialDevices, ...usbDevices);

            // Add backend devices that aren't already discovered via browser
            for (const bd of backendDevices) {
                const exists = allDevices.some(d =>
                    d.serialNumber === bd.serialNumber ||
                    (d.vendorId === bd.vendorId && d.productId === bd.productId)
                );
                if (!exists) {
                    allDevices.push(bd);
                }
            }

            this.discoveredDevices.set(allDevices);
        } catch (error) {
            console.error('Error during device discovery:', error);
        } finally {
            this.isDiscovering.set(false);
        }

        return allDevices;
    }

    /**
     * Fetch discovered devices from backend
     */
    private async fetchBackendDevices(): Promise<DiscoveredDevice[]> {
        try {
            const response = await firstValueFrom(
                this.http.get<{ devices: BackendDevice[] }>('/api/v1/hardware/discover')
            );

            if (!response?.devices) return [];

            return response.devices.map(d => {
                const plrDef = d.plr_backend
                    ? PLR_MACHINE_DEFINITIONS.find(m => m.fqn === d.plr_backend)
                    : undefined;

                return {
                    id: d.id,
                    name: d.name,
                    connectionType: d.connection_type as ConnectionType,
                    status: d.status as DeviceStatus,
                    manufacturer: d.manufacturer,
                    productName: d.model,
                    serialNumber: d.serial_number,
                    plrBackend: d.plr_backend,
                    plrMachineDefinition: plrDef,
                };
            });
        } catch (error) {
            console.warn('Could not fetch devices from backend:', error);
            return [];
        }
    }

    /**
     * Update device configuration
     */
    updateDeviceConfiguration(deviceId: string, config: Record<string, unknown>): void {
        this.discoveredDevices.update(devices =>
            devices.map(d => {
                if (d.id !== deviceId) return d;
                return {
                    ...d,
                    configuration: config,
                    status: 'available' as DeviceStatus,
                };
            })
        );
    }

    /**
     * Register a discovered device as a machine in the backend
     */
    async registerAsMachine(device: DiscoveredDevice, name?: string): Promise<RegisterMachineResponse | null> {
        if (!device.plrBackend) {
            console.error('Cannot register device without PLR backend');
            return null;
        }

        if (device.requiresConfiguration && !device.configuration) {
            console.error('Device requires configuration before registration');
            return null;
        }

        const request: RegisterMachineRequest = {
            device_id: device.id,
            name: name || device.name,
            plr_backend: device.plrBackend,
            connection_type: device.connectionType,
            configuration: device.configuration,
        };

        try {
            const response = await firstValueFrom(
                this.http.post<RegisterMachineResponse>('/api/v1/hardware/register', request)
            );
            return response;
        } catch (error) {
            console.error('Error registering device as machine:', error);
            return null;
        }
    }

    /**
     * Open a serial connection
     */
    async openSerialConnection(device: DiscoveredDevice, options: SerialOptions = { baudRate: 9600 }): Promise<boolean> {
        if (!device.port) {
            console.error('No serial port available for device');
            return false;
        }

        try {
            await device.port.open(options);
            this.discoveredDevices.update(devices =>
                devices.map(d => d.id === device.id ? { ...d, status: 'connected' as DeviceStatus } : d)
            );
            return true;
        } catch (error) {
            console.error('Error opening serial connection:', error);
            this.discoveredDevices.update(devices =>
                devices.map(d => d.id === device.id ? { ...d, status: 'error' as DeviceStatus } : d)
            );
            return false;
        }
    }

    /**
     * Close a serial connection
     */
    async closeSerialConnection(device: DiscoveredDevice): Promise<boolean> {
        if (!device.port) return false;

        try {
            await device.port.close();
            this.discoveredDevices.update(devices =>
                devices.map(d => d.id === device.id ? { ...d, status: 'available' as DeviceStatus } : d)
            );
            return true;
        } catch (error) {
            console.error('Error closing serial connection:', error);
            return false;
        }
    }

    /**
     * Remove a device from the discovered list
     */
    removeDevice(deviceId: string): void {
        this.discoveredDevices.update(devices =>
            devices.filter(d => d.id !== deviceId)
        );
    }

    /**
     * Clear error state for a device
     */
    clearDeviceError(deviceId: string): void {
        this.discoveredDevices.update(devices =>
            devices.map(d => d.id === deviceId
                ? { ...d, status: 'available' as DeviceStatus, errorMessage: undefined }
                : d
            )
        );
    }

    /**
     * Set device error state
     */
    setDeviceError(deviceId: string, errorMessage: string): void {
        this.discoveredDevices.update(devices =>
            devices.map(d => d.id === deviceId
                ? { ...d, status: 'error' as DeviceStatus, errorMessage }
                : d
            )
        );
    }

    /**
     * Check if a device is a recognized PLR-supported device
     */
    isPlrSupported(device: DiscoveredDevice): boolean {
        return !!(device.plrBackend && device.plrBackend.length > 0);
    }

    // =========================================================================
    // Backend Connection Management
    // =========================================================================

    /**
     * Connect to a device via backend API (persists connection state)
     */
    async connectViaBackend(device: DiscoveredDevice): Promise<boolean> {
        try {
            const response = await firstValueFrom(
                this.http.post<{ status: string; message: string }>('/api/v1/hardware/connect', {
                    device_id: device.id,
                    backend_class: device.plrBackend,
                    config: {
                        port: device.port ? 'webserial' : undefined,
                        ip_address: device.ipAddress,
                        ...device.configuration,
                    },
                })
            );

            if (response.status === 'connected') {
                this.discoveredDevices.update(devices =>
                    devices.map(d => d.id === device.id
                        ? { ...d, status: 'connected' as DeviceStatus, errorMessage: undefined }
                        : d
                    )
                );
                return true;
            }
            return false;
        } catch (error) {
            console.error('Backend connection failed:', error);
            this.setDeviceError(device.id, (error as Error).message || 'Connection failed');
            return false;
        }
    }

    /**
     * Disconnect from a device via backend API
     */
    async disconnectViaBackend(device: DiscoveredDevice): Promise<boolean> {
        try {
            await firstValueFrom(
                this.http.post('/api/v1/hardware/disconnect', {
                    device_id: device.id,
                })
            );

            this.discoveredDevices.update(devices =>
                devices.map(d => d.id === device.id
                    ? { ...d, status: 'available' as DeviceStatus }
                    : d
                )
            );
            return true;
        } catch (error) {
            console.error('Backend disconnection failed:', error);
            return false;
        }
    }

    /**
     * Fetch active connections from backend
     */
    async fetchBackendConnections(): Promise<void> {
        try {
            const connections = await firstValueFrom(
                this.http.get<Array<{
                    device_id: string;
                    status: string;
                    connected_at: string | null;
                    last_heartbeat: string;
                    backend_class: string | null;
                    error_message: string | null;
                }>>('/api/v1/hardware/connections')
            );

            // Update device statuses based on backend state
            this.discoveredDevices.update(devices =>
                devices.map(d => {
                    const conn = connections.find(c => c.device_id === d.id);
                    if (conn) {
                        return {
                            ...d,
                            status: conn.status as DeviceStatus,
                            errorMessage: conn.error_message || undefined,
                        };
                    }
                    return d;
                })
            );
        } catch (error) {
            // Silently fail - backend might not be available
            console.debug('Could not fetch backend connections:', error);
        }
    }

    /**
     * Send heartbeat for a connected device
     */
    async sendHeartbeat(deviceId: string): Promise<boolean> {
        try {
            const response = await firstValueFrom(
                this.http.post<{ success: boolean }>('/api/v1/hardware/heartbeat', {
                    device_id: deviceId,
                })
            );
            return response.success;
        } catch (error) {
            console.debug('Heartbeat failed:', error);
            return false;
        }
    }

    // =========================================================================
    // Low-level Port I/O Methods (for WebBridgeIO integration)
    // =========================================================================

    /**
     * Track open ports with their stream readers/writers
     */
    private openPorts = new Map<string, {
        port: SerialPort;
        reader: ReadableStreamDefaultReader<Uint8Array>;
        writer: WritableStreamDefaultWriter<Uint8Array>;
    }>();

    /**
     * Open a serial port by device ID
     */
    async openPort(portId: string, options: { baudRate?: number } = {}): Promise<void> {
        const device = this.discoveredDevices().find(d => d.id === portId);
        if (!device?.port) {
            throw new Error(`Port ${portId} not found in discovered devices`);
        }

        // Check if already open
        if (this.openPorts.has(portId)) {
            console.warn(`Port ${portId} is already open`);
            return;
        }

        const baudRate = options.baudRate || 9600;
        await device.port.open({ baudRate });

        const reader = device.port.readable?.getReader();
        const writer = device.port.writable?.getWriter();

        if (!reader || !writer) {
            throw new Error(`Failed to get reader/writer for port ${portId}`);
        }

        this.openPorts.set(portId, {
            port: device.port,
            reader,
            writer
        });

        // Update device status
        this.discoveredDevices.update(devices =>
            devices.map(d => d.id === portId ? { ...d, status: 'connected' as DeviceStatus } : d)
        );

        console.log(`[HardwareDiscovery] Opened port ${portId} at ${baudRate} baud`);
    }

    /**
     * Close a serial port by device ID
     */
    async closePort(portId: string): Promise<void> {
        const conn = this.openPorts.get(portId);
        if (!conn) {
            console.warn(`Port ${portId} is not open`);
            return;
        }

        try {
            conn.reader.releaseLock();
            conn.writer.releaseLock();
            await conn.port.close();
        } finally {
            this.openPorts.delete(portId);

            // Update device status
            this.discoveredDevices.update(devices =>
                devices.map(d => d.id === portId ? { ...d, status: 'available' as DeviceStatus } : d)
            );
        }

        console.log(`[HardwareDiscovery] Closed port ${portId}`);
    }

    /**
     * Write data to a serial port
     */
    async writeToPort(portId: string, data: Uint8Array): Promise<void> {
        const conn = this.openPorts.get(portId);
        if (!conn) {
            throw new Error(`Port ${portId} is not open`);
        }

        await conn.writer.write(data);
    }

    /**
     * Read a specific number of bytes from a serial port
     */
    async readFromPort(portId: string, size: number): Promise<Uint8Array> {
        const conn = this.openPorts.get(portId);
        if (!conn) {
            throw new Error(`Port ${portId} is not open`);
        }

        const chunks: Uint8Array[] = [];
        let bytesRead = 0;

        while (bytesRead < size) {
            const { value, done } = await conn.reader.read();
            if (done || !value) break;
            chunks.push(value);
            bytesRead += value.length;
        }

        // Concatenate chunks
        const result = new Uint8Array(bytesRead);
        let offset = 0;
        for (const chunk of chunks) {
            result.set(chunk, offset);
            offset += chunk.length;
        }

        return result.slice(0, size);
    }

    /**
     * Read a line (until newline) from a serial port
     */
    async readLineFromPort(portId: string): Promise<Uint8Array> {
        const conn = this.openPorts.get(portId);
        if (!conn) {
            throw new Error(`Port ${portId} is not open`);
        }

        const chunks: number[] = [];
        const NEWLINE = 0x0A; // \n

        while (true) {
            const { value, done } = await conn.reader.read();
            if (done || !value) break;

            for (let i = 0; i < value.length; i++) {
                chunks.push(value[i]);
                if (value[i] === NEWLINE) {
                    return new Uint8Array(chunks);
                }
            }
        }

        return new Uint8Array(chunks);
    }

    /**
     * Check if a port is currently open
     */
    isPortOpen(portId: string): boolean {
        return this.openPorts.has(portId);
    }
}

