import React, { useState, useRef, useEffect } from 'react';
import { Box, IconButton } from '@chakra-ui/react';
import { LuX } from "react-icons/lu";
import {
  useDraggable,
} from '@dnd-kit/core';
import { CSS } from '@dnd-kit/utilities';
import { ValueDisplay } from './valueDisplay';

// Improve DraggableValue with better drag behavior
export const DraggableValue: React.FC<{
  id: string;
  value: string;
  type: string;
  isFromParam?: boolean;
  paramSource?: string | undefined;
  isEditable?: boolean;
  isEditing?: boolean;
  onFocus?: () => void;
  onBlur?: () => void;
  onValueChange?: (newValue: string) => void;
  onRemove?: () => void;
}> = ({
  id,
  value,
  type,
  isFromParam,
  paramSource,
  isEditable = true,
  isEditing = false,
  onFocus,
  onBlur,
  onValueChange,
  onRemove
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

    const {
      attributes,
      listeners,
      setNodeRef,
      transform,
      isDragging
    } = useDraggable({
      id,
      data: {
        type: 'value',
        value,
        metadata: {
          type,
          isFromParam,
          paramSource,
          isEditable
        }
      },
      disabled: isEditing, // Disable dragging while editing
    });

    const style = transform ? {
      transform: CSS.Transform.toString(transform),
      opacity: isDragging ? 0 : 1, // Hide original when dragging
      cursor: isEditing ? 'text' : 'grab',
      zIndex: isDragging ? 1000 : undefined,
      minHeight: '42px',
      transformOrigin: '0 0', // Fix the transform origin to prevent offset
    } : {
      cursor: isEditing ? 'text' : 'grab',
      minHeight: '42px'
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

    const handleBlur = () => {
      onBlur?.();
    };

    return (
      <Box
        ref={setNodeRef}
        style={style}
        {...(!isEditing ? attributes : {})}
        {...(!isEditing ? listeners : {})}
        p={2}
        borderWidth={1}
        borderRadius="md"
        width="100%"
        display="flex"
        alignItems="center"
        gap={2}
        bg={isEditing ? "blue.50" : "white"}
        _dark={{ bg: isEditing ? "blue.900" : 'gray.700' }}
        position="relative"
        onMouseEnter={() => setIsHovering(true)}
        onMouseLeave={() => setIsHovering(false)}
        transition="all 0.2s"
      >
        <Box cursor={isEditing ? "default" : "grab"} opacity={isEditing ? 0.5 : 1}>☰</Box>
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

        {/* Show remove button only when hovering */}
        {onRemove && !isEditing && (
          <IconButton
            aria-label="Remove Value"
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
