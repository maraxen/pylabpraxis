/**
 * Utility functions for managing browser storage
 */

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
