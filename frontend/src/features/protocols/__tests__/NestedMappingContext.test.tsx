import { renderHook, act } from '@utils/test_utils';
import { useNestedMapping } from '@protocols/contexts/nestedMappingContext';

describe('nestedMappingContext', () => {
  test('provides default values', () => {
    const { result } = renderHook(() => useNestedMapping());
    // Check default config type, valueType, and editingState initial state.
    expect(result.current.config).toBeDefined();
    expect(result.current.valueType).toBeDefined();
    expect(result.current.editingState.id).toBeNull();
  });

  test('getValueMetadata returns correct metadata', () => {
    const { result } = renderHook(() => useNestedMapping());
    const sampleValue = 'example';
    const metadata = result.current.getValueMetadata(sampleValue);
    // Default mocked metadata: isEditable true and isFromParam false with type matching valueType
    expect(metadata.isEditable).toBe(true);
    expect(metadata.isFromParam).toBe(false);
    expect(metadata.type).toBe(result.current.valueType);
  });
});
