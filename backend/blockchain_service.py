"""
Blockchain Service - Real Web3 Integration
==========================================
Connects backend to deployed smart contracts on Hardhat/Ethereum.

This module provides:
- READ: Fetch manifesto data directly from blockchain
- WRITE: Submit manifestos to blockchain (tx first, then DB)
- VERIFY: Verify manifesto authenticity on-chain

Architecture:
- Blockchain is the SOURCE OF TRUTH
- Database is a CACHE/MIRROR for fast queries
- All verification reads from chain, not DB
"""

import json
import os
from pathlib import Path
from typing import Optional, Tuple, Dict, Any, List
from datetime import datetime, timezone
from web3 import Web3
from web3.exceptions import ContractLogicError, TransactionNotFound
from eth_account import Account
from eth_account.messages import encode_defunct

# =============================================================================
# CONFIGURATION
# =============================================================================

# Default to local Hardhat node
RPC_URL = os.getenv("BLOCKCHAIN_RPC_URL", "http://localhost:8545")
CHAIN_ID = int(os.getenv("BLOCKCHAIN_CHAIN_ID", "31337"))

# Contract addresses (from deployments.json)
MANIFESTO_REGISTRY_ADDRESS = os.getenv(
    "MANIFESTO_REGISTRY_ADDRESS",
    "0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512"
)
PROMISE_REGISTRY_ADDRESS = os.getenv(
    "PROMISE_REGISTRY_ADDRESS",
    "0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0"
)

# Demo signer key (Hardhat account #0 - NEVER use in production!)
# This is for demonstration only - in production, politicians sign client-side
DEMO_SIGNER_KEY = os.getenv(
    "DEMO_SIGNER_KEY",
    "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
)

# Path to contract artifacts
ARTIFACTS_PATH = Path(__file__).parent.parent / "blockchain" / "artifacts" / "contracts"


# =============================================================================
# WEB3 CONNECTION
# =============================================================================

class BlockchainService:
    """
    Service for interacting with deployed smart contracts.
    
    Usage:
        blockchain = BlockchainService()
        
        # Read
        result = blockchain.verify_manifesto(politician_id=1, content_hash="0x...")
        manifestos = blockchain.get_politician_manifestos(politician_id=1)
        
        # Write
        tx_hash = blockchain.submit_manifesto(politician_id=1, content_hash="0x...", signer_key="0x...")
    """
    
    def __init__(self, rpc_url: str = RPC_URL):
        """Initialize Web3 connection and load contracts."""
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.chain_id = CHAIN_ID
        self.connected = False
        self.manifesto_registry = None
        self.promise_registry = None
        
        self._connect()
    
    def _connect(self) -> bool:
        """Establish connection to blockchain node."""
        try:
            if self.w3.is_connected():
                self.connected = True
                self._load_contracts()
                print(f"✓ Connected to blockchain at {RPC_URL}")
                print(f"  Chain ID: {self.chain_id}")
                print(f"  Latest block: {self.w3.eth.block_number}")
                return True
            else:
                print(f"⚠️ Failed to connect to blockchain at {RPC_URL}")
                self.connected = False
                return False
        except Exception as e:
            print(f"⚠️ Blockchain connection error: {e}")
            self.connected = False
            return False
    
    def _load_contracts(self):
        """Load contract ABIs and create contract instances."""
        # Load ManifestoRegistry
        manifesto_abi_path = ARTIFACTS_PATH / "ManifestoRegistry.sol" / "ManifestoRegistry.json"
        if manifesto_abi_path.exists():
            with open(manifesto_abi_path) as f:
                artifact = json.load(f)
                self.manifesto_registry = self.w3.eth.contract(
                    address=Web3.to_checksum_address(MANIFESTO_REGISTRY_ADDRESS),
                    abi=artifact["abi"]
                )
                print(f"  ✓ ManifestoRegistry loaded at {MANIFESTO_REGISTRY_ADDRESS}")
        else:
            print(f"  ⚠️ ManifestoRegistry ABI not found at {manifesto_abi_path}")
        
        # Load PromiseRegistry
        promise_abi_path = ARTIFACTS_PATH / "PromiseRegistry.sol" / "PromiseRegistry.json"
        if promise_abi_path.exists():
            with open(promise_abi_path) as f:
                artifact = json.load(f)
                self.promise_registry = self.w3.eth.contract(
                    address=Web3.to_checksum_address(PROMISE_REGISTRY_ADDRESS),
                    abi=artifact["abi"]
                )
                print(f"  ✓ PromiseRegistry loaded at {PROMISE_REGISTRY_ADDRESS}")
        else:
            print(f"  ⚠️ PromiseRegistry ABI not found at {promise_abi_path}")
    
    def is_connected(self) -> bool:
        """Check if blockchain connection is active."""
        try:
            return self.w3.is_connected() and self.connected
        except:
            return False
    
    def get_block_number(self) -> int:
        """Get current block number."""
        if not self.is_connected():
            return 0
        return self.w3.eth.block_number
    
    # =========================================================================
    # READ OPERATIONS (ManifestoRegistry)
    # =========================================================================
    
    def is_politician_registered(self, politician_id: int, wallet_address: str) -> bool:
        """
        Check if a politician is registered with a specific wallet.
        
        Args:
            politician_id: The politician's ID
            wallet_address: The wallet address to check
            
        Returns:
            True if the wallet is registered for this politician
        """
        if not self.manifesto_registry:
            return False
        
        try:
            return self.manifesto_registry.functions.isPoliticianWallet(
                politician_id,
                Web3.to_checksum_address(wallet_address)
            ).call()
        except ContractLogicError as e:
            print(f"Contract error: {e}")
            return False
        except Exception as e:
            print(f"Error checking politician registration: {e}")
            return False
    
    def get_politician(self, politician_id: int) -> Optional[Dict[str, Any]]:
        """
        Get politician info from blockchain.
        
        Returns:
            Dict with wallet, manifestoCount, isRegistered
        """
        if not self.manifesto_registry:
            return None
        
        try:
            result = self.manifesto_registry.functions.getPolitician(politician_id).call()
            return {
                "wallet": result[0],
                "manifesto_count": result[1],
                "is_registered": result[2]
            }
        except ContractLogicError:
            return None
        except Exception as e:
            print(f"Error getting politician: {e}")
            return None
    
    def verify_manifesto(self, politician_id: int, content_hash: str) -> Dict[str, Any]:
        """
        Verify a manifesto hash on-chain.
        
        This is the KEY verification function - reads directly from blockchain!
        
        Args:
            politician_id: The politician's ID
            content_hash: The SHA256 hash of manifesto text (0x prefixed)
            
        Returns:
            Dict with verified (bool), timestamp, index
        """
        if not self.manifesto_registry:
            return {"verified": False, "error": "Contract not loaded", "source": "error"}
        
        try:
            # Convert hash string to bytes32
            if content_hash.startswith("0x"):
                hash_bytes = bytes.fromhex(content_hash[2:].ljust(64, '0'))
            else:
                hash_bytes = bytes.fromhex(content_hash.ljust(64, '0'))
            
            result = self.manifesto_registry.functions.verifyManifesto(
                politician_id,
                hash_bytes
            ).call()
            
            return {
                "verified": result[0],
                "timestamp": result[1],
                "timestamp_iso": datetime.fromtimestamp(result[1], tz=timezone.utc).isoformat() if result[1] > 0 else None,
                "index": result[2],
                "source": "blockchain",
                "contract": MANIFESTO_REGISTRY_ADDRESS,
                "chain_id": self.chain_id
            }
        except ContractLogicError as e:
            return {"verified": False, "error": str(e), "source": "blockchain"}
        except Exception as e:
            print(f"Error verifying manifesto: {e}")
            return {"verified": False, "error": str(e), "source": "error"}
    
    def lookup_hash(self, content_hash: str) -> Dict[str, Any]:
        """
        Reverse lookup: find politician by manifesto hash.
        
        Args:
            content_hash: The SHA256 hash to look up
            
        Returns:
            Dict with politician_id, exists, timestamp
        """
        if not self.manifesto_registry:
            return {"exists": False, "error": "Contract not loaded"}
        
        try:
            if content_hash.startswith("0x"):
                hash_bytes = bytes.fromhex(content_hash[2:].ljust(64, '0'))
            else:
                hash_bytes = bytes.fromhex(content_hash.ljust(64, '0'))
            
            result = self.manifesto_registry.functions.lookupHash(hash_bytes).call()
            
            return {
                "politician_id": result[0],
                "exists": result[1],
                "timestamp": result[2],
                "timestamp_iso": datetime.fromtimestamp(result[2], tz=timezone.utc).isoformat() if result[2] > 0 else None,
                "source": "blockchain"
            }
        except Exception as e:
            print(f"Error looking up hash: {e}")
            return {"exists": False, "error": str(e)}
    
    def get_manifesto(self, content_hash: str) -> Optional[Dict[str, Any]]:
        """
        Get manifesto data by hash.
        
        Args:
            content_hash: The manifesto hash
            
        Returns:
            Dict with contentHash, politicianId, timestamp, blockNumber
        """
        if not self.manifesto_registry:
            return None
        
        try:
            if content_hash.startswith("0x"):
                hash_bytes = bytes.fromhex(content_hash[2:].ljust(64, '0'))
            else:
                hash_bytes = bytes.fromhex(content_hash.ljust(64, '0'))
            
            result = self.manifesto_registry.functions.getManifesto(hash_bytes).call()
            
            return {
                "content_hash": "0x" + result[0].hex(),
                "politician_id": result[1],
                "timestamp": result[2],
                "timestamp_iso": datetime.fromtimestamp(result[2], tz=timezone.utc).isoformat() if result[2] > 0 else None,
                "block_number": result[3],
                "source": "blockchain"
            }
        except ContractLogicError:
            return None
        except Exception as e:
            print(f"Error getting manifesto: {e}")
            return None
    
    def get_politician_manifestos(self, politician_id: int) -> List[Dict[str, Any]]:
        """
        Get all manifesto hashes for a politician.
        
        Args:
            politician_id: The politician's ID
            
        Returns:
            List of manifesto data dicts
        """
        if not self.manifesto_registry:
            return []
        
        try:
            result = self.manifesto_registry.functions.getPoliticianManifestos(politician_id).call()
            
            # Contract returns [hashes[], timestamps[]] - two parallel arrays
            if len(result) != 2:
                return []
            
            hashes = result[0]
            timestamps = result[1]
            
            manifestos = []
            for i in range(len(hashes)):
                content_hash = hashes[i]
                timestamp = timestamps[i] if i < len(timestamps) else 0
                
                manifestos.append({
                    "content_hash": "0x" + content_hash.hex(),
                    "politician_id": politician_id,
                    "timestamp": timestamp,
                    "timestamp_iso": datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat() if timestamp > 0 else None,
                    "block_number": None  # Not returned by this function
                })
            
            return manifestos
        except ContractLogicError:
            return []
        except Exception as e:
            print(f"Error getting politician manifestos: {e}")
            return []
    
    # =========================================================================
    # WRITE OPERATIONS (ManifestoRegistry)
    # =========================================================================
    
    def register_politician(
        self,
        politician_id: int,
        signer_key: str = DEMO_SIGNER_KEY
    ) -> Dict[str, Any]:
        """
        Register a politician on-chain.
        
        Args:
            politician_id: The politician's ID
            signer_key: Private key to sign transaction
            
        Returns:
            Dict with success, tx_hash, block_number
        """
        if not self.manifesto_registry:
            return {"success": False, "error": "Contract not loaded"}
        
        try:
            account = Account.from_key(signer_key)
            
            # Build transaction
            tx = self.manifesto_registry.functions.registerPolitician(
                politician_id
            ).build_transaction({
                'from': account.address,
                'nonce': self.w3.eth.get_transaction_count(account.address),
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price,
                'chainId': self.chain_id
            })
            
            # Sign and send
            signed_tx = self.w3.eth.account.sign_transaction(tx, signer_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            # Wait for receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            return {
                "success": receipt.status == 1,
                "tx_hash": tx_hash.hex(),
                "block_number": receipt.blockNumber,
                "gas_used": receipt.gasUsed,
                "signer": account.address
            }
        except ContractLogicError as e:
            return {"success": False, "error": f"Contract error: {e}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def submit_manifesto(
        self,
        politician_id: int,
        content_hash: str,
        signer_key: str = DEMO_SIGNER_KEY
    ) -> Dict[str, Any]:
        """
        Submit a manifesto hash to blockchain.
        
        THIS IS THE KEY WRITE FUNCTION.
        
        Flow:
        1. Build transaction
        2. Sign with politician's key (or demo key)
        3. Send to blockchain
        4. Wait for confirmation
        5. Return tx details for DB storage
        
        Args:
            politician_id: The politician's ID
            content_hash: SHA256 hash of manifesto text
            signer_key: Private key to sign (politician's or demo)
            
        Returns:
            Dict with success, tx_hash, block_number, timestamp
        """
        if not self.manifesto_registry:
            return {"success": False, "error": "Contract not loaded"}
        
        try:
            account = Account.from_key(signer_key)
            
            # Convert hash to bytes32
            if content_hash.startswith("0x"):
                hash_bytes = bytes.fromhex(content_hash[2:].ljust(64, '0'))
            else:
                hash_bytes = bytes.fromhex(content_hash.ljust(64, '0'))
            
            # Build transaction
            tx = self.manifesto_registry.functions.submitManifesto(
                politician_id,
                hash_bytes
            ).build_transaction({
                'from': account.address,
                'nonce': self.w3.eth.get_transaction_count(account.address),
                'gas': 300000,
                'gasPrice': self.w3.eth.gas_price,
                'chainId': self.chain_id
            })
            
            # Sign transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx, signer_key)
            
            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            # Wait for receipt (CRITICAL - must confirm before DB write)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            if receipt.status != 1:
                return {
                    "success": False,
                    "error": "Transaction reverted",
                    "tx_hash": tx_hash.hex()
                }
            
            # Get block timestamp
            block = self.w3.eth.get_block(receipt.blockNumber)
            
            return {
                "success": True,
                "tx_hash": tx_hash.hex(),
                "block_number": receipt.blockNumber,
                "block_timestamp": block.timestamp,
                "block_timestamp_iso": datetime.fromtimestamp(block.timestamp, tz=timezone.utc).isoformat(),
                "gas_used": receipt.gasUsed,
                "signer": account.address,
                "content_hash": content_hash,
                "politician_id": politician_id,
                "source": "blockchain"
            }
            
        except ContractLogicError as e:
            error_msg = str(e)
            if "Not authorized" in error_msg:
                return {"success": False, "error": "Wallet not registered for this politician"}
            elif "already exists" in error_msg or "Duplicate" in error_msg:
                return {"success": False, "error": "Manifesto hash already submitted"}
            return {"success": False, "error": f"Contract error: {e}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def update_politician_wallet(
        self,
        politician_id: int,
        new_wallet: str,
        current_signer_key: str
    ) -> Dict[str, Any]:
        """
        Update a politician's wallet address (key rotation).
        
        Args:
            politician_id: The politician's ID
            new_wallet: New wallet address
            current_signer_key: Current private key
            
        Returns:
            Dict with success, tx_hash, etc.
        """
        if not self.manifesto_registry:
            return {"success": False, "error": "Contract not loaded"}
        
        try:
            account = Account.from_key(current_signer_key)
            
            tx = self.manifesto_registry.functions.updateWallet(
                politician_id,
                Web3.to_checksum_address(new_wallet)
            ).build_transaction({
                'from': account.address,
                'nonce': self.w3.eth.get_transaction_count(account.address),
                'gas': 100000,
                'gasPrice': self.w3.eth.gas_price,
                'chainId': self.chain_id
            })
            
            signed_tx = self.w3.eth.account.sign_transaction(tx, current_signer_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            return {
                "success": receipt.status == 1,
                "tx_hash": tx_hash.hex(),
                "block_number": receipt.blockNumber,
                "old_wallet": account.address,
                "new_wallet": new_wallet
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # =========================================================================
    # UTILITY FUNCTIONS
    # =========================================================================
    
    def compute_hash(self, text: str) -> str:
        """
        Compute SHA256 hash of text (matching contract's computeHash).
        
        Args:
            text: The manifesto text
            
        Returns:
            0x-prefixed hash string
        """
        if not self.manifesto_registry:
            # Fallback to local computation
            import hashlib
            return "0x" + hashlib.sha256(text.encode()).hexdigest()
        
        try:
            result = self.manifesto_registry.functions.computeHash(text).call()
            return "0x" + result.hex()
        except Exception:
            # Fallback to local computation
            import hashlib
            return "0x" + hashlib.sha256(text.encode()).hexdigest()
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get current connection status and info."""
        return {
            "connected": self.is_connected(),
            "rpc_url": RPC_URL,
            "chain_id": self.chain_id,
            "block_number": self.get_block_number() if self.is_connected() else 0,
            "contracts": {
                "manifesto_registry": {
                    "address": MANIFESTO_REGISTRY_ADDRESS,
                    "loaded": self.manifesto_registry is not None
                },
                "promise_registry": {
                    "address": PROMISE_REGISTRY_ADDRESS,
                    "loaded": self.promise_registry is not None
                }
            }
        }


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

# Create a singleton instance for the application
_blockchain_service: Optional[BlockchainService] = None


def get_blockchain_service() -> BlockchainService:
    """Get or create the blockchain service singleton."""
    global _blockchain_service
    if _blockchain_service is None:
        _blockchain_service = BlockchainService()
    return _blockchain_service


def reset_blockchain_service():
    """Reset the blockchain service (useful for testing)."""
    global _blockchain_service
    _blockchain_service = None


# =============================================================================
# QUICK TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Blockchain Service Test")
    print("=" * 60)
    
    service = get_blockchain_service()
    
    print("\n📊 Connection Info:")
    info = service.get_connection_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    if service.is_connected():
        print("\n🔍 Testing Read Operations:")
        
        # Test verify manifesto
        test_hash = "0x" + "a" * 64
        result = service.verify_manifesto(1, test_hash)
        print(f"  verifyManifesto(1, {test_hash[:20]}...): {result}")
        
        # Test lookup hash
        result = service.lookup_hash(test_hash)
        print(f"  lookupHash({test_hash[:20]}...): {result}")
        
        # Test get politician
        result = service.get_politician(1)
        print(f"  getPolitician(1): {result}")
    
    print("\n✅ Test complete!")
