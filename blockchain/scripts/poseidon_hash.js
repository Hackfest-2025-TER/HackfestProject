/**
 * Poseidon Hash Utility Script
 * 
 * Uses circomlibjs Poseidon implementation to match the circuit.
 * Called by Python backend via subprocess for consistent hashing.
 * 
 * Usage:
 *   node poseidon_hash.js hash <input1> [input2]
 *   node poseidon_hash.js merkle <leaves_json> <depth>
 *   node poseidon_hash.js proof <leaf_hash> <leaves_json> <depth>
 */

const { buildPoseidon } = require("circomlibjs");

// Convert BigInt to field element string
function toFieldStr(n) {
    return BigInt(n).toString();
}

// Convert hex string to BigInt
function hexToBigInt(hex) {
    if (hex.startsWith("0x")) {
        return BigInt(hex);
    }
    return BigInt("0x" + hex);
}

// Convert string to field element (for voter IDs, secrets)
function stringToField(str) {
    // Hash the string to get consistent field element
    let hash = BigInt(0);
    for (let i = 0; i < str.length; i++) {
        hash = hash * BigInt(256) + BigInt(str.charCodeAt(i));
    }
    // Ensure it's within field (BN254 field prime)
    const FIELD_SIZE = BigInt("21888242871839275222246405745257275088548364400416034343698204186575808495617");
    return hash % FIELD_SIZE;
}

async function main() {
    const poseidon = await buildPoseidon();
    const F = poseidon.F;
    
    const command = process.argv[2];
    
    if (command === "hash") {
        // Hash one or two inputs
        const input1 = process.argv[3];
        const input2 = process.argv[4];
        
        let inputs;
        if (input2) {
            // Two inputs - parse as BigInts or strings
            const val1 = input1.match(/^\d+$/) ? BigInt(input1) : stringToField(input1);
            const val2 = input2.match(/^\d+$/) ? BigInt(input2) : stringToField(input2);
            inputs = [val1, val2];
        } else {
            // Single input
            const val1 = input1.match(/^\d+$/) ? BigInt(input1) : stringToField(input1);
            inputs = [val1];
        }
        
        const hash = poseidon(inputs);
        const hashStr = F.toString(hash, 10);
        
        console.log(JSON.stringify({
            hash: hashStr,
            hashHex: "0x" + BigInt(hashStr).toString(16).padStart(64, "0")
        }));
        
    } else if (command === "commitment") {
        // Generate voter commitment: Poseidon(secret, voterId)
        // NOTE: This is the commitment that binds secret to voter
        const secret = process.argv[3];
        const voterId = process.argv[4];
        
        const secretField = stringToField(secret);
        const voterIdField = stringToField(voterId);
        
        const commitment = poseidon([secretField, voterIdField]);
        const commitmentStr = F.toString(commitment, 10);
        
        console.log(JSON.stringify({
            commitment: commitmentStr,
            commitmentHex: "0x" + BigInt(commitmentStr).toString(16).padStart(64, "0"),
            secret: secretField.toString(),
            voterId: voterIdField.toString()
        }));
        
    } else if (command === "voter-leaf") {
        // Generate voter leaf for Merkle tree: Poseidon(voterId)
        // This MUST match the circuit: voterIdHash = Poseidon(voterId)
        const voterId = process.argv[3];
        const voterIdField = stringToField(voterId);
        
        const leaf = poseidon([voterIdField]);
        const leafStr = F.toString(leaf, 10);
        
        console.log(JSON.stringify({
            leaf: leafStr,
            leafHex: "0x" + BigInt(leafStr).toString(16).padStart(64, "0"),
            voterId: voterIdField.toString()
        }));
        
    } else if (command === "batch-voter-leaves") {
        // Generate voter leaves in batch for efficiency
        // Input: JSON array of voter IDs
        const voterIdsJson = process.argv[3];
        const voterIds = JSON.parse(voterIdsJson);
        
        const leaves = [];
        for (const voterId of voterIds) {
            const voterIdField = stringToField(voterId);
            const leaf = poseidon([voterIdField]);
            leaves.push(F.toString(leaf, 10));
        }
        
        console.log(JSON.stringify({
            leaves: leaves,
            count: leaves.length
        }));
        
    } else if (command === "merkle") {
        // Build Merkle tree from leaves
        const leavesJson = process.argv[3];
        const depth = parseInt(process.argv[4]) || 15;
        
        let leaves = JSON.parse(leavesJson);
        
        // Convert to BigInts
        leaves = leaves.map(l => BigInt(l));
        
        // Pad to 2^depth
        const targetSize = Math.pow(2, depth);
        while (leaves.length < targetSize) {
            leaves.push(BigInt(0));
        }
        
        // Build tree level by level
        let currentLevel = leaves;
        const tree = [currentLevel.map(l => l.toString())];
        
        while (currentLevel.length > 1) {
            const nextLevel = [];
            for (let i = 0; i < currentLevel.length; i += 2) {
                const left = currentLevel[i];
                const right = currentLevel[i + 1];
                const parent = poseidon([left, right]);
                nextLevel.push(F.toObject(parent));
            }
            tree.push(nextLevel.map(l => l.toString()));
            currentLevel = nextLevel;
        }
        
        const root = currentLevel[0].toString();
        
        console.log(JSON.stringify({
            root: root,
            rootHex: "0x" + BigInt(root).toString(16).padStart(64, "0"),
            levels: tree.length,
            leafCount: leaves.length
        }));
        
    } else if (command === "proof") {
        // Generate Merkle proof for a leaf
        const leafIndex = parseInt(process.argv[3]);
        const leavesJson = process.argv[4];
        const depth = parseInt(process.argv[5]) || 15;
        
        let leaves = JSON.parse(leavesJson);
        leaves = leaves.map(l => BigInt(l));
        
        // Pad to 2^depth
        const targetSize = Math.pow(2, depth);
        while (leaves.length < targetSize) {
            leaves.push(BigInt(0));
        }
        
        // Build tree and collect proof
        let currentLevel = leaves;
        const pathElements = [];
        const pathIndices = [];
        let idx = leafIndex;
        
        for (let level = 0; level < depth; level++) {
            const isRight = idx % 2 === 1;
            const siblingIdx = isRight ? idx - 1 : idx + 1;
            
            pathElements.push(currentLevel[siblingIdx].toString());
            pathIndices.push(isRight ? 1 : 0);
            
            // Build next level
            const nextLevel = [];
            for (let i = 0; i < currentLevel.length; i += 2) {
                const left = currentLevel[i];
                const right = currentLevel[i + 1];
                const parent = poseidon([left, right]);
                nextLevel.push(F.toObject(parent));
            }
            currentLevel = nextLevel;
            idx = Math.floor(idx / 2);
        }
        
        const root = currentLevel[0].toString();
        
        console.log(JSON.stringify({
            leaf: leaves[leafIndex].toString(),
            leafIndex: leafIndex,
            pathElements: pathElements,
            pathIndices: pathIndices,
            root: root,
            rootHex: "0x" + BigInt(root).toString(16).padStart(64, "0")
        }));
        
    } else if (command === "build-registry") {
        // Build complete registry from voter data (CSV parsed as JSON)
        const votersJson = process.argv[3];
        const depth = parseInt(process.argv[4]) || 15;
        
        const voters = JSON.parse(votersJson);
        const commitments = [];
        const voterMap = {};  // commitment -> voter index
        
        // Generate commitments for each voter
        for (let i = 0; i < voters.length; i++) {
            const { voterId, secret } = voters[i];
            
            const secretField = stringToField(secret);
            const voterIdField = stringToField(voterId);
            
            const commitment = poseidon([secretField, voterIdField]);
            const commitmentStr = F.toString(commitment, 10);
            
            commitments.push(commitmentStr);
            voterMap[commitmentStr] = i;
        }
        
        // Shuffle commitments (cryptographic shuffle)
        const seed = process.argv[5] || Date.now().toString();
        const shuffled = [...commitments];
        
        // Fisher-Yates shuffle with seeded random
        let seedNum = 0;
        for (const char of seed) {
            seedNum = (seedNum * 31 + char.charCodeAt(0)) >>> 0;
        }
        
        for (let i = shuffled.length - 1; i > 0; i--) {
            seedNum = (seedNum * 1103515245 + 12345) >>> 0;
            const j = seedNum % (i + 1);
            [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
        }
        
        // Build Merkle tree from shuffled leaves
        let leaves = shuffled.map(l => BigInt(l));
        
        const targetSize = Math.pow(2, depth);
        while (leaves.length < targetSize) {
            leaves.push(BigInt(0));
        }
        
        let currentLevel = leaves;
        
        while (currentLevel.length > 1) {
            const nextLevel = [];
            for (let i = 0; i < currentLevel.length; i += 2) {
                const left = currentLevel[i];
                const right = currentLevel[i + 1];
                const parent = poseidon([left, right]);
                nextLevel.push(F.toObject(parent));
            }
            currentLevel = nextLevel;
        }
        
        const root = currentLevel[0].toString();
        
        console.log(JSON.stringify({
            root: root,
            rootHex: "0x" + BigInt(root).toString(16).padStart(64, "0"),
            leaves: shuffled,
            voterCount: voters.length,
            depth: depth,
            seed: seed
        }));
        
    } else {
        console.error("Usage:");
        console.error("  node poseidon_hash.js hash <input1> [input2]");
        console.error("  node poseidon_hash.js commitment <secret> <voterId>  # For binding");
        console.error("  node poseidon_hash.js voter-leaf <voterId>           # For Merkle tree");
        console.error("  node poseidon_hash.js merkle <leaves_json> <depth>");
        console.error("  node poseidon_hash.js proof <leafIndex> <leaves_json> <depth>");
        console.error("  node poseidon_hash.js build-registry <voters_json> <depth> [seed]");
        process.exit(1);
    }
}

main().catch(err => {
    console.error(JSON.stringify({ error: err.message }));
    process.exit(1);
});
