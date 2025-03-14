/**
 * Utility functions for managing browser storage
 */

import { MappingValue } from '../types';

export const STORAGE_KEY_PREFIX = 'mapping_state_';
const STORAGE_PREFIX = 'mapping_state_';

/**
 * Clears any storage related to the application that may be causing quota issues
 */
export const clearExcessStorage = (): boolean => {
  try {
    // Remove only keys matching our application prefix.
    Object.keys(sessionStorage).forEach(key => {
      if (key.startsWith('pylabpraxis_temp_')) {
        sessionStorage.removeItem(key);
      }
    });
    console.log("Filtered sessionStorage keys cleared.");
  } catch (e) {
    console.warn("Error clearing sessionStorage:", e);
  }
  return true;
};

export const saveToStorage = (key: string, value: any) => {
  try {
    const serialized = JSON.stringify(value);
    localStorage.setItem(`${STORAGE_KEY_PREFIX}${key}`, serialized);
    return true;
  } catch (error) {
    console.error('Error saving to storage:', error);
    return false;
  }
};

export const loadFromStorage = (key: string) => {
  try {
    const serialized = localStorage.getItem(`${STORAGE_KEY_PREFIX}${key}`);
    return serialized ? JSON.parse(serialized) : null;
  } catch (error) {
    console.error('Error loading from storage:', error);
    return null;
  }
};

export const clearStorage = (key: string) => {
  try {
    localStorage.removeItem(`${STORAGE_KEY_PREFIX}${key}`);
    return true;
  } catch (error) {
    console.error('Error clearing storage:', error);
    return false;
  }
};

/**
 * Generate a compact ID that doesn't rely on UUID or other storage-intensive methods
 */
export const generateCompactId = (prefix: string = ''): string => {
  if (crypto && typeof crypto.randomUUID === 'function') {
    return `${prefix}${crypto.randomUUID()}`;
  }
  // Fallback to timestamp + random number if crypto.randomUUID is unavailable
  const timestamp = Date.now().toString(36);
  const randomPart = Math.floor(Math.random() * 1000000).toString(36);
  return `${prefix}${timestamp}${randomPart}`;
};

export const saveMappingState = (mappingId: string, state: MappingValue): void => {
  try {
    localStorage.setItem(
      `${STORAGE_PREFIX}${mappingId}`,
      JSON.stringify(state)
    );
  } catch (error) {
    console.error('Failed to save mapping state:', error);
  }
};

export const loadMappingState = (mappingId: string): MappingValue | null => {
  try {
    const stored = localStorage.getItem(`${STORAGE_PREFIX}${mappingId}`);
    return stored ? JSON.parse(stored) : null;
  } catch (error) {
    console.error('Failed to load mapping state:', error);
    return null;
  }
};

export const clearMappingState = (mappingId: string): void => {
  try {
    localStorage.removeItem(`${STORAGE_PREFIX}${mappingId}`);
  } catch (error) {
    console.error('Failed to clear mapping state:', error);
  }
};

export const clearAllMappingStates = (): void => {
  try {
    Object.keys(localStorage)
      .filter(key => key.startsWith(STORAGE_PREFIX))
      .forEach(key => localStorage.removeItem(key));
  } catch (error) {
    console.error('Failed to clear all mapping states:', error);
  }
};