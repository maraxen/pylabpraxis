import React from 'react';
import { Text } from '@chakra-ui/react';

interface ValueDisplayTextProps {
  value: any;
  type?: string;
}

export const ValueDisplayText: React.FC<ValueDisplayTextProps> = ({ value, type = 'string' }) => {
  if (value === undefined || value === null) {
    return <Text color="gray.400">(empty)</Text>;
  }

  const normalizedType = type?.toLowerCase();
  switch (normalizedType) {
    case 'boolean':
    case 'bool':
      const boolValue = typeof value === 'boolean' ? value : String(value).toLowerCase() === 'true';
      return <Text fontWeight="medium">{boolValue ? 'True' : 'False'}</Text>;
    case 'number':
    case 'int':
    case 'integer':
    case 'float':
    case 'double':
      return <Text fontWeight="medium">{value}</Text>;
    case 'dict':
    case 'object':
      return formatDictPreview(value);
    case 'array':
      return formatArrayPreview(value);
    case 'string':
    case 'str':
    default:
      if (typeof value === 'object' && value !== null) {
        return formatObjectPreview(value);
      }
      return <Text fontWeight="medium">{String(value)}</Text>;
  }
};

// Helper function to format dictionary preview
const formatDictPreview = (dict: Record<string, any>) => {
  if (!dict || typeof dict !== 'object') {
    return <Text fontWeight="medium">{String(dict)}</Text>;
  }

  const keys = Object.keys(dict);
  if (keys.length === 0) {
    return <Text fontWeight="medium">{'{}'}</Text>;
  }

  const previewKeys = keys.slice(0, 2);
  const hasMore = keys.length > 2;
  return (
    <Text fontWeight="medium" truncate>
      {'{'}
      {previewKeys.map(key => `${key}: ${formatPreviewValue(dict[key])}`).join(', ')}
      {hasMore ? ', ...' : ''}
      {'}'}
    </Text>
  );
};

// Helper function to format array preview
const formatArrayPreview = (arr: any[]) => {
  if (!Array.isArray(arr)) {
    return <Text fontWeight="medium">{String(arr)}</Text>;
  }
  if (arr.length === 0) {
    return <Text fontWeight="medium">[]</Text>;
  }

  const previewItems = arr.slice(0, 3);
  const hasMore = arr.length > 3;
  return (
    <Text fontWeight="medium" truncate>
      {'['}
      {previewItems.map(item => formatPreviewValue(item)).join(', ')}
      {hasMore ? ', ...' : ''}
      {']'}
    </Text>
  );
};

// Generic object preview - fallback
const formatObjectPreview = (obj: any) => {
  if (!obj || typeof obj !== 'object') {
    return <Text fontWeight="medium">{String(obj)}</Text>;
  }

  if (obj.id && obj.value !== undefined) {
    return <Text fontWeight="medium">{String(obj.value)}</Text>;
  }

  return <Text fontWeight="medium">{'{...}'}</Text>;
};

// Format value for preview display
const formatPreviewValue = (val: any): string => {
  if (val === null || val === undefined) {
    return 'null';
  }

  if (typeof val === 'object') {
    if (Array.isArray(val)) {
      return '[...]';
    }
    return '{...}';
  }

  if (typeof val === 'string') {
    return val.length > 10 ? `"${val.substring(0, 10)}..."` : `"${val}"`;
  }

  return String(val);
};