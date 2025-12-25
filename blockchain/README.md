# PromiseThread Blockchain

**Smart contracts and ZK circuits for on-chain vote aggregation and verification.**

## Technology Stack

- **Framework:** Hardhat 2.19.0
- **Language:** Solidity 0.8.19
- **ZK Circuits:** Circom 2.0.0
- **ZK Proof System:** Groth16 (snarkjs)
- **Networks:** Local (dev), Polygon Mumbai, Avalanche Fuji

## Installation

```bash
cd blockchain

# Install dependencies
npm install
# or
pnpm install

# Compile contracts
npx hardhat compile

# Run tests
npx hardhat test

# Start local node
npx hardhat node

# Deploy to localhost (in another terminal)
npx hardhat run scripts/deploy.js --network localhost
```

## Smart Contracts

### PromiseRegistry.sol

Stores vote aggregates and Merkle roots on-chain.

**Key Functions:**

```solidity
function createPromise(
    uint256 promiseId,
    bytes32 promiseHash,
    uint256 gracePeriodEnd
) external
```
Create a new promise record.

```solidity
function updateVotes(
    uint256 promiseId,
    uint256 kept,
    uint256 broken
) external
```
Update vote aggregates (only after grace period).

```solidity
function storeMerkleRoot(
    uint256 batchId,
    bytes32 root
) external
```
Store Merkle root for a batch of votes.

**Events:**
- `PromiseCreated(uint256 indexed promiseId, bytes32 promiseHash)`
- `VotesUpdated(uint256 indexed promiseId, uint256 kept, uint256 broken)`
- `MerkleRootStored(uint256 indexed batchId, bytes32 root)`

### ManifestoRegistry.sol

Extended registry with politician signature verification.

**Key Functions:**

```solidity
function submitManifesto(
    uint256 manifestoId,
    bytes32 contentHash,
    bytes memory signature
) external
```
Submit manifesto signed by politician's wallet.

```solidity
function verifySignature(
    uint256 manifestoId,
    address expectedSigner
) external view returns (bool)
```
Verify politician signed the manifesto.

### ZKVerifier.sol

Nullifier tracking and zk-SNARK verification.

**Key Functions:**

```solidity
function setMerkleRoot(bytes32 _root) external
```
Update the voter registry Merkle root.

```solidity
function verifyAndRegister(
    bytes32 nullifier,
    bytes32 commitment,
    uint[8] calldata proof
) external returns (bool)
```
Verify zk-SNARK proof and register nullifier (prevent double-voting).

**Note:** On-chain verification is simplified in this version; full Groth16 verification is performed off-chain.

## ZK Circuits

### citizen_credential.circom

Proves voter membership without revealing identity.

**Circuit Logic:**

```circom
template VoterCredential(levels) {
    // Private inputs (not revealed)
    signal input voterId;
    signal input voterSecret;
    signal input pathElements[levels];
    signal input pathIndices[levels];
    
    // Public inputs
    signal input merkleRoot;
    
    // Outputs
    signal output nullifier;
    signal output voterIdHash;
    signal output commitment;
    
    // Constraint 1: Hash voter ID to get leaf
    component voterHasher = Poseidon(1);
    voterHasher.inputs[0] <== voterId;
    voterIdHash <== voterHasher.out;
    
    // Constraint 2: Verify Merkle membership
    component merkleProof = MerkleProof(levels);
    merkleProof.leaf <== voterIdHash;
    // ... verify path ...
    merkleRoot === merkleProof.root;  // ENFORCED
    
    // Constraint 3: Generate nullifier
    component nullifierHasher = Poseidon(2);
    nullifierHasher.inputs[0] <== voterId;
    nullifierHasher.inputs[1] <== voterSecret;
    nullifier <== nullifierHasher.out;
    
    // Constraint 4: Commitment binding
    component commitHasher = Poseidon(2);
    commitHasher.inputs[0] <== voterIdHash;
    commitHasher.inputs[1] <== nullifier;
    commitment <== commitHasher.out;
}

component main {public [merkleRoot]} = VoterCredential(15);
```

**Parameters:**
- **levels:** 15 (supports 32,768 voters)
- **Demo:** 11 levels for 1,048 voters
- **Hash:** Poseidon (zk-SNARK optimized)
- **Proof system:** Groth16

### Circuit Compilation

**Prerequisites:**
- Circom 2.0+
- snarkjs 0.7+
- Powers of Tau ceremony file

**Steps:**

```bash
# 1. Compile circuit
circom circuits/citizen_credential.circom \
    --r1cs --wasm --sym \
    -o build/circuits

# 2. Download Powers of Tau (15th power = 32K constraints)
wget https://hermez.s3-eu-west-1.amazonaws.com/powersOfTau28_hez_final_15.ptau

# 3. Generate proving key (takes 5-10 minutes)
snarkjs groth16 setup \
    build/circuits/citizen_credential.r1cs \
    powersOfTau28_hez_final_15.ptau \
    build/circuits/circuit_final.zkey

# 4. Export verification key
snarkjs zkey export verificationkey \
    build/circuits/circuit_final.zkey \
    build/circuits/verification_key.json

# 5. Copy to frontend
cp build/circuits/citizen_credential_js/citizen_credential.wasm \
   ../frontend/static/zk/
cp build/circuits/circuit_final.zkey \
   ../frontend/static/zk/
cp build/circuits/verification_key.json \
   ../frontend/static/zk/
```

**Output files:**
- `citizen_credential.wasm` - Circuit compiled to WASM (~45 KB)
- `circuit_final.zkey` - Proving key (~1.2 MB)
- `verification_key.json` - Verification key (~2 KB)

### Proof Generation (Client-Side)

```javascript
import { groth16 } from 'snarkjs';

// Prepare inputs
const input = {
  voterId: BigInt(voterIdNumber),
  voterSecret: BigInt(secretNumber),
  pathElements: merklePath.map(p => BigInt(p.hash)),
  pathIndices: merklePath.map(p => p.position === 'left' ? 0 : 1),
  merkleRoot: BigInt(merkleRootHex)
};

// Generate proof
const { proof, publicSignals } = await groth16.fullProve(
  input,
  '/zk/citizen_credential.wasm',
  '/zk/circuit_final.zkey'
);

// publicSignals[0] = merkleRoot
// publicSignals[1] = nullifier
// publicSignals[2] = voterIdHash
// publicSignals[3] = commitment
```

### Proof Verification (Server-Side)

```javascript
const snarkjs = require('snarkjs');
const fs = require('fs');

const vKey = JSON.parse(fs.readFileSync('verification_key.json'));

const isValid = await snarkjs.groth16.verify(
  vKey,
  publicSignals,
  proof
);

if (isValid) {
  console.log('Proof verified');
} else {
  console.log('Invalid proof');
}
```

## Deployment

### Local Network

```bash
# Terminal 1: Start node
npx hardhat node

# Terminal 2: Deploy
npx hardhat run scripts/deploy.js --network localhost

# Output:
# PromiseRegistry: 0x5FbDB2315678afecb367f032d93F642f64180aa3
# ManifestoRegistry: 0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512
# ZKVerifier: 0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0
```

### Polygon Mumbai (Testnet)

```bash
# Set environment variables
export MUMBAI_RPC_URL="https://rpc-mumbai.maticvigil.com"
export DEPLOYER_PRIVATE_KEY="0x..."

# Deploy
npx hardhat run scripts/deploy.js --network mumbai

# Verify on PolygonScan
npx hardhat verify --network mumbai <CONTRACT_ADDRESS> <CONSTRUCTOR_ARGS>
```

### Avalanche Fuji (Testnet)

```bash
export FUJI_RPC_URL="https://api.avax-test.network/ext/bc/C/rpc"
export DEPLOYER_PRIVATE_KEY="0x..."

npx hardhat run scripts/deploy.js --network fuji
```

### Network Configuration

```javascript
// hardhat.config.js
module.exports = {
  solidity: "0.8.19",
  networks: {
    localhost: {
      url: "http://127.0.0.1:8545",
      chainId: 31337
    },
    mumbai: {
      url: process.env.MUMBAI_RPC_URL,
      accounts: [process.env.DEPLOYER_PRIVATE_KEY],
      chainId: 80001,
      gasPrice: 20000000000 // 20 gwei
    },
    fuji: {
      url: process.env.FUJI_RPC_URL,
      accounts: [process.env.DEPLOYER_PRIVATE_KEY],
      chainId: 43113
    }
  }
};
```

## Testing

```bash
# Run all tests
npx hardhat test

# Run specific test
npx hardhat test test/PromiseRegistry.test.js

# Run with gas reporter
REPORT_GAS=true npx hardhat test

# Run with coverage
npx hardhat coverage
```

### Test Examples

```javascript
describe("PromiseRegistry", function () {
  it("Should create a new promise", async function () {
    const promiseHash = ethers.utils.id("Build bridge");
    const gracePeriod = Math.floor(Date.now() / 1000) + 86400 * 180;
    
    await registry.createPromise(1, promiseHash, gracePeriod);
    
    const promise = await registry.promises(1);
    expect(promise.promiseHash).to.equal(promiseHash);
    expect(promise.voteKept).to.equal(0);
  });
  
  it("Should update votes after grace period", async function () {
    // ... create promise ...
    // ... fast forward time ...
    await ethers.provider.send("evm_increaseTime", [86400 * 181]);
    
    await registry.updateVotes(1, 45, 12);
    
    const promise = await registry.promises(1);
    expect(promise.voteKept).to.equal(45);
    expect(promise.voteBroken).to.equal(12);
  });
});
```

## Gas Optimization

**Estimated Gas Costs (Polygon Mumbai):**

| Operation | Gas Used | Cost @ 30 gwei |
|-----------|----------|----------------|
| createPromise | ~120,000 | $0.004 |
| updateVotes | ~60,000 | $0.002 |
| storeMerkleRoot | ~45,000 | $0.0015 |

**Optimization Techniques:**
- Use `uint256` instead of smaller types (less packing overhead)
- Emit events instead of storing rarely-accessed data
- Batch operations when possible
- Store only aggregates, not individual votes

## Security Audit Checklist

- [ ] **Reentrancy protection** - Not needed (no external calls with state changes)
- [ ] **Integer overflow** - Solidity 0.8+ has built-in checks
- [ ] **Access control** - Add `onlyOwner` modifiers for admin functions
- [ ] **Grace period enforcement** - Implemented in `updateVotes`
- [ ] **Nullifier uniqueness** - Mapping prevents reuse
- [ ] **zk-SNARK verification** - On-chain verification (currently off-chain)
- [ ] **Front-running protection** - Consider commit-reveal for sensitive ops

## Production Deployment

### Mainnet Deployment Steps

1. **Audit smart contracts** - Third-party security audit
2. **Test on testnets** - Mumbai, Fuji, Sepolia
3. **Set up multisig** - Use Gnosis Safe for admin functions
4. **Deploy to mainnet** - Polygon or Avalanche C-Chain
5. **Verify contracts** - On block explorers
6. **Configure backend** - Update RPC URLs and contract addresses
7. **Monitor with alerts** - Set up event monitoring

### Mainnet Networks

**Polygon Mainnet:**
```bash
export POLYGON_RPC_URL="https://polygon-rpc.com"
export DEPLOYER_PRIVATE_KEY="0x..."

npx hardhat run scripts/deploy.js --network polygon
```

**Avalanche C-Chain:**
```bash
export AVALANCHE_RPC_URL="https://api.avax.network/ext/bc/C/rpc"
npx hardhat run scripts/deploy.js --network avalanche
```

---

For backend integration, see [../backend/README.md](../backend/README.md)
For frontend integration, see [../frontend/README.md](../frontend/README.md)
