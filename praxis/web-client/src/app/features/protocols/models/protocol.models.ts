
export interface ProtocolDefinition {
  accession_id: string;
  name: string;
  description?: string;
  category?: string;
  is_top_level: boolean;
  version: string;
  source_file_path?: string;
  module_name?: string;
  function_name?: string;
}

export interface ProtocolRun {
  accession_id: string;
  protocol_definition_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  start_time?: string;
  end_time?: string;
}

export interface ProtocolUpload {
    file: File;
    // or if purely path based for now
    path?: string;
}
