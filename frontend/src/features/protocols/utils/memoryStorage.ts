// In-memory storage object (volatile; lost on refresh)
const memoryStorage: Record<string, any> = {};

// Get value from memory storage
export const getMemoryItem = (key: string): any => {
  return memoryStorage[key];
};

// Set value in memory storage
export const setMemoryItem = (key: string, value: any): void => {
  memoryStorage[key] = value;
};

// Remove value from memory storage
export const removeMemoryItem = (key: string): void => {
  delete memoryStorage[key];
};