/**
 * Models for the Execution Monitor feature.
 */

/**
 * Represents the status of a protocol run.
 * Matches backend ProtocolRunStatusEnum.
 */
export type RunStatus =
    | 'PENDING'
    | 'PREPARING'
    | 'QUEUED'
    | 'RUNNING'
    | 'COMPLETED'
    | 'FAILED'
    | 'CANCELLED'
    | 'PAUSED';

/**
 * Summary representation of a protocol run for list views.
 */
export interface RunSummary {
    accession_id: string;
    name?: string;
    status: RunStatus;
    created_at: string;
    start_time?: string;
    end_time?: string;
    duration_ms?: number;
    protocol_name?: string;
    protocol_accession_id?: string;
}

/**
 * Detailed representation of a single protocol run.
 */
export interface RunDetail extends RunSummary {
    input_parameters_json?: Record<string, unknown>;
    resolved_assets_json?: Record<string, unknown>;
    output_data_json?: Record<string, unknown>;
    logs?: string[];
}

/**
 * Response for paginated run history.
 */
export interface RunHistoryResponse {
    items: RunSummary[];
    total: number;
    limit: number;
    offset: number;
}

/**
 * Parameters for filtering run history.
 */
export interface RunHistoryParams {
    limit?: number;
    offset?: number;
    status?: RunStatus | RunStatus[];
    protocol_id?: string;
    sort_by?: 'created_at' | 'start_time' | 'status';
    sort_order?: 'asc' | 'desc';
}
