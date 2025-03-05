/**
 * Utility functions for managing browser storage
 */

/**
 * Clears any storage related to the application that may be causing quota issues
 */
export const clearExcessStorage = (): boolean => {
  try {
    // Try to identify what's taking up space
    const storageInfo: Record<string, number> = {};
    let totalSize = 0;

    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (!key) continue;

      const item = localStorage.getItem(key) || '';
      const size = item.length * 2; // Approximate size in bytes (2 bytes per char)

      storageInfo[key] = size;
      totalSize += size;

      // If a single item is very large, remove it
      if (size > 500000) { // 500KB
        console.log(`Removing large item: ${key} (${size} bytes)`);
        localStorage.removeItem(key);
      }
    }

    console.log(`Total localStorage usage: ${totalSize} bytes`);

    // Clean up IndexedDB if available
    if ('indexedDB' in window) {
      indexedDB.databases().then(databases => {
        databases.forEach(db => {
          console.log(`Deleting IndexedDB database: ${db.name}`);
          indexedDB.deleteDatabase(db.name || '');
        });
      }).catch(() => {
        // Ignore errors
      });
    }

    // Remove any session storage items
    sessionStorage.clear();

    return true;
  } catch (e) {
    console.error("Error clearing storage:", e);
    return false;
  }
};

/**
 * Generate a compact ID that doesn't rely on UUID or other storage-intensive methods
 */
export const generateCompactId = (prefix: string = ''): string => {
  // Use timestamp + random number without relying on crypto API
  const timestamp = Date.now().toString(36); // Base 36 timestamp is more compact
  const randomPart = Math.floor(Math.random() * 1000000).toString(36);
  return `${prefix}${timestamp}${randomPart}`;
};
