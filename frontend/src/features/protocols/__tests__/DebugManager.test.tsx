import React from 'react';
import { render } from '@testing-library/react';
import { DebugManager } from '../managers/debugManager';

// Spy on console.log
const originalConsoleLog = console.log;
jest.spyOn(console, 'log').mockImplementation(() => { });

// Mock the context provider
jest.mock('../contexts/nestedMappingContext', () => ({
  useNestedMapping: jest.fn().mockReturnValue({
    creationMode: null,
    value: {},
    dragInfo: {
      isDragging: false,
      activeId: null,
      activeData: null,
      overDroppableId: null
    }
  })
}));

describe('DebugManager Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  afterAll(() => {
    // Restore original console.log
    console.log = originalConsoleLog;
  });

  // Basic rendering tests
  describe('Rendering', () => {
    test('renders children without modification', () => {
      const { getByText } = render(
        <DebugManager>
          <div>Test Content</div>
        </DebugManager>
      );

      expect(getByText('Test Content')).toBeInTheDocument();
    });
  });

  // Effect tests
  describe('Debug logging', () => {
    test('logs creation mode changes', () => {
      // First render with null creation mode
      const { rerender } = render(
        <DebugManager>
          <div>Test Content</div>
        </DebugManager>
      );

      // Check that console.log was called for initial render
      expect(console.log).toHaveBeenCalledWith("Creation mode changed:", null);

      // Update context with new creation mode
      require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValueOnce({
        creationMode: 'value',
        value: {},
        dragInfo: {
          isDragging: false,
          activeId: null,
          activeData: null,
          overDroppableId: null
        }
      });

      // Re-render with updated context
      rerender(
        <DebugManager>
          <div>Test Content</div>
        </DebugManager>
      );

      // Check that console.log was called with new mode
      expect(console.log).toHaveBeenCalledWith("Creation mode changed:", "value");
    });

    test('logs drag info when dragging', () => {
      const dragInfo = {
        isDragging: true,
        activeId: 'test-id',
        activeData: { value: 'test-value' },
        overDroppableId: 'drop-target'
      };

      // Mock context with active drag
      require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValueOnce({
        creationMode: null,
        value: {},
        dragInfo
      });

      render(
        <DebugManager>
          <div>Test Content</div>
        </DebugManager>
      );

      // Check that drag info was logged
      expect(console.log).toHaveBeenCalledWith("Drag info updated:", dragInfo);
    });

    test('does not log drag info when not dragging', () => {
      const dragInfo = {
        isDragging: false,
        activeId: null,
        activeData: null,
        overDroppableId: null
      };

      // Mock context with no active drag
      require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValueOnce({
        creationMode: null,
        value: {},
        dragInfo
      });

      jest.clearAllMocks(); // Clear previous calls to console.log

      render(
        <DebugManager>
          <div>Test Content</div>
        </DebugManager>
      );

      // Check that only creation mode was logged, not drag info
      expect(console.log).toHaveBeenCalledTimes(1);
      expect(console.log).not.toHaveBeenCalledWith("Drag info updated:", expect.anything());
    });
  });

  // Edge cases
  describe('Edge cases', () => {
    test('handles undefined context values', () => {
      // Mock with undefined values
      require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValueOnce({
        creationMode: undefined,
        value: undefined,
        dragInfo: undefined
      });

      // Should not throw errors
      expect(() => {
        render(
          <DebugManager>
            <div>Test Content</div>
          </DebugManager>
        );
      }).not.toThrow();
    });
  });
});