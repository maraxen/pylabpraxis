import { ParameterConfig } from './utils/parameterUtils';

export interface HierarchicalMappingProps {
  name: string;
  value: Record<string, any>;
  config: ParameterConfig;
  onChange: (newValue: any) => void;
  parameters?: Record<string, ParameterConfig>;
}
