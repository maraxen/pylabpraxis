import { Machine, Workcell } from '@features/assets/models/asset.models';

export interface WorkcellGroup {
    workcell: Workcell | null;
    machines: MachineWithRuntime[];
    isExpanded: boolean;
}

export interface MachineWithRuntime extends Machine {
    connectionState: 'connected' | 'disconnected' | 'connecting';
    lastStateUpdate?: Date;
    stateSource: 'live' | 'simulated' | 'cached' | 'definition';
    currentRun?: ProtocolRunSummary;
    alerts: MachineAlert[];
}

export interface MachineAlert {
    severity: 'info' | 'warning' | 'error';
    message: string;
    resourceId?: string;
}

export interface ProtocolRunSummary {
    id: string;
    protocolName: string;
    currentStep: number;
    totalSteps: number;
    progress: number;
    estimatedRemaining?: number;
}
