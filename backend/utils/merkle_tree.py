import csv
import hashlib
import math
import os
import random
import secrets

class MerkleTree:
    def __init__(self, leaves):
        self.leaves = leaves
        self.tree = []
        self.root = ""
        self.build_tree()

    def build_tree(self):
        n = len(self.leaves)
        if n == 0:
            self.root = ""
            return

        # Pad to next power of 2
        next_pow_2 = 2 ** math.ceil(math.log2(n))
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
        
        self.root = current_level[0]

    @staticmethod
    def hash_node(data: str) -> str:
        return hashlib.sha256(data.encode()).hexdigest()


class VoterRegistry:
    """
    Privacy-Preserving Voter Registry with Cryptographic Shuffling
    
    Flow:
    1. EC loads (voterID, secret) pairs from registry
    2. EC computes commitment = hash(secret + voterID) for each voter
    3. EC shuffles commitments using cryptographic randomness
    4. EC builds Merkle tree from SHUFFLED commitments
    5. EC publishes: shuffled leaves, merkle root
    6. EC DELETES: original mapping (leaf->voter) - this is the trust assumption
    
    Voter verification:
    1. Voter knows their voterID and secret (citizenship number)
    2. Voter computes hash(secret + voterID)
    3. Voter downloads all shuffled leaves
    4. Voter finds their commitment in the array (position unknown to EC)
    5. Voter builds Merkle proof from that position
    """
    
    # For demo: simulated secrets. In production, these would be citizenship numbers
    # that EC has but deletes the mapping after tree construction
    DEMO_SECRET_PREFIX = "CITIZENSHIP_"  # Simulates citizenship number
    
    def __init__(self, csv_path):
        self.leaves = []           # Shuffled commitments (published)
        self.merkle_tree = None
        self.voter_count = 0
        self.shuffle_seed = None   # Published for auditability, but doesn't reveal mapping
        
        # For demo only: store secrets so users can look them up
        # In production: EC deletes this after tree construction!
        self._demo_secrets = {}    # voterID -> secret (DELETED IN PRODUCTION)
        
        if os.path.exists(csv_path):
            self.load_and_build(csv_path)
        else:
            print(f"Warning: CSV file not found at {csv_path}")
            self.merkle_tree = MerkleTree([])

    def load_and_build(self, path):
        """
        Simulates Election Commission building the tree:
        1. Load voter data
        2. Generate commitments with secrets
        3. Shuffle (breaks position->voter link)
        4. Build tree
        """
        print(f"[EC] Loading voter registry from {path}...")
        
        commitments = []
        
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            
            for row in reader:
                if count >= 1048:  # Limit for browser performance
                    break
                
                voter_id = row.get('मतदाता नं', '').strip()
                if not voter_id:
                    continue
                
                # In production: secret = citizenship_number from EC database
                # For demo: we derive a deterministic secret so users can test
                secret = self._generate_demo_secret(voter_id, row)
                
                # Compute commitment: hash(secret + voterID)
                # This binds the voter to their secret - only correct secret works
                commitment = MerkleTree.hash_node(secret + voter_id)
                commitments.append(commitment)
                
                # Store for demo lookup (DELETED IN PRODUCTION!)
                self._demo_secrets[voter_id] = secret
                
                count += 1
        
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
        
        # Build Merkle tree from shuffled leaves
        self.merkle_tree = MerkleTree(self.leaves)
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
    
    def compute_commitment(self, secret: str, voter_id: str) -> str:
        """Compute the commitment hash that should match a leaf"""
        return MerkleTree.hash_node(secret + voter_id)
    
    def find_leaf_index(self, commitment: str) -> int:
        """Find the index of a commitment in the shuffled leaves"""
        try:
            return self.leaves.index(commitment)
        except ValueError:
            return -1


# Initialize registry
CSV_PATH = os.environ.get(
    'VOTER_CSV_PATH', 
    '/app/data/dhulikhel_voter_list_full.csv'
)

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

registry = VoterRegistry(CSV_PATH)
