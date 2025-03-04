import React, { useState, useRef, useEffect } from 'react';
import { Box, IconButton, Badge } from '@chakra-ui/react';
import { LuX } from "react-icons/lu";
import {
  useSortable,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import {
  SortableItemProps
} from '../utils/parameterUtils';
import { ValueDisplay } from './valueDisplay';

// Update SortableItem to maintain metadata and add hover-based removal
export const SortableItem: React.FC<SortableItemProps & {
  isFromParam?: boolean;
  paramSource?: string | undefined;
  isEditable?: boolean;
  isEditing?: boolean;
  onRemove?: () => void;
  onFocus?: () => void;
  onBlur?: () => void;
  onValueChange?: (newValue: string) => void;
}> = ({
  id,
  value,
  type,
  isFromParam,
  paramSource,
  isEditable = true,
  isEditing = false,
  onRemove,
  onFocus,
  onBlur,
  onValueChange
}) => {
    const [isHovering, setIsHovering] = useState(false);
    const [localValue, setLocalValue] = useState(value);
    const inputRef = useRef<HTMLInputElement>(null);

    // Sync localValue with parent value when not editing
    useEffect(() => {
      if (!isEditing) {
        setLocalValue(value);
      }
    }, [value, isEditing]);

    // Focus the input when editing starts
    useEffect(() => {
      if (isEditing && inputRef.current) {
        inputRef.current.focus();
      }
    }, [isEditing]);

    const { attributes, listeners, setNodeRef, transform, transition } = useSortable({
      id,
      disabled: isEditing, // Disable sorting while editing
    });

    const style = {
      transform: CSS.Transform.toString(transform),
      transition,
      transformOrigin: '0 0', // Fix the transform origin
      cursor: isEditing ? 'text' : 'grab',
    };

    const handleValueChange = (_: string, newValue: any) => {
      setLocalValue(newValue);
      onValueChange?.(newValue);
    };

    const handleFocus = () => {
      if (isEditable && !isFromParam) {
        onFocus?.();
      }
    };

    return (
      <Box
        ref={setNodeRef}
        style={style}
        display="flex"
        alignItems="center"
        gap={2}
        p={2}
        borderWidth="1px"
        borderRadius="md"
        bg={isEditing ? "blue.50" : "white"}
        _dark={{ bg: isEditing ? "blue.900" : "gray.700" }}
        position="relative"
        onMouseEnter={() => setIsHovering(true)}
        onMouseLeave={() => setIsHovering(false)}
      >
        <Box
          cursor={isEditing ? "default" : "grab"}
          opacity={isEditing ? 0.5 : 1}
          {...(isEditing ? {} : attributes)}
          {...(isEditing ? {} : listeners)}
        >
          ☰
        </Box>
        <ValueDisplay
          value={isEditing ? localValue : value}
          type={type}
          isFromParam={isFromParam}
          paramSource={paramSource}
          isEditable={isEditable}
          isEditing={isEditing}
          onFocus={onFocus}
          onBlur={onBlur}
          onValueChange={onValueChange}
        />

        {/* Show remove button only when hovering and not editing */}
        {onRemove && !isEditing && isEditable && (
          <IconButton
            aria-label="Remove Item"
            size="xs"
            position="absolute"
            top={1}
            right={1}
            opacity={isHovering ? 1 : 0}
            transition="opacity 0.2s"
            onClick={(e) => {
              e.stopPropagation();
              onRemove();
            }}
          >
            <LuX />
          </IconButton>
        )}
      </Box>
    );
  };