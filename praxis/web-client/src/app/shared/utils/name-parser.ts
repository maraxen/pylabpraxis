/**
 * Extracts the unique/distinguishing part of asset names.
 * 
 * Examples:
 * - ["Hamilton Core96 Tip Rack", "Hamilton Core96 Plate"] -> ["Tip Rack", "Plate"]
 * - ["Corning 384 Well", "Corning 96 Well"] -> ["384 Well", "96 Well"]
 */
/**
 * Tokenizes an array of names based on common delimiters.
 * @param names - The array of names to tokenize.
 * @returns An array of string arrays, where each inner array represents the tokens of a name.
 */
export function tokenizeNames(names: string[]): string[][] {
    return names.map(name => name.split(/([_\-\s]+)/));
}

/**
 * Finds the length of the common prefix among tokenized names.
 * @param tokenizedNames - An array of tokenized names.
 * @returns The number of tokens that are part of the common prefix.
 */
export function findCommonPrefix(tokenizedNames: string[][]): number {
    if (!tokenizedNames || tokenizedNames.length === 0) {
        return 0;
    }

    const firstTokens = tokenizedNames[0];
    let commonPrefixLen = 0;

    for (let t = 0; t < firstTokens.length; t++) {
        const token = firstTokens[t];
        const allMatch = tokenizedNames.every(tokens => tokens.length > t && tokens[t] === token);
        if (allMatch) {
            commonPrefixLen++;
        } else {
            break;
        }
    }
    return commonPrefixLen;
}

/**
 * Finds the length of the common suffix among tokenized names.
 * @param tokenizedNames - An array of tokenized names.
 * @param prefixLen - The length of the common prefix.
 * @returns The number of tokens that are part of the common suffix.
 */
export function findCommonSuffix(tokenizedNames: string[][], prefixLen: number): number {
    if (!tokenizedNames || tokenizedNames.length === 0) {
        return 0;
    }

    const shortestLen = Math.min(...tokenizedNames.map(t => t.length));
    const firstTokens = tokenizedNames[0];
    let commonSuffixLen = 0;

    for (let t = 1; t <= shortestLen - prefixLen; t++) {
        const token = firstTokens[firstTokens.length - t];
        const allMatch = tokenizedNames.every(tokens => tokens[tokens.length - t] === token);
        if (allMatch) {
            commonSuffixLen++;
        } else {
            break;
        }
    }
    return commonSuffixLen;
}

/**
 * Extracts the middle part of tokenized names.
 * @param tokenizedNames - An array of tokenized names.
 * @param prefixLen - The length of the common prefix.
 * @param suffixLen - The length of the common suffix.
 * @returns An array of strings, each being the extracted middle part of a name.
 */
export function extractMiddleParts(
    tokenizedNames: string[][],
    prefixLen: number,
    suffixLen: number,
): string[] {
    return tokenizedNames.map(tokens => {
        const middleTokens = tokens.slice(prefixLen, tokens.length - suffixLen);
        let part = middleTokens.join('').trim();
        part = part.replace(/^[_\-\s]+|[_\-\s]+$/g, '');
        return part;
    });
}

/**
 * Resolves collisions in the unique parts by falling back to the original name if a part is not unique.
 * @param names - The original array of names.
 * @param uniqueParts - The array of extracted unique parts.
 * @returns A map from the original name to the resolved unique part (or the original name in case of collision).
 */
export function resolveCollisions(
    names: string[],
    uniqueParts: string[],
): Map<string, string> {
    const counts = new Map<string, number>();
    uniqueParts.forEach(p => counts.set(p, (counts.get(p) || 0) + 1));

    const result = new Map<string, string>();
    for (let i = 0; i < names.length; i++) {
        const name = names[i];
        const part = uniqueParts[i];

        if (!part || part === name || counts.get(part)! > 1) {
            result.set(name, name);
        } else {
            result.set(name, part);
        }
    }
    return result;
}

export function extractUniqueNameParts(names: string[]): Map<string, string> {
    if (names.length === 0) return new Map();
    if (names.length === 1) return new Map([[names[0], names[0]]]);

    const tokenizedNames = tokenizeNames(names);
    const commonPrefixLen = findCommonPrefix(tokenizedNames);
    const commonSuffixLen = findCommonSuffix(tokenizedNames, commonPrefixLen);
    const uniqueParts = extractMiddleParts(
        tokenizedNames,
        commonPrefixLen,
        commonSuffixLen,
    );

    return resolveCollisions(names, uniqueParts);
}
