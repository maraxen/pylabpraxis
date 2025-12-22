
export enum ExecutionStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled'
}

export interface ExecutionMessage {
  type: 'status' | 'log' | 'progress' | 'error' | 'complete';
  payload: any;
  timestamp: string;
}

export interface ExecutionState {
  runId: string;
  protocolName: string;
  status: ExecutionStatus;
  progress: number;
  currentStep?: string;
  logs: string[];
  startTime?: string;
  endTime?: string;
}
