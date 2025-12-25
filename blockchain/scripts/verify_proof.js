/**
 * ZK Proof Verifier - Node.js Script
 * 
 * This script verifies Groth16 proofs using snarkjs.
 * Called by Python backend via subprocess.
 * 
 * Usage: node verify_proof.js <proof_json> <public_signals_json>
 */

const snarkjs = require('snarkjs');
const fs = require('fs');
const path = require('path');

// Path to verification key
const VKEY_PATH = path.join(__dirname, '..', 'circuits', 'build', 'verification_key.json');

async function verifyProof(proofJson, publicSignalsJson) {
    try {
        // Load verification key
        const vkey = JSON.parse(fs.readFileSync(VKEY_PATH, 'utf8'));
        
        // Parse proof and signals
        const proof = JSON.parse(proofJson);
        const publicSignals = JSON.parse(publicSignalsJson);
        
        // Verify
        const isValid = await snarkjs.groth16.verify(vkey, publicSignals, proof);
        
        // Output result as JSON
        console.log(JSON.stringify({
            valid: isValid,
            nullifier: publicSignals[0],
            voterIdHash: publicSignals[1],
            commitment: publicSignals[2]
        }));
        
        process.exit(isValid ? 0 : 1);
    } catch (error) {
        console.error(JSON.stringify({
            valid: false,
            error: error.message
        }));
        process.exit(1);
    }
}

// Get arguments
const args = process.argv.slice(2);
if (args.length < 2) {
    console.error('Usage: node verify_proof.js <proof_json> <public_signals_json>');
    process.exit(1);
}

verifyProof(args[0], args[1]);
