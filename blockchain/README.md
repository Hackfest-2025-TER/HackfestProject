# PromiseThread Blockchain

**Smart contracts and ZK circuits for on-chain vote aggregation, politician accountability, and anonymous verification.**

## System Architecture

The PromiseThread architecture separates concerns between the Blockchain (public ledger), the Off-chain Database (storage), and the ZK Proof System (privacy).

**Note on ZK & Blockchain Distinction:**
Zero-Knowledge (ZK) proofs are generated **client-side** (in the user's browser) and verified off-chain or on-chain. The ZK circuits themselves are **not** stored on the blockchain. The blockchain only acts as a verifier (or settler) that accepts a valid proof to prevent double-voting.

### 1. Identity & Commitments (`ManifestoRegistry.sol`)
Serves as the immutable source of truth for politician identities and their campaign promises (manifestos).
- **Politician Registration**: Politicians register their wallets, establishing a verifiable on-chain identity.
- **Manifesto Commitments**: Politicians submit SHA256 hashes of their detailed manifestos. The full text is stored off-chain (backend), but the on-chain hash guarantees the content hasn't been tampered with.
- **Verification**: Any user can hash the off-chain manifesto text and compare it with the on-chain commitment to verify authenticity.

### 2. Accountability & Voting (`PromiseRegistry.sol`)
Tracks specific promises made by politicians and the community's verdict on whether they were kept.
- **Promise Lifecycle**:
  1. **Registration**: A specific promise (derived from a manifesto) is registered with a `gracePeriod`.
  2. **Grace Period**: A lock-up period where no voting can occur, giving the politician time to fulfill the promise.
  3. **Voting/Aggregation**: After the grace period, community votes are aggregated and submitted.
  4. **Finalization**: Based on the vote ratio (60% threshold), the promise is marked as `Kept`, `Broken`, or `Disputed`.
- **Vote Aggregation**: To save gas, individual votes are not stored on-chain. Instead, votes are batched, and only the aggregates (kept/broken counts) and a **Merkle Root** of the batch are submitted.

### 3. Privacy & Anonymity (`ZKVerifier.sol` & Circuits)
Ensures that voters can prove they are eligible citizens without revealing their specific identity.
- **ZK-SNARKs (Groth16)**: We use Circom circuits to generate Zero-Knowledge proofs.
- **Credential Issuance**: A voter proves they exist in the authorized Merkle Tree of citizens.
- **Nullifiers**: To prevent double-voting, every valid proof generates a deterministic "nullifier" hash. If a user tries to vote again, the contract detects the duplicate nullifier and rejects the transaction.

## Technology Stack

- **Framework:** Hardhat 2.19.0
- **Language:** Solidity 0.8.19
- **ZK Circuits:** Circom 2.0.0
- **ZK Proof System:** Groth16 (via snarkjs)
- **Networks:** Local (dev), Polygon Mumbai, Avalanche Fuji

## Smart Contracts API

### ManifestoRegistry.sol
*Immutable registry for political manifesto commitments.*

```solidity
function registerPolitician(uint256 politicianId) external
```
Registers the caller's wallet as the official controller for a politician ID.

```solidity
function submitManifesto(uint256 politicianId, bytes32 contentHash) external returns (uint256)
```
Submits a SHA256 hash of a manifesto. Returns the new manifesto index.

```solidity
function verifyManifesto(uint256 politicianId, bytes32 contentHash) external view returns (bool, uint256, uint256)
```
Verifies if a specific hash exists for a politician. Returns validity, timestamp, and block number.

### PromiseRegistry.sol
*Stores promise hashes and vote aggregates.*

```solidity
function registerPromise(bytes32 promiseId, bytes32 promiseHash, uint256 gracePeriodDays) external
```
Registers a new promise. Can only be called by the politician who owns the promise logic (in this simplified version, any address can register, but frontend enforces ownership).

```solidity
function submitVoteAggregate(
    bytes32 promiseId,
    uint256 votesKept,
    uint256 votesBroken,
    bytes32 merkleRoot,
    bytes32[] calldata nullifiers
) external
```
Submits a batch of votes. **Critical:** Checks `nullifiers` against `usedNullifiers` to prevent double-counting.

```solidity
function finalizeStatus(bytes32 promiseId) external
```
Calculates the final status based on aggregated votes. Requires >60% consensus to mark as Kept or Broken.

### ZKVerifier.sol
*Verifies zero-knowledge proofs for anonymous voting.*

```solidity
function issueCredential(
    bytes32 nullifierHash,
    uint256[8] calldata proof,
    uint256[] calldata publicInputs
) external returns (bytes32 credentialHash)
```
Verifies a specific zk-SNARK proof. If valid and the nullifier is unused, issues a credential hash and marks the nullifier as used.

## ZK Circuit Details (`citizen_credential.circom`)

The circuit proves membership in a Merkle tree of eligible voters.

**Inputs:**
- `voterId` (Private): The user's unique ID.
- `voterSecret` (Private): A secret key known only to the user.
- `pathElements` & `pathIndices` (Private): Merkle proof path.
- `merkleRoot` (Public): The root of the valid voter tree.

**Outputs:**
- `nullifier`: Hash(voterId, voterSecret) - Unique per user per context, deterministic but anonymous.
- `commitment`: Hash(leaf, nullifier) - Bounds the proof to this specific operation.

## Installation & Setup

```bash
cd blockchain

# Install dependencies
npm install

# Compile contracts
npx hardhat compile

# Run tests
npx hardhat test

# Compile ZK Circuits (Requires Circom)
npm run circuit:compile
npm run circuit:setup
```

## Deployment

### Local Network
```bash
# Terminal 1
npx hardhat node

# Terminal 2
npx hardhat run scripts/deploy.js --network localhost
```

### Testnets (Mumbai / Fuji)
Create a `.env` file with `MUMBAI_RPC_URL` (or `FUJI_RPC_URL`) and `PRIVATE_KEY`.

```bash
npx hardhat run scripts/deploy.js --network mumbai
# or
npx hardhat run scripts/deploy.js --network fuji
```
