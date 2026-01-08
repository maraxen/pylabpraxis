/**
 * Extracts the unique/distinguishing part of asset names.
 * 
 * Examples:
 * - ["Hamilton Core96 Tip Rack", "Hamilton Core96 Plate"] -> ["Tip Rack", "Plate"]
 * - ["Corning 384 Well", "Corning 96 Well"] -> ["384 Well", "96 Well"]
 */
export function extractUniqueNameParts(names: string[]): Map<string, string> {
    if (names.length === 0) return new Map();
    if (names.length === 1) return new Map([[names[0], names[0]]]);

    // Tokenize each name, keeping delimiters to allow reconstructive logic
    const tokenizedNames = names.map(name => name.split(/([_\-\s]+)/));

    // 1. Find common prefix tokens
    let commonPrefixLen = 0;
    const firstTokens = tokenizedNames[0];

    for (let t = 0; t < firstTokens.length; t++) {
        const token = firstTokens[t];
        const allMatch = tokenizedNames.every(tokens => tokens[t] === token);
        if (allMatch) {
            commonPrefixLen++;
        } else {
            break;
        }
    }

    // 2. Find common suffix tokens
    let commonSuffixLen = 0;
    const shortestLen = Math.min(...tokenizedNames.map(t => t.length));

    // We iterate backwards from the end
    for (let t = 1; t <= shortestLen - commonPrefixLen; t++) {
        const token = firstTokens[firstTokens.length - t];
        const allMatch = tokenizedNames.every(tokens => tokens[tokens.length - t] === token);
        if (allMatch) {
            commonSuffixLen++;
        } else {
            break;
        }
    }

    const uniqueParts = names.map((name, i) => {
        const tokens = tokenizedNames[i];
        // Extract middle tokens
        const middleTokens = tokens.slice(commonPrefixLen, tokens.length - commonSuffixLen);
        let part = middleTokens.join('').trim();

        // Post-processing: remove leading/trailing separators if they were left over
        part = part.replace(/^[_\-\s]+|[_\-\s]+$/g, '');

        return part;
    });

    // Collision check & meaningfulness check
    const counts = new Map<string, number>();
    uniqueParts.forEach(p => counts.set(p, (counts.get(p) || 0) + 1));

    const result = new Map<string, string>();
    for (let i = 0; i < names.length; i++) {
        const name = names[i];
        const part = uniqueParts[i];

        // If the part is empty, identical to the name, or has collisions, fallback to full name
        if (!part || part === name || counts.get(part)! > 1) {
            result.set(name, name);
        } else {
            result.set(name, part);
        }
    }

    return result;
}
