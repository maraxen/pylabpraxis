import { Machine } from '@core/db/schema';

export interface CreateProtocolRunRequestBody {
  protocol_definition_accession_id?: string;
  name?: string;
  parameters?: any;
}

export interface RegisterHardwareRequestBody {
  device_id?: string;
  name?: string;
  plr_backend?: string;
  connection_type?: string;
  configuration?: any;
}

export interface ConnectHardwareRequestBody {
  device_id?: string;
}

export interface ReplCommandRequestBody {
  device_id?: string;
  command?: string;
}

// Interface for Machine with extra properties seen in this file
export interface MockMachine extends Machine {
  machine_type?: string;
  is_simulation_override: boolean | null;
  backend_definition?: unknown;
}

// Type guards to check for body properties
export function isCreateProtocolRunBody(
  body: unknown,
): body is CreateProtocolRunRequestBody {
  return (
    typeof body === 'object' &&
    body !== null &&
    ('protocol_definition_accession_id' in body || 'name' in body)
  );
}

export function isRegisterHardwareBody(
  body: unknown,
): body is RegisterHardwareRequestBody {
  if (typeof body === 'string') {
    try {
      const parsed = JSON.parse(body);
      return typeof parsed === 'object' && parsed !== null;
    } catch {
      return false;
    }
  }
  return typeof body === 'object' && body !== null;
}

export function isConnectHardwareBody(
  body: unknown,
): body is ConnectHardwareRequestBody {
  return typeof body === 'object' && body !== null && 'device_id' in body;
}

export function isReplCommandBody(body: unknown): body is ReplCommandRequestBody {
  return typeof body === 'object' && body !== null && 'command' in body;
}
