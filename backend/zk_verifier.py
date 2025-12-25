"""
Zero-Knowledge Proof Verification Module

This module handles server-side verification of zk-SNARK proofs.
Uses snarkjs via Node.js subprocess for reliable verification.
"""

import json
import os
import subprocess
from typing import Dict, List, Any, Tuple
from functools import lru_cache

# Paths
BLOCKCHAIN_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'blockchain'
)
VERIFY_SCRIPT = os.path.join(BLOCKCHAIN_DIR, 'scripts', 'verify_proof.js')
VERIFICATION_KEY_PATH = os.path.join(
    BLOCKCHAIN_DIR, 'circuits', 'build', 'verification_key.json'
)


@lru_cache(maxsize=1)
def load_verification_key() -> Dict[str, Any]:
    """Load and cache the verification key."""
    if os.path.exists(VERIFICATION_KEY_PATH):
        with open(VERIFICATION_KEY_PATH, 'r') as f:
            vkey = json.load(f)
            print(f"[ZK Verify] Loaded verification key from {VERIFICATION_KEY_PATH}")
            return vkey
    raise FileNotFoundError(f"Verification key not found at {VERIFICATION_KEY_PATH}")


def verify_groth16_proof_nodejs(
    proof: Dict[str, Any],
    public_signals: List[str]
) -> Tuple[bool, Dict[str, Any]]:
    """
    Verify a Groth16 proof using snarkjs via Node.js.
    
    This is the most reliable method as it uses the same library
    that generated the proof.
    
    Returns:
        Tuple of (is_valid, result_dict)
    """
    try:
        proof_json = json.dumps(proof)
        signals_json = json.dumps(public_signals)
        
        result = subprocess.run(
            ['node', VERIFY_SCRIPT, proof_json, signals_json],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=BLOCKCHAIN_DIR
        )
        
        if result.stdout:
            output = json.loads(result.stdout.strip())
            return output.get('valid', False), output
        
        if result.stderr:
            return False, {'error': result.stderr}
        
        return result.returncode == 0, {}
        
    except subprocess.TimeoutExpired:
        return False, {'error': 'Verification timeout'}
    except json.JSONDecodeError as e:
        return False, {'error': f'Invalid JSON response: {e}'}
    except FileNotFoundError:
        return False, {'error': 'Node.js or verify script not found'}
    except Exception as e:
        return False, {'error': str(e)}


def verify_proof_simple(
    proof: Dict[str, Any],
    public_signals: List[str]
) -> Tuple[bool, str]:
    """
    Simple wrapper for proof verification with error message.
    Uses Node.js snarkjs for verification.
    
    Returns:
        Tuple of (is_valid, message)
    """
    is_valid, result = verify_groth16_proof_nodejs(proof, public_signals)
    
    if is_valid:
        return True, "Proof verified successfully"
    else:
        error = result.get('error', 'Verification failed')
        return False, f"Invalid proof: {error}"


if __name__ == "__main__":
    # Test loading verification key
    try:
        vkey = load_verification_key()
        print("Verification key loaded successfully!")
        print(f"  Protocol: {vkey.get('protocol')}")
        print(f"  Curve: {vkey.get('curve')}")
        print(f"  IC points: {len(vkey.get('IC', []))}")
    except Exception as e:
        print(f"Failed to load verification key: {e}")
