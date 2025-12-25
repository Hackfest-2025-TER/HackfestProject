"""
Cryptographic Utilities for PromiseThread
==========================================
Handles key generation, signatures, and verification.

Security Architecture:
- Private keys are NEVER stored on server
- Keys are generated and encrypted client-side (or given to user)
- Backend only verifies signatures, never creates them
- Keystore format follows Ethereum standards (Web3 Secret Storage)
"""

import hashlib
import json
import os
import secrets
from datetime import datetime, timezone
from typing import Optional, Tuple, Dict, Any

# Try to import eth_account, fall back to simulation if not available
try:
    from eth_account import Account
    from eth_account.messages import encode_defunct
    from web3 import Web3
    ETH_AVAILABLE = True
except ImportError:
    ETH_AVAILABLE = False
    print("⚠️ eth_account not installed. Using simulated crypto.")


# =============================================================================
# KEY GENERATION
# =============================================================================

def generate_key_pair() -> Tuple[str, str, str]:
    """
    Generate a new Ethereum-compatible key pair.
    
    Returns:
        Tuple of (private_key, public_key, address)
        
    IMPORTANT: private_key should be shown to user ONCE and never stored.
    """
    if ETH_AVAILABLE:
        account = Account.create()
        private_key = account.key.hex()
        public_key = account._key_obj.public_key.to_hex() if hasattr(account, '_key_obj') else ""
        address = account.address
    else:
        # Simulated key generation for development
        private_key = "0x" + secrets.token_hex(32)
        public_key = "0x04" + secrets.token_hex(64)  # Simulated uncompressed public key
        address = "0x" + secrets.token_hex(20)
    
    return private_key, public_key, address


def create_encrypted_keystore(
    private_key: str, 
    passphrase: str,
    address: str
) -> Dict[str, Any]:
    """
    Create an encrypted keystore file (Web3 Secret Storage format).
    
    This is the standard Ethereum keystore format that can be:
    - Safely stored in multiple locations
    - Decrypted only with the passphrase
    - Imported into any Ethereum wallet
    
    Args:
        private_key: The private key to encrypt (0x...)
        passphrase: User-chosen passphrase
        address: The wallet address
        
    Returns:
        Keystore JSON structure (can be saved as file)
    """
    if ETH_AVAILABLE:
        # Use proper Ethereum keystore format
        keystore = Account.encrypt(private_key, passphrase)
        return keystore
    else:
        # Simulated keystore for development
        # In production, this should use proper encryption
        import base64
        
        # Simple simulation (NOT SECURE - for demo only)
        salt = secrets.token_hex(16)
        iv = secrets.token_hex(16)
        
        # Simulated encryption
        encrypted = base64.b64encode(
            f"{private_key}:{passphrase}:{salt}".encode()
        ).decode()
        
        return {
            "version": 3,
            "id": secrets.token_hex(16),
            "address": address.lower().replace("0x", ""),
            "crypto": {
                "ciphertext": encrypted,
                "cipherparams": {"iv": iv},
                "cipher": "aes-128-ctr",
                "kdf": "scrypt",
                "kdfparams": {
                    "dklen": 32,
                    "salt": salt,
                    "n": 262144,
                    "r": 8,
                    "p": 1
                },
                "mac": secrets.token_hex(32)
            },
            "meta": {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "platform": "PromiseThread"
            }
        }


def decrypt_keystore(keystore: Dict[str, Any], passphrase: str) -> Optional[str]:
    """
    Decrypt a keystore file to recover the private key.
    
    This should typically happen CLIENT-SIDE, not on server.
    This function is provided for testing/verification only.
    
    Args:
        keystore: The keystore JSON structure
        passphrase: The user's passphrase
        
    Returns:
        Private key (0x...) or None if decryption fails
    """
    if ETH_AVAILABLE:
        try:
            private_key = Account.decrypt(keystore, passphrase)
            return "0x" + private_key.hex()
        except Exception:
            return None
    else:
        # Simulated decryption for development
        import base64
        try:
            encrypted = keystore["crypto"]["ciphertext"]
            decoded = base64.b64decode(encrypted).decode()
            parts = decoded.split(":")
            if len(parts) >= 2 and parts[1] == passphrase:
                return parts[0]
            return None
        except Exception:
            return None


# =============================================================================
# HASHING
# =============================================================================

def compute_manifesto_hash(manifesto_text: str) -> str:
    """
    Compute keccak256 hash of manifesto text (matches Solidity keccak256).
    
    This is the "commitment" that goes on blockchain.
    Anyone can verify by hashing the text and comparing.
    
    IMPORTANT: Uses keccak256 to match smart contract implementation.
    
    Args:
        manifesto_text: Full manifesto text
        
    Returns:
        Hash as hex string (0x...)
    """
    if ETH_AVAILABLE:
        # Use proper keccak256 (matches Solidity)
        return Web3.keccak(text=manifesto_text).hex()
    else:
        # Fallback for development (not cryptographically equivalent!)
        hash_bytes = hashlib.sha256(manifesto_text.encode('utf-8')).digest()
        return "0x" + hash_bytes.hex()


def compute_message_hash(message: str) -> bytes:
    """
    Compute keccak256 hash of message for signing.
    
    Args:
        message: Message to hash
        
    Returns:
        Hash as bytes
    """
    if ETH_AVAILABLE:
        return Web3.keccak(text=message)
    else:
        # Fallback to SHA256 for simulation
        return hashlib.sha256(message.encode()).digest()


# =============================================================================
# SIGNATURE VERIFICATION
# =============================================================================

def verify_signature(
    message: str,
    signature: str,
    expected_address: str
) -> Tuple[bool, Optional[str]]:
    """
    Verify that a signature was created by the expected address.
    
    This is the core verification function that proves:
    1. The message hasn't been tampered with
    2. The signer owns the private key for expected_address
    
    Args:
        message: The original message that was signed
        signature: The signature (hex string)
        expected_address: The expected signer's address (0x...)
        
    Returns:
        Tuple of (is_valid, recovered_address)
    """
    if ETH_AVAILABLE:
        try:
            message_hash = compute_message_hash(message)
            signable = encode_defunct(message_hash)
            recovered = Account.recover_message(signable, signature=signature)
            is_valid = recovered.lower() == expected_address.lower()
            return is_valid, recovered
        except Exception as e:
            print(f"Signature verification error: {e}")
            return False, None
    else:
        # Simulated verification for development
        # In simulation, we can't actually verify, so we check format
        if signature and len(signature) > 100:
            # Simulated: extract address from signature (NOT SECURE)
            try:
                # Our simulation encodes address in signature
                if "|" in signature:
                    parts = signature.split("|")
                    embedded_addr = parts[0]
                    is_valid = embedded_addr.lower() == expected_address.lower()
                    return is_valid, embedded_addr
            except:
                pass
        return False, None


def create_signature(message: str, private_key: str) -> str:
    """
    Create a signature for a message.
    
    NOTE: This should typically happen CLIENT-SIDE.
    This function is provided for testing only.
    
    Args:
        message: Message to sign
        private_key: Private key (0x...)
        
    Returns:
        Signature as hex string
    """
    if ETH_AVAILABLE:
        message_hash = compute_message_hash(message)
        signable = encode_defunct(message_hash)
        signed = Account.sign_message(signable, private_key)
        return signed.signature.hex()
    else:
        # Simulated signature for development
        # Embeds address for verification (NOT SECURE)
        from eth_account import Account as SimAccount
        try:
            acct = SimAccount.from_key(private_key)
            address = acct.address
        except:
            address = "0x" + hashlib.sha256(private_key.encode()).hexdigest()[:40]
        
        # Create simulated signature with embedded address
        sig_data = hashlib.sha256(f"{message}:{private_key}".encode()).hexdigest()
        return f"{address}|{sig_data}"


# =============================================================================
# KEY ROTATION
# =============================================================================

def generate_rotation_proof(
    old_address: str,
    new_address: str,
    reason: str,
    timestamp: datetime
) -> Dict[str, Any]:
    """
    Generate proof data for key rotation event.
    
    This creates a record that can be stored on-chain to prove
    that a key rotation was legitimate.
    
    Args:
        old_address: Previous wallet address
        new_address: New wallet address
        reason: Reason for rotation (lost, compromised, etc.)
        timestamp: When rotation occurred
        
    Returns:
        Rotation proof data structure
    """
    rotation_data = {
        "old_address": old_address,
        "new_address": new_address,
        "reason": reason,
        "timestamp": timestamp.isoformat(),
        "rotation_hash": compute_manifesto_hash(
            f"{old_address}:{new_address}:{reason}:{timestamp.isoformat()}"
        )
    }
    return rotation_data


# =============================================================================
# VERIFICATION HELPERS
# =============================================================================

def get_verification_bundle(
    manifesto_text: str,
    stored_hash: str,
    signature: str,
    signer_address: str,
    blockchain_tx: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a complete verification bundle for a manifesto.
    
    This bundle contains everything needed for independent verification:
    - Anyone can hash the text and compare
    - Anyone can verify the signature
    - Anyone can check the blockchain transaction
    
    Args:
        manifesto_text: Full manifesto text
        stored_hash: Hash stored in database/blockchain
        signature: Politician's signature
        signer_address: Politician's wallet address
        blockchain_tx: Optional blockchain transaction hash
        
    Returns:
        Complete verification bundle
    """
    computed_hash = compute_manifesto_hash(manifesto_text)
    hash_matches = computed_hash == stored_hash
    
    sig_valid, recovered_addr = verify_signature(manifesto_text, signature, signer_address)
    
    return {
        "verification_results": {
            "hash_matches": hash_matches,
            "signature_valid": sig_valid,
            "blockchain_recorded": bool(blockchain_tx)
        },
        "computed_hash": computed_hash,
        "stored_hash": stored_hash,
        "signature": signature,
        "expected_signer": signer_address,
        "recovered_signer": recovered_addr,
        "blockchain_tx": blockchain_tx,
        "overall_valid": hash_matches and sig_valid,
        "verification_instructions": [
            "1. Download the manifesto text",
            "2. Compute keccak256 hash of the text (matches Solidity)",
            "3. Compare with stored_hash (should match)",
            "4. Verify signature recovers to expected_signer",
            "5. Optional: Check blockchain_tx on block explorer"
        ]
    }


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def is_valid_address(address: str) -> bool:
    """Check if a string is a valid Ethereum address."""
    if not address or not isinstance(address, str):
        return False
    if not address.startswith("0x"):
        return False
    if len(address) != 42:
        return False
    try:
        int(address, 16)
        return True
    except ValueError:
        return False


def is_valid_signature(signature: str) -> bool:
    """Check if a string looks like a valid signature."""
    if not signature or not isinstance(signature, str):
        return False
    # Ethereum signatures are 65 bytes = 130 hex chars (+ optional 0x)
    sig = signature.replace("0x", "")
    return len(sig) >= 128 and all(c in "0123456789abcdefABCDEF" for c in sig[:128])


def format_address_short(address: str) -> str:
    """Format address for display (0x1234...5678)."""
    if not address or len(address) < 10:
        return address or ""
    return f"{address[:6]}...{address[-4:]}"
