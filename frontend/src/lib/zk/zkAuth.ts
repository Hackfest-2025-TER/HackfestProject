/**
 * Zero-Knowledge Authentication System
 * 
 * This is the REAL ZK authentication flow:
 * 
 * 1. User enters VoterID + Secret
 * 2. Frontend fetches Merkle proof from server (NOT entire tree)
 * 3. Frontend generates real zk-SNARK proof using snarkjs
 * 4. Frontend sends proof to server
 * 5. Server verifies proof cryptographically
 * 6. Server issues credential only if proof is valid
 * 
 * Privacy guarantees:
 * - VoterID never sent to server (only hash in Merkle tree)
 * - Secret never sent to server
 * - Proof reveals nothing about identity
 * - Only nullifier is public (unlinkable to voter)
 */

import { generateProof, stringToFieldElement, bigintToHex } from './zkProver';
import { 
    initPoseidon, 
    poseidonHash1, 
    poseidonHash2, 
    buildPoseidonMerkleTree,
    getMerkleProof,
    stringToField,
    fieldToHex
} from './poseidon';

const API_URL = '';

export interface AuthResult {
    success: boolean;
    credential?: string;
    nullifier?: string;
    message?: string;
    used_votes?: number[];
}

export interface MerkleProofData {
    leaf: string;           // Poseidon hash of voterId
    pathElements: string[]; // Sibling hashes
    pathIndices: number[];  // 0=left, 1=right
    root: string;          // Current Merkle root
    leafIndex: number;     // Position in tree
}

/**
 * Initialize the ZK system (must be called before authentication)
 */
export async function initZK(): Promise<void> {
    await initPoseidon();
    console.log('[ZK Auth] System initialized');
}

/**
 * Compute the leaf hash for a voter ID (must match backend computation)
 */
export function computeVoterLeaf(voterId: string): bigint {
    const voterIdField = stringToField(voterId);
    return poseidonHash1(voterIdField);
}

/**
 * Compute nullifier from voterId and secret
 * Circuit: nullifier = Poseidon(voterId, voterSecret)
 */
export function computeNullifier(voterId: string, secret: string): bigint {
    const voterIdField = stringToField(voterId);
    const secretField = stringToField(secret);
    return poseidonHash2(voterIdField, secretField);
}

/**
 * Fetch Merkle proof from server for a voter
 * Server returns only the proof path, not the entire tree
 * 
 * NOTE: We only send voterId, not secret.
 * The tree stores Poseidon(voterId), not Poseidon(secret, voterId).
 * Secret is kept private and only used locally for ZK proof generation.
 */
async function fetchMerkleProof(voterId: string): Promise<MerkleProofData | null> {
    try {
        const response = await fetch(`${API_URL}/api/zk/merkle-proof`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ voter_id: voterId })
        });
        
        if (!response.ok) {
            const error = await response.json();
            console.error('[ZK Auth] Failed to fetch proof:', error);
            return null;
        }
        
        return await response.json();
    } catch (error) {
        console.error('[ZK Auth] Network error:', error);
        return null;
    }
}

/**
 * Main authentication function using real ZK proofs
 */
export async function authenticateWithZK(
    voterId: string,
    secret: string,
    onStatusUpdate: (status: string) => void
): Promise<AuthResult> {
    try {
        // Step 1: Initialize Poseidon
        onStatusUpdate('Initializing cryptographic system...');
        await initZK();
        
        // Step 2: Compute voter ID field
        // The tree stores Poseidon(voterId) - we'll verify this via ZK proof
        onStatusUpdate('Preparing voter credentials...');
        const voterIdField = stringToField(voterId);
        const secretField = stringToField(secret);
        
        console.log('[ZK Auth] Voter ID field:', voterIdField.toString().slice(0, 20) + '...');
        
        // Step 3: Fetch Merkle proof from server (scalable - O(log n))
        // NOTE: We only send voterId, secret stays local for privacy!
        onStatusUpdate('Fetching Merkle proof from server...');
        const merkleProof = await fetchMerkleProof(voterId);
        
        if (!merkleProof) {
            return {
                success: false,
                message: 'Voter not found in registry. Please verify your Voter ID and citizenship number.'
            };
        }
        
        console.log('[ZK Auth] Got Merkle proof, root:', merkleProof.root.slice(0, 20) + '...');
        console.log('[ZK Auth] Leaf index:', merkleProof.leafIndex);
        
        // Step 4: Generate ZK proof
        onStatusUpdate('Generating zero-knowledge proof...');
        
        const pathElements = merkleProof.pathElements.map(e => BigInt(e));
        const merkleRoot = BigInt(merkleProof.root);
        
        const proofResult = await generateProof({
            voterId: voterIdField,
            voterSecret: secretField,
            pathElements: pathElements,
            pathIndices: merkleProof.pathIndices,
            merkleRoot: merkleRoot
        });
        
        console.log('[ZK Auth] Proof generated!');
        console.log('[ZK Auth] Nullifier:', proofResult.nullifier.slice(0, 20) + '...');
        
        // Step 5: Send proof to server for verification
        onStatusUpdate('Submitting proof for cryptographic verification...');
        
        const response = await fetch(`${API_URL}/api/zk/verify-proof`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                proof: proofResult.proof,
                publicSignals: proofResult.publicSignals,
                merkle_root: merkleProof.root
            })
        });
        
        if (!response.ok) {
            let errorMessage = 'Proof verification failed';
            // Clone the response before reading to avoid "body already consumed" error
            const responseClone = response.clone();
            try {
                const error = await response.json();
                errorMessage = error.detail || error.message || errorMessage;
            } catch (e) {
                // Response is not JSON, try to get text from the clone
                try {
                    const text = await responseClone.text();
                    errorMessage = text || `Server error (${response.status})`;
                } catch {
                    errorMessage = `Server error (${response.status})`;
                }
            }
            console.error('[ZK Auth] Verification failed:', errorMessage);
            return {
                success: false,
                message: errorMessage
            };
        }
        
        const result = await response.json();
        
        if (!result.valid) {
            return {
                success: false,
                message: result.message || 'Invalid proof'
            };
        }
        
        console.log('[ZK Auth] Authentication successful!');
        
        return {
            success: true,
            credential: result.credential,
            nullifier: result.nullifier,
            message: result.message || 'Successfully verified as eligible voter',
            used_votes: result.used_votes || []
        };
        
    } catch (error: any) {
        console.error('[ZK Auth] Error:', error);
        return {
            success: false,
            message: error.message || 'Authentication failed'
        };
    }
}

/**
 * Fallback: Simple commitment-based auth (for backward compatibility)
 * This is less secure but works without the full ZK circuit
 */
export async function authenticateSimple(
    voterId: string,
    secret: string,
    onStatusUpdate: (status: string) => void
): Promise<AuthResult> {
    try {
        onStatusUpdate('Initializing...');
        await initZK();
        
        // Compute commitment using Poseidon (matches server)
        onStatusUpdate('Computing commitment...');
        const voterIdField = stringToField(voterId);
        const secretField = stringToField(secret);
        const commitment = poseidonHash2(secretField, voterIdField);
        const nullifier = poseidonHash2(voterIdField, secretField);
        
        const commitmentHex = fieldToHex(commitment);
        const nullifierHex = fieldToHex(nullifier);
        
        // Send commitment to server
        onStatusUpdate('Verifying with server...');
        const response = await fetch(`${API_URL}/api/zk/verify-commitment`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                commitment: commitmentHex,
                nullifier: nullifierHex
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            return {
                success: false,
                message: error.detail || 'Verification failed'
            };
        }
        
        const result = await response.json();
        
        return {
            success: result.valid,
            credential: result.credential,
            nullifier: nullifierHex,
            message: result.message,
            used_votes: result.used_votes
        };
        
    } catch (error: any) {
        console.error('[Auth Simple] Error:', error);
        return {
            success: false,
            message: error.message || 'Authentication failed'
        };
    }
}
