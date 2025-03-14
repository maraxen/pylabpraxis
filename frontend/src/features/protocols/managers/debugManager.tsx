import React, { useEffect } from 'react';
import { useNestedMapping } from '../contexts/nestedMappingContext';

interface DebugManagerProps {
  children: React.ReactNode;
}

export const DebugManager: React.FC<DebugManagerProps> = ({ children }) => {
  const {
    creationMode,
    value,
    dragInfo
  } = useNestedMapping();

  // Log state changes for debugging
  useEffect(() => {
    console.log("Creation mode changed:", creationMode);
  }, [creationMode]);

  useEffect(() => {
    if (dragInfo.isDragging) {
      console.log("Drag info updated:", dragInfo);
    }
  }, [dragInfo]);

  return <>{children}</>;
};
