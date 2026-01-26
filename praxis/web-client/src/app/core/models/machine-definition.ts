/**
 * Machine Definition Types for Direct Control
 */

export interface ArgumentInfo {
    name: string;
    type: string;
    default?: unknown;
    description?: string;
}

export interface MethodInfo {
    name: string;
    description?: string;
    args?: ArgumentInfo[];
    returns?: string;
}

export interface MachineDefinition {
    machine_type: string;
    methods: MethodInfo[];
}
