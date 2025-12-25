/**
 * Zero-Knowledge Proof Generator using snarkjs
 * 
 * This module handles real zk-SNARK proof generation for voter authentication.
 * 
 * Circuit: VoterCredential (15 levels Merkle tree, supports ~32K voters)
 * 
 * Private Inputs:
 *   - voterId: The voter's ID number
 *   - voterSecret: User's secret (citizenship number)
 *   - pathElements[15]: Merkle proof path
 *   - pathIndices[15]: Path directions (0=left, 1=right)
 * 
 * Public Inputs:
 *   - merkleRoot: Root of voter registry Merkle tree
 * 
 * Outputs:
 *   - nullifier: Hash(voterId, voterSecret) - prevents double voting
 *   - voterIdHash: Hash(voterId) - for reference
 *   - commitment: Hash(voterIdHash, nullifier) - binds the proof
 */

// import * as snarkjs from 'snarkjs'; // Dynamic import used instead

// Circuit artifact paths
const WASM_PATH = '/zk/citizen_credential.wasm';
const ZKEY_PATH = '/zk/citizen_credential_final.zkey';

export interface ZKProofInput {
    voterId: bigint;
    voterSecret: bigint;
    pathElements: bigint[];
    pathIndices: number[];
    merkleRoot: bigint;
}

export interface ZKProofResult {
    proof: {
        pi_a: string[];
        pi_b: string[][];
        pi_c: string[];
        protocol: string;
        curve: string;
    };
    publicSignals: string[];
    nullifier: string;
    voterIdHash: string;
    commitment: string;
}

/**
 * Generate a zk-SNARK proof for voter authentication
 * 
 * @param input - Circuit inputs (private and public)
 * @returns Proof and public signals
 */
export async function generateProof(input: ZKProofInput): Promise<ZKProofResult> {
    console.log('[ZK] Starting proof generation...');
    console.log('[ZK] Merkle root:', input.merkleRoot.toString(16).slice(0, 16) + '...');
    
    // Prepare circuit input
    const circuitInput = {
        voterId: input.voterId.toString(),
        voterSecret: input.voterSecret.toString(),
        pathElements: input.pathElements.map(e => e.toString()),
        pathIndices: input.pathIndices,
        merkleRoot: input.merkleRoot.toString()
    };
    
    console.log('[ZK] Circuit input prepared, generating proof...');
    
    try {
        const snarkjs = await import('snarkjs');
        // Generate the proof using snarkjs
        const { proof, publicSignals } = await snarkjs.groth16.fullProve(
            circuitInput,
            WASM_PATH,
            ZKEY_PATH
        );
        
        console.log('[ZK] Proof generated successfully!');
        console.log('[ZK] Public signals:', publicSignals);
        
        // publicSignals order matches circuit outputs: [nullifier, voterIdHash, commitment]
        return {
            proof: proof as ZKProofResult['proof'],
            publicSignals,
            nullifier: publicSignals[0],
            voterIdHash: publicSignals[1],
            commitment: publicSignals[2]
        };
    } catch (error: any) {
        console.error('[ZK] Proof generation failed:', error);
        throw new Error(`Proof generation failed: ${error.message}`);
    }
}

/**
 * Verify a zk-SNARK proof locally (optional, server also verifies)
 * 
 * @param proof - The generated proof
 * @param publicSignals - Public signals from proof generation
 * @returns true if valid
 */
export async function verifyProofLocally(
    proof: ZKProofResult['proof'], 
    publicSignals: string[]
): Promise<boolean> {
    try {
        const response = await fetch('/zk/verification_key.json');
        const vkey = await response.json();
        
        const snarkjs = await import('snarkjs');
        const isValid = await snarkjs.groth16.verify(vkey, publicSignals, proof);
        console.log('[ZK] Local verification result:', isValid);
        return isValid;
    } catch (error) {
        console.error('[ZK] Local verification failed:', error);
        return false;
    }
}

/**
 * Convert a string to a field element (bigint) using hash
 * Poseidon works with field elements, so we need to convert strings
 */
export function stringToFieldElement(str: string): bigint {
    // Simple conversion: use first 31 bytes of string as bigint
    // For production, use proper hash-to-field
    const bytes = new TextEncoder().encode(str);
    let result = BigInt(0);
    const maxBytes = Math.min(bytes.length, 31); // Poseidon field is ~254 bits
    for (let i = 0; i < maxBytes; i++) {
        result = (result << BigInt(8)) | BigInt(bytes[i]);
    }
    return result;
}

/**
 * Convert a bigint to hex string with 0x prefix
 */
export function bigintToHex(n: bigint): string {
    return '0x' + n.toString(16).padStart(64, '0');
}
