/**
 * Poseidon Hash Implementation for Browser
 * 
 * Uses circomlibjs to compute Poseidon hashes that match the Circom circuit.
 * This is critical - SHA256 won't work with the circuit, we MUST use Poseidon.
 */

// import { buildPoseidon } from 'circomlibjs'; // Dynamic import used instead

let poseidonInstance: any = null;

/**
 * Initialize the Poseidon hasher (must be called before using hash functions)
 */
export async function initPoseidon(): Promise<void> {
    if (!poseidonInstance) {
        console.log('[Poseidon] Initializing hasher...');
        const { buildPoseidon } = await import('circomlibjs');
        poseidonInstance = await buildPoseidon();
        console.log('[Poseidon] Hasher ready');
    }
}

/**
 * Compute Poseidon hash of one input
 * Matches: component voterHasher = Poseidon(1) in circuit
 */
export function poseidonHash1(input: bigint): bigint {
    if (!poseidonInstance) {
        throw new Error('Poseidon not initialized. Call initPoseidon() first.');
    }
    const hash = poseidonInstance([input]);
    return poseidonInstance.F.toObject(hash);
}

/**
 * Compute Poseidon hash of two inputs
 * Matches: Poseidon(2) in circuit for nullifier, commitment, and Merkle tree
 */
export function poseidonHash2(a: bigint, b: bigint): bigint {
    if (!poseidonInstance) {
        throw new Error('Poseidon not initialized. Call initPoseidon() first.');
    }
    const hash = poseidonInstance([a, b]);
    return poseidonInstance.F.toObject(hash);
}

/**
 * Build a Poseidon-based Merkle tree from leaves
 * Returns the tree structure and root
 */
export function buildPoseidonMerkleTree(leaves: bigint[]): {
    layers: bigint[][];
    root: bigint;
} {
    if (!poseidonInstance) {
        throw new Error('Poseidon not initialized. Call initPoseidon() first.');
    }
    
    if (leaves.length === 0) {
        throw new Error('Cannot build tree with no leaves');
    }
    
    // Pad to next power of 2
    const targetSize = Math.pow(2, Math.ceil(Math.log2(leaves.length)));
    const paddedLeaves = [...leaves];
    while (paddedLeaves.length < targetSize) {
        paddedLeaves.push(BigInt(0)); // Zero padding
    }
    
    const layers: bigint[][] = [paddedLeaves];
    let currentLayer = paddedLeaves;
    
    // Build tree bottom-up using Poseidon
    while (currentLayer.length > 1) {
        const nextLayer: bigint[] = [];
        for (let i = 0; i < currentLayer.length; i += 2) {
            const left = currentLayer[i];
            const right = currentLayer[i + 1];
            const parent = poseidonHash2(left, right);
            nextLayer.push(parent);
        }
        layers.push(nextLayer);
        currentLayer = nextLayer;
    }
    
    return {
        layers,
        root: currentLayer[0]
    };
}

/**
 * Get Merkle proof for a leaf at given index
 * Returns path elements and path indices for the circuit
 */
export function getMerkleProof(
    layers: bigint[][],
    leafIndex: number,
    levels: number = 15
): {
    pathElements: bigint[];
    pathIndices: number[];
} {
    const pathElements: bigint[] = [];
    const pathIndices: number[] = [];
    
    let currentIndex = leafIndex;
    
    for (let i = 0; i < layers.length - 1 && i < levels; i++) {
        const layer = layers[i];
        const isRight = currentIndex % 2 === 1;
        const siblingIndex = isRight ? currentIndex - 1 : currentIndex + 1;
        
        if (siblingIndex < layer.length) {
            pathElements.push(layer[siblingIndex]);
        } else {
            pathElements.push(BigInt(0)); // Padding sibling
        }
        
        pathIndices.push(isRight ? 1 : 0);
        currentIndex = Math.floor(currentIndex / 2);
    }
    
    // Pad to required levels if tree is smaller
    while (pathElements.length < levels) {
        pathElements.push(BigInt(0));
        pathIndices.push(0);
    }
    
    return { pathElements, pathIndices };
}

/**
 * Verify a Merkle proof
 */
export function verifyMerkleProof(
    leaf: bigint,
    pathElements: bigint[],
    pathIndices: number[],
    expectedRoot: bigint
): boolean {
    let currentHash = leaf;
    
    for (let i = 0; i < pathElements.length; i++) {
        const sibling = pathElements[i];
        const isRight = pathIndices[i] === 1;
        
        if (isRight) {
            currentHash = poseidonHash2(sibling, currentHash);
        } else {
            currentHash = poseidonHash2(currentHash, sibling);
        }
    }
    
    return currentHash === expectedRoot;
}

/**
 * Convert a string (like voter ID) to a field element
 * Uses a simple but deterministic conversion
 */
export function stringToField(str: string): bigint {
    const bytes = new TextEncoder().encode(str);
    let result = BigInt(0);
    // Use first 31 bytes (fits in BN254 field)
    const maxBytes = Math.min(bytes.length, 31);
    for (let i = 0; i < maxBytes; i++) {
        result = (result << BigInt(8)) | BigInt(bytes[i]);
    }
    return result;
}

/**
 * Convert field element to hex string
 */
export function fieldToHex(n: bigint): string {
    return '0x' + n.toString(16).padStart(64, '0');
}
