import csv
import hashlib
import math
import os

class MerkleTree:
    def __init__(self, leaves):
        self.leaves = leaves
        self.tree = []
        self.root = ""
        self.build_tree()

    def build_tree(self):
        # 1. Pad leaves to next power of 2 for a balanced tree
        n = len(self.leaves)
        if n == 0:
            self.root = ""
            return

        next_pow_2 = 2 ** math.ceil(math.log2(n))
        # Pad with zero-hash or empty string hash
        # Using a consistent zero value for padding
        zero_hash = self.hash_node("0")
        padding = [zero_hash] * (next_pow_2 - n)
        current_level = self.leaves + padding

        self.tree = [current_level]

        # 2. Build up
        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i+1]
                # Concatenate and hash
                combined = self.hash_node(left + right)
                next_level.append(combined)
            self.tree.append(next_level)
            current_level = next_level
        
        self.root = current_level[0]

    @staticmethod
    def hash_node(data: str) -> str:
        # Using SHA256. In production ZK, you'd use Poseidon/MiMC.
        return hashlib.sha256(data.encode()).hexdigest()

# Singleton Loader
class VoterRegistry:
    def __init__(self, csv_path):
        self.leaves = []
        self.merkle_tree = None
        if os.path.exists(csv_path):
            self.load_csv(csv_path)
            self.merkle_tree = MerkleTree(self.leaves)
        else:
            print(f"Warning: CSV file not found at {csv_path}")
            self.merkle_tree = MerkleTree([])

    def load_csv(self, path):
        print(f"Loading registry from {path}...")
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            # LIMIT TO 1048 LEAVES
            for row in reader:
                if count >= 1048: 
                    break
                
                # 'मतदाता नं' is the unique Voter ID
                voter_id = row['मतदाता नं']
                if voter_id:
                    # Hash the ID to create the leaf
                    leaf = MerkleTree.hash_node(voter_id)
                    self.leaves.append(leaf)
                    count += 1
        print(f"Loaded {len(self.leaves)} voters into anonymity set.")

# Initialize
# In Docker, the data folder is mounted to /app/data
# Locally, we look relative to the backend folder
CSV_PATH = os.environ.get(
    'VOTER_CSV_PATH', 
    '/app/data/dhulikhel_voter_list_full.csv'  # Docker path
)

# Fallback for local development
if not os.path.exists(CSV_PATH):
    local_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "dhulikhel_voter_list_full.csv")
    if os.path.exists(local_path):
        CSV_PATH = local_path

registry = VoterRegistry(CSV_PATH)
