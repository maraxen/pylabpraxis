import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
// Replace user-event import with mock implementation
import { ChakraProvider } from '@chakra-ui/react';
import { ParameterConfig } from '../utils/parameterUtils';
import HierarchicalMapping from '@protocols/components';
import HierarchicalMappingProps from '@protocols/components';
import { } from '@protocols/components';
import { system } from '@styles/theme';

// Mock implementation of userEvent for testing
const userEvent = {
  type: async (element: HTMLElement, text: string) => {
    const selectionStart = (element as HTMLInputElement).selectionStart || 0;
    const value = element.getAttribute('value') || '';
    const newValue = value.substring(0, selectionStart) + text + value.substring(selectionStart);
    fireEvent.change(element, { target: { value: newValue } });
    return;
  },
  clear: async (element: HTMLElement) => {
    fireEvent.change(element, { target: { value: '' } });
    return;
  }
};

// Mock nanoid to provide predictable IDs during tests
jest.mock('nanoid', () => ({
  nanoid: jest.fn().mockImplementation(() => `test-id-${Math.floor(Math.random() * 1000)}`)
}));

// DnD-kit sensors can be complex to test, so let's mock them
jest.mock('@dnd-kit/core', () => {
  const original = jest.requireActual('@dnd-kit/core');
  return {
    ...original,
    useSensor: jest.fn(),
    useSensors: jest.fn().mockReturnValue([]),
    DndContext: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
    DragOverlay: ({ children }: { children: React.ReactNode }) => <div data-testid="drag-overlay">{children}</div>,
  };
});

// Helper to create a test wrapper with ChakraProvider
const renderWithChakra = (ui: React.ReactElement) => {
  // Add the required 'value' prop to ChakraProvider
  return render(
    <ChakraProvider value={system}>{ui}</ChakraProvider>
  );
};

describe('HierarchicalMapping Component', () => {
  // Basic rendering test
  test('renders with empty values', () => {
    const props: HierarchicalMappingProps = {
      name: "test-mapping",
      value: {},
      config: {
        type: 'dict',
        constraints: {
          key_constraints: { type: 'string' },
          value_constraints: { type: 'string' }
        }
      },
      onChange: jest.fn()
    };

    renderWithChakra(<HierarchicalMapping {...props} />);

    expect(screen.getByText('Groups')).toBeInTheDocument();
    expect(screen.getByText('Available Values')).toBeInTheDocument();
    expect(screen.getByText(/No groups defined/i)).toBeInTheDocument();
    expect(screen.getByText(/No available values/i)).toBeInTheDocument();
  });

  // ...existing code...
});