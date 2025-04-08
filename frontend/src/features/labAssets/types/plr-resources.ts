// Types for PyLabRobot resource metadata from the API

export interface ParameterInfo {
  name: string;
  type: string;
  required: boolean;
  default: any;
  description: string;
}

export interface ResourceTypeInfo {
  name: string;
  parent_class: string;
  can_create_directly: boolean;
  constructor_params: Record<string, ParameterInfo>;
  doc: string;
  module: string;
}

export interface MachineTypeInfo {
  name: string;
  parent_class: string;
  constructor_params: Record<string, ParameterInfo>;
  backends: string[];
  doc: string;
  module: string;
}

export interface ResourceCategoriesResponse {
  categories: {
    Containers: string[];
    Carriers: string[];
    Tips: string[];
    Plates: string[];
    Other: string[];
  };
}

// Common parameter types that may need special handling in the UI
export type ParameterValue = string | number | boolean | unknown[] | Record<string, unknown>;
export type FormValues = Record<string, ParameterValue>;

// For the resource form
export interface ResourceFormData {
  name: string;
  resourceType: string;
  description?: string;
  params: FormValues;
}

// For the machine form
export interface MachineFormData {
  name: string;
  machineType: string;
  backend?: string;
  description?: string;
  params: FormValues;
}