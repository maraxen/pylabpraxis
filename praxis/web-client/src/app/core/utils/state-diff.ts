/**
 * State diffing and patching utilities.
 * 
 * Provides functions to calculate the difference between two nested objects
 * and apply those differences to a base object. This is used to store 
 * incremental state changes instead of full snapshots, reducing database 
 * storage requirements while maintaining full history.
 * 
 * Logic must remain consistent with the Python equivalent (state_diff.py).
 */

export function calculateDiff(old: any, newValue: any): any {
    // Simple equality check
    if (old === newValue) {
        return null;
    }

    // If either is not an object or is an array, return the new value as a replacement
    if (
        typeof old !== 'object' || old === null ||
        typeof newValue !== 'object' || newValue === null ||
        Array.isArray(old) || Array.isArray(newValue)
    ) {
        // Deep comparison for objects/arrays that weren't strictly equal
        if (JSON.stringify(old) === JSON.stringify(newValue)) {
            return null;
        }
        return newValue;
    }

    const diff: any = {};
    let hasChanges = false;

    // Check for changes and additions
    for (const key in newValue) {
        if (Object.prototype.hasOwnProperty.call(newValue, key)) {
            if (!(key in old)) {
                diff[key] = newValue[key];
                hasChanges = true;
            } else {
                const nestedDiff = calculateDiff(old[key], newValue[key]);
                if (nestedDiff !== null) {
                    diff[key] = nestedDiff;
                    hasChanges = true;
                }
            }
        }
    }

    // Check for removals
    for (const key in old) {
        if (Object.prototype.hasOwnProperty.call(old, key) && !(key in newValue)) {
            diff[key] = '__DELETED__';
            hasChanges = true;
        }
    }

    return hasChanges ? diff : null;
}

export function applyDiff(base: any, diff: any): any {
    if (diff === null) {
        return base;
    }

    // If diff is not an object or is an array, it's a replacement
    if (
        typeof base !== 'object' || base === null ||
        typeof diff !== 'object' || diff === null ||
        Array.isArray(base) || Array.isArray(diff)
    ) {
        return diff;
    }

    const result = { ...base };

    for (const key in diff) {
        if (Object.prototype.hasOwnProperty.call(diff, key)) {
            const value = diff[key];
            if (value === '__DELETED__') {
                delete result[key];
            } else if (key in result) {
                result[key] = applyDiff(result[key], value);
            } else {
                result[key] = value;
            }
        }
    }

    return result;
}
