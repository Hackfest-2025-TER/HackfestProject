import csv
import hashlib
import json
import math
import os
import random
import secrets
import subprocess


class PoseidonHasher:
    """
    Poseidon hash using Node.js subprocess.
    
    Uses circomlibjs Poseidon implementation to match the circuit exactly.
    This ensures frontend and backend produce identical hashes.
    """
    
    SCRIPT_PATH = None
    
    @classmethod
    def _get_script_path(cls):
        if cls.SCRIPT_PATH is None:
            # Find the poseidon_hash.js script
            backend_dir = os.path.dirname(os.path.dirname(__file__))
            project_root = os.path.dirname(backend_dir)
            cls.SCRIPT_PATH = os.path.join(project_root, "blockchain", "scripts", "poseidon_hash.js")
        return cls.SCRIPT_PATH
    
    @classmethod
    def hash_voter_leaf(cls, voter_id: str) -> dict:
        """
        Generate voter leaf for Merkle tree: Poseidon(voterId)
        
        This MUST match the circuit:
            voterIdHash = Poseidon(voterId)
        
        The leaf is what goes into the Merkle tree.
        """
        script = cls._get_script_path()
        
        try:
            result = subprocess.run(
                ["node", script, "voter-leaf", voter_id],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=os.path.dirname(script)
            )
            
            if result.returncode != 0:
                raise Exception(f"Poseidon hash failed: {result.stderr}")
            
            return json.loads(result.stdout)
        except subprocess.TimeoutExpired:
            raise Exception("Poseidon hash timeout")
        except json.JSONDecodeError:
            raise Exception(f"Invalid Poseidon output: {result.stdout}")
    
    @classmethod
    def batch_hash_voter_leaves(cls, voter_ids: list) -> list:
        """
        Generate voter leaves in batch for efficiency.
        
        Batching avoids subprocess overhead for each voter.
        ~1000 voters takes ~1 second vs ~60 seconds with individual calls.
        """
        script = cls._get_script_path()
        voter_ids_json = json.dumps(voter_ids)
        
        try:
            result = subprocess.run(
                ["node", script, "batch-voter-leaves", voter_ids_json],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=os.path.dirname(script)
            )
            
            if result.returncode != 0:
                raise Exception(f"Batch Poseidon hash failed: {result.stderr}")
            
            data = json.loads(result.stdout)
            return data["leaves"]
        except subprocess.TimeoutExpired:
            raise Exception("Batch Poseidon hash timeout")
        except json.JSONDecodeError:
            raise Exception(f"Invalid batch Poseidon output: {result.stdout}")
    
    @classmethod
    def hash_commitment(cls, secret: str, voter_id: str) -> dict:
        """
        Generate voter commitment: Poseidon(secret, voterId)
        
        This binds the voter to their secret but is NOT stored in the tree.
        The tree stores Poseidon(voterId) only.
        """
        script = cls._get_script_path()
        
        try:
            result = subprocess.run(
                ["node", script, "commitment", secret, voter_id],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=os.path.dirname(script)
            )
            
            if result.returncode != 0:
                raise Exception(f"Poseidon hash failed: {result.stderr}")
            
            return json.loads(result.stdout)
        except subprocess.TimeoutExpired:
            raise Exception("Poseidon hash timeout")
        except json.JSONDecodeError:
            raise Exception(f"Invalid Poseidon output: {result.stdout}")
    
    @classmethod
    def build_merkle_tree(cls, leaves: list, depth: int = 15) -> dict:
        """Build Merkle tree from commitment leaves"""
        script = cls._get_script_path()
        leaves_json = json.dumps(leaves)
        
        try:
            result = subprocess.run(
                ["node", script, "merkle", leaves_json, str(depth)],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=os.path.dirname(script)
            )
            
            if result.returncode != 0:
                raise Exception(f"Merkle tree build failed: {result.stderr}")
            
            return json.loads(result.stdout)
        except subprocess.TimeoutExpired:
            raise Exception("Merkle tree build timeout")
    
    @classmethod
    def get_merkle_proof(cls, leaf_index: int, leaves: list, depth: int = 15) -> dict:
        """Generate Merkle proof for a leaf"""
        script = cls._get_script_path()
        leaves_json = json.dumps(leaves)
        
        try:
            result = subprocess.run(
                ["node", script, "proof", str(leaf_index), leaves_json, str(depth)],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=os.path.dirname(script)
            )
            
            if result.returncode != 0:
                raise Exception(f"Merkle proof generation failed: {result.stderr}")
            
            return json.loads(result.stdout)
        except subprocess.TimeoutExpired:
            raise Exception("Merkle proof timeout")


class MerkleTree:
    """
    Poseidon-based Merkle Tree for ZK circuits.
    
    Uses circomlibjs Poseidon via Node.js to ensure compatibility
    with the Circom circuit implementation.
    """
    
    def __init__(self, leaves, depth=15, use_poseidon=True):
        self.leaves = leaves
        self.depth = depth
        self.tree = []
        self.root = ""
        self.use_poseidon = use_poseidon
        self.build_tree()

    def build_tree(self):
        n = len(self.leaves)
        if n == 0:
            self.root = ""
            return
        
        if self.use_poseidon:
            # Use Poseidon via Node.js
            try:
                result = PoseidonHasher.build_merkle_tree(self.leaves, self.depth)
                self.root = result["root"]
                print(f"[Poseidon] Merkle root: {self.root[:20]}...")
            except Exception as e:
                print(f"[Warning] Poseidon failed, falling back to SHA256: {e}")
                self._build_sha256_tree()
        else:
            self._build_sha256_tree()
    
    def _build_sha256_tree(self):
        """Fallback SHA256 tree (for compatibility only)"""
        n = len(self.leaves)
        next_pow_2 = 2 ** math.ceil(math.log2(max(n, 1)))
        zero_hash = self.hash_node("")
        padding = [zero_hash] * (next_pow_2 - n)
        current_level = self.leaves + padding

        self.tree = [current_level]

        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i+1]
                combined = self.hash_node(left + right)
                next_level.append(combined)
            self.tree.append(next_level)
            current_level = next_level
        
        self.root = current_level[0] if current_level else ""

    @staticmethod
    def hash_node(data: str) -> str:
        return hashlib.sha256(data.encode()).hexdigest()


class VoterRegistry:
    """
    Privacy-Preserving Voter Registry with Poseidon Hashing
    
    Flow:
    1. EC loads (voterID, secret) pairs from registry
    2. EC computes commitment = Poseidon(secret, voterID) for each voter
    3. EC shuffles commitments using cryptographic randomness
    4. EC builds Merkle tree from SHUFFLED commitments (Poseidon)
    5. EC publishes: shuffled leaves, merkle root
    6. EC DELETES: original mapping (leaf->voter) - this is the trust assumption
    
    Voter verification:
    1. Voter knows their voterID and secret (citizenship number)
    2. Voter computes Poseidon(secret, voterID)
    3. Voter requests Merkle proof from server (O(log n))
    4. Voter builds ZK proof using the Merkle proof
    5. Server verifies ZK proof - no identity revealed!
    """
    
    # For demo: simulated secrets. In production, these would be citizenship numbers
    DEMO_SECRET_PREFIX = "CITIZENSHIP_"  # Simulates citizenship number
    
    def __init__(self, csv_path, use_poseidon=True):
        self.leaves = []           # Shuffled commitments (published)
        self.merkle_tree = None
        self.voter_count = 0
        self.shuffle_seed = None   # Published for auditability
        self.use_poseidon = use_poseidon
        self.depth = 15            # Supports 2^15 = 32,768 voters
        
        # For demo only: store secrets so users can look them up
        self._demo_secrets = {}    # voterID -> secret (DELETED IN PRODUCTION)
        self._commitment_map = {}  # commitment -> original index (for proof generation)
        
        if os.path.exists(csv_path):
            self.load_and_build(csv_path)
        else:
            print(f"Warning: CSV file not found at {csv_path}")
            self.merkle_tree = MerkleTree([], use_poseidon=self.use_poseidon)

    def load_and_build(self, path):
        """
        Simulates Election Commission building the tree:
        1. Load voter data
        2. Generate Poseidon commitments with secrets
        3. Shuffle (breaks position->voter link)
        4. Build tree
        """
        print(f"[EC] Loading voter registry from {path}...")
        print(f"[EC] Using {'Poseidon' if self.use_poseidon else 'SHA256'} hashing")
        
        commitments = []
        voter_data = []
        
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            
            for row in reader:
                if count >= 1048:  # Limit for demo performance
                    break
                
                voter_id = row.get('मतदाता नं', '').strip()
                if not voter_id:
                    continue
                
                secret = self._generate_demo_secret(voter_id, row)
                voter_data.append({"voterId": voter_id, "secret": secret})
                self._demo_secrets[voter_id] = secret
                count += 1
        
        if self.use_poseidon:
            # Generate Poseidon voter leaves in batch for efficiency
            # This matches the circuit: voterIdHash = Poseidon(voterId)
            print(f"[EC] Generating {len(voter_data)} Poseidon voter leaves (batch)...")
            try:
                voter_ids = [vd["voterId"] for vd in voter_data]
                commitments = PoseidonHasher.batch_hash_voter_leaves(voter_ids)
                print(f"[EC] Batch Poseidon hashing complete")
            except Exception as e:
                print(f"[Warning] Batch Poseidon failed, using SHA256: {e}")
                for vd in voter_data:
                    commitment = MerkleTree.hash_node(vd["voterId"])
                    commitments.append(commitment)
        else:
            # Fallback to SHA256
            for vd in voter_data:
                commitment = MerkleTree.hash_node(vd["voterId"])
                commitments.append(commitment)
        
        self.voter_count = len(commitments)
        print(f"[EC] Generated {self.voter_count} voter commitments")
        
        # CRITICAL: Cryptographic shuffle breaks the position->voter mapping
        # Even EC cannot know which leaf belongs to which voter after this
        self.shuffle_seed = secrets.token_hex(32)  # Published for auditability
        print(f"[EC] Shuffle seed: {self.shuffle_seed[:16]}...")
        
        # Deterministic shuffle using the seed (reproducible but unpredictable)
        random.seed(self.shuffle_seed)
        random.shuffle(commitments)
        
        self.leaves = commitments
        print(f"[EC] Shuffled commitments - position mapping destroyed")
        
        # Build commitment -> shuffled index map for proof generation
        for idx, comm in enumerate(self.leaves):
            self._commitment_map[comm] = idx
        
        # Build Merkle tree from shuffled leaves
        self.merkle_tree = MerkleTree(self.leaves, depth=self.depth, use_poseidon=self.use_poseidon)
        print(f"[EC] Merkle tree built. Root: {self.merkle_tree.root[:16]}...")
        
        # In production: EC would now DELETE self._demo_secrets and any other mapping
        # print("[EC] Deleting voter->commitment mapping...")
        # self._demo_secrets = {}  # Uncomment in production
        
    def _generate_demo_secret(self, voter_id: str, row: dict) -> str:
        """
        Demo only: Generate a predictable secret for testing.
        
        In production: 
        - This would be the voter's real citizenship number
        - EC has this from voter registration database
        - EC MUST delete the mapping after tree construction
        """
        # For demo: use "CITIZENSHIP_" + some derivation
        # Users can use this pattern to test, or we provide lookup
        return f"{self.DEMO_SECRET_PREFIX}{voter_id}"
    
    def get_demo_secret(self, voter_id: str) -> str:
        """Demo only: Allow users to look up their test secret"""
        return self._demo_secrets.get(voter_id)
    
    def compute_voter_leaf(self, voter_id: str) -> str:
        """
        Compute the voter leaf hash: Poseidon(voterId)
        
        This matches the circuit and is what's stored in the Merkle tree.
        Secret is NOT part of the leaf - it's only used for nullifier.
        """
        if self.use_poseidon:
            try:
                result = PoseidonHasher.hash_voter_leaf(voter_id)
                return result["leaf"]
            except Exception:
                pass
        return MerkleTree.hash_node(voter_id)
    
    def compute_commitment(self, secret: str, voter_id: str) -> str:
        """
        Compute the commitment: Poseidon(secret, voterId)
        
        NOTE: This is NOT stored in the tree. For tree lookup, use compute_voter_leaf().
        This method is for reference/binding purposes only.
        """
        if self.use_poseidon:
            try:
                result = PoseidonHasher.hash_commitment(secret, voter_id)
                return result["commitment"]
            except Exception:
                pass
        return MerkleTree.hash_node(secret + voter_id)
    
    def find_leaf_index(self, commitment: str) -> int:
        """Find the index of a commitment in the shuffled leaves"""
        return self._commitment_map.get(commitment, -1)
    
    def get_merkle_proof(self, commitment: str) -> dict:
        """
        Generate Merkle proof for a commitment (SCALABLE).
        
        This is the key scalability fix - instead of downloading all leaves,
        the client just needs to request a proof for their commitment.
        Returns O(log n) path elements instead of O(n) leaves.
        """
        leaf_index = self.find_leaf_index(commitment)
        if leaf_index == -1:
            return None
        
        if self.use_poseidon:
            try:
                return PoseidonHasher.get_merkle_proof(
                    leaf_index, 
                    self.leaves, 
                    self.depth
                )
            except Exception as e:
                print(f"[Warning] Poseidon proof generation failed: {e}")
        
        # Fallback to SHA256-based proof
        return self._get_sha256_proof(leaf_index)
    
    def _get_sha256_proof(self, leaf_index: int) -> dict:
        """Generate SHA256 Merkle proof (fallback)"""
        path_elements = []
        path_indices = []
        
        if not self.merkle_tree.tree:
            return None
        
        idx = leaf_index
        for level in self.merkle_tree.tree[:-1]:
            is_right = idx % 2 == 1
            sibling_idx = idx - 1 if is_right else idx + 1
            
            if sibling_idx < len(level):
                path_elements.append(level[sibling_idx])
            else:
                path_elements.append("0" * 64)
            
            path_indices.append(1 if is_right else 0)
            idx = idx // 2
        
        # Pad to required depth
        while len(path_elements) < self.depth:
            path_elements.append("0" * 64)
            path_indices.append(0)
        
        return {
            "leaf": self.leaves[leaf_index],
            "leafIndex": leaf_index,
            "pathElements": path_elements,
            "pathIndices": path_indices,
            "root": self.merkle_tree.root
        }


# Initialize registry
CSV_PATH = os.environ.get(
    'VOTER_CSV_PATH', 
    '/app/data/dhulikhel_voter_list_full.csv'
)

# Use Poseidon hashing for ZK circuit compatibility
# Set to 'false' to fallback to SHA256 (faster but incompatible with circuit)
USE_POSEIDON = os.environ.get('USE_POSEIDON', 'true').lower() != 'false'

if not os.path.exists(CSV_PATH):
    # Try relative to backend directory
    backend_dir = os.path.dirname(os.path.dirname(__file__))
    local_path = os.path.join(backend_dir, "data", "dhulikhel_voter_list_full.csv")
    
    # Try relative to project root (one level up from backend)
    if not os.path.exists(local_path):
        project_root = os.path.dirname(backend_dir)
        local_path = os.path.join(project_root, "data", "dhulikhel_voter_list_full.csv")
    
    if os.path.exists(local_path):
        CSV_PATH = local_path

print(f"[Registry] Poseidon hashing: {'enabled' if USE_POSEIDON else 'disabled (SHA256)'}")
registry = VoterRegistry(CSV_PATH, use_poseidon=USE_POSEIDON)
