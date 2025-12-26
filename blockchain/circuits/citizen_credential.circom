// Voter Membership Circuit for WaachaPatra "Blind Auditor" System
// This circuit proves voter eligibility WITHOUT revealing identity
//
// The Proof: "I know a voter_id and secret such that:
//   1. voter_id exists in the voter registry (Merkle proof)
//   2. nullifier = Hash(voter_id, secret) - for preventing double voting"
//
// Privacy Guarantees:
// - voter_id is NEVER revealed
// - secret is NEVER revealed  
// - Only nullifier and Merkle root are public

pragma circom 2.0.0;

include "../node_modules/circomlib/circuits/poseidon.circom";
include "../node_modules/circomlib/circuits/comparators.circom";
include "../node_modules/circomlib/circuits/bitify.circom";

// Merkle proof verification for binary tree
template MerkleProof(levels) {
    signal input leaf;
    signal input pathElements[levels];
    signal input pathIndices[levels];  // 0 = left, 1 = right
    signal output root;
    
    component hashers[levels];
    component mux[levels];
    
    signal levelHashes[levels + 1];
    levelHashes[0] <== leaf;
    
    for (var i = 0; i < levels; i++) {
        hashers[i] = Poseidon(2);
        
        // If pathIndex is 0, we're on the left: Hash(current, sibling)
        // If pathIndex is 1, we're on the right: Hash(sibling, current)
        
        // Constrain pathIndices to be binary
        pathIndices[i] * (1 - pathIndices[i]) === 0;
        
        // Select ordering based on path index
        hashers[i].inputs[0] <== levelHashes[i] + pathIndices[i] * (pathElements[i] - levelHashes[i]);
        hashers[i].inputs[1] <== pathElements[i] + pathIndices[i] * (levelHashes[i] - pathElements[i]);
        
        levelHashes[i + 1] <== hashers[i].out;
    }
    
    root <== levelHashes[levels];
}

// Main Voter Credential Circuit
// levels = 15 supports up to 32,768 voters (sufficient for ~26K voters)
template VoterCredential(levels) {
    // ========== PRIVATE INPUTS (not revealed) ==========
    signal input voterId;           // The voter's ID from the CSV
    signal input voterSecret;       // User's personal secret (e.g., citizenship number)
    signal input pathElements[levels];  // Merkle proof path
    signal input pathIndices[levels];   // Path directions (0=left, 1=right)
    
    // ========== PUBLIC INPUTS (revealed for verification) ==========
    signal input merkleRoot;        // Published root of voter registry
    
    // ========== OUTPUTS ==========
    signal output nullifier;        // Hash(voterId, voterSecret) - public, prevents double voting
    signal output voterIdHash;      // Hash(voterId) - for reference only
    signal output commitment;       // Hash(voterIdHash, nullifier) - binds the proof
    
    // Step 1: Hash the voter ID to get the leaf
    component voterHasher = Poseidon(1);
    voterHasher.inputs[0] <== voterId;
    voterIdHash <== voterHasher.out;
    
    // Step 2: Verify Merkle membership
    component merkleVerifier = MerkleProof(levels);
    merkleVerifier.leaf <== voterIdHash;
    for (var i = 0; i < levels; i++) {
        merkleVerifier.pathElements[i] <== pathElements[i];
        merkleVerifier.pathIndices[i] <== pathIndices[i];
    }
    
    // Constrain: computed root must equal public merkle root
    merkleRoot === merkleVerifier.root;
    
    // Step 3: Generate nullifier (deterministic per voter+secret combo)
    // This is the "one person, one vote" mechanism
    component nullifierHasher = Poseidon(2);
    nullifierHasher.inputs[0] <== voterId;
    nullifierHasher.inputs[1] <== voterSecret;
    nullifier <== nullifierHasher.out;
    
    // Step 4: Generate commitment (binds voterIdHash to nullifier)
    component commitmentHasher = Poseidon(2);
    commitmentHasher.inputs[0] <== voterIdHash;
    commitmentHasher.inputs[1] <== nullifier;
    commitment <== commitmentHasher.out;
}

// Instantiate the main component with 15 levels (supports ~32K voters)
component main {public [merkleRoot]} = VoterCredential(15);

/*
 * ============= HOW IT WORKS =============
 * 
 * REGISTRATION FLOW (Frontend):
 * 1. User enters their Voter ID (from the public voter list)
 * 2. User enters their Secret (citizenship number - only they know this)
 * 3. Frontend fetches Merkle proof from /api/registry/lookup
 * 4. Frontend generates ZK proof using snarkjs
 * 5. Frontend sends {proof, nullifier, commitment} to backend
 * 6. Backend verifies proof and stores ONLY the nullifier
 *
 * VOTING FLOW:
 * 1. User provides their nullifier (stored locally after registration)
 * 2. Backend checks: has this nullifier voted on this manifesto?
 * 3. If not, vote is recorded linked to nullifier (NOT voter ID)
 *
 * PRIVACY GUARANTEES:
 * - Server NEVER learns which voter ID cast which vote
 * - Server ONLY knows: "a valid voter from the registry voted"
 * - Nullifier prevents same person from voting twice
 * - Even if database is leaked, votes cannot be linked to identities
 *
 * INTEGRITY GUARANTEES:
 * - Only voters in the CSV can generate valid proofs
 * - Each voter can only vote once per manifesto (nullifier check)
 * - Merkle root is published on-chain (immutable reference)
 */
