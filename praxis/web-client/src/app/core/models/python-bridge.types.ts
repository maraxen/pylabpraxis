export interface PythonBridgeMessage {
  type: string;
  payload: unknown;
}

export interface UserInteractionMessage {
  type: 'USER_INTERACTION';
  action: 'pause' | 'confirm' | 'input';
  message?: string;
  default?: string;
}

export interface ExecutionResultMessage {
  type: 'EXECUTION_RESULT';
  success: boolean;
  result?: unknown;
  error?: string;
}
