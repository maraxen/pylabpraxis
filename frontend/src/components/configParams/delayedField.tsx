import React, { useState, useEffect } from 'react';

interface DelayedFieldProps<T> {
  // Current value
  value: T;
  // Callback to commit value change on blur
  onBlur: (value: T) => void;
  // Render function that provides localValue, handleChange and handleBlur
  children: (localValue: T, handleChange: (val: T) => void, handleBlur: () => void) => React.ReactNode;
}

export function DelayedField<T>({ value, onBlur, children }: DelayedFieldProps<T>) {
  const [localValue, setLocalValue] = useState<T>(value);

  useEffect(() => {
    setLocalValue(value);
  }, [value]);

  const handleChange = (val: T) => {
    setLocalValue(val);
  };

  const handleBlur = () => {
    onBlur(localValue);
  };

  return <>{children(localValue, handleChange, handleBlur)}</>;
}
