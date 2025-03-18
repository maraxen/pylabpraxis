/**
 * Utility functions for managing browser storage
 */

/**
 * Clears any storage related to the application that may be causing quota issues
 */

import { nanoid } from 'nanoid';

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

/**
 * Generate a compact ID using nanoid for efficiency
 *
 * @param prefix Optional prefix to add to the ID
 * @param length Optional length of the nanoid (default: 8)
 * @returns A unique compact ID string
 */
export const generateCompactId = (prefix: string = '', length: number = 8): string => {
  // Use nanoid for efficient ID generation
  return `${prefix}${nanoid(length)}`;
};
