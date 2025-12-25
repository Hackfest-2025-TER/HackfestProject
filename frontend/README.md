# PromiseThread Frontend

**SvelteKit-based web application with client-side ZK proof generation.**

## Technology Stack

- **Framework:** SvelteKit 2.0 (SSR + SPA hybrid)
- **Language:** TypeScript 5.0
- **Styling:** Tailwind CSS 3.4
- **ZK Libraries:** snarkjs 0.7.5, circomlibjs 0.1.7
- **Blockchain:** ethers.js 5.7.2
- **Build Tool:** Vite 5.0

## 🔬 Deep Technical Theory: Client-Side Trust

### 1. The Trustless Proving Model
Crucially, ZK proof generation **MUST** happen on the client (browser).
*   **Why?**: If the backend generated the proof, the user would have to send their `secret` to the backend. This requires trusting the backend not to store the secret or impersonate the voter.
*   **Implementation**: We use **WebAssembly (WASM)**.
    *   The `citizen_credential.wasm` file allows the browser to run compiled C++ circuit code at near-native speed.
    *   This enables complex cryptographic operations (Elliptic Curve pairings on BN128) to run locally on the user's device.

### 2. Security Assumptions
*   **The "Toxic Waste" Assumption**: We assume the Trusted Setup for Groth16 was performed correctly (using Hermez Powers of Tau).
*   **The "Discrete Log" Assumption**: The security of the BN128 curve relies on the difficulty of the Discrete Logarithm Problem.
*   **XSS Threat Model**: Since the `secret` is entered in the browser, an XSS (Cross-Site Scripting) attack could steal it.
    *   *Mitigation*: We do not store the secret in `localStorage`. detailed state management ensures it is cleared from memory after proof generation.

## System Distinction: Blockchain vs ZK

It is important to note that **Zero-Knowledge (ZK) proofs are NOT "on the blockchain" in this layer.**
-   **Client-Side Generation:** All ZK proofs are generated strictly in the user's browser using WebAssembly (`.wasm`) circuits.
-   **Privacy:** The user's secret keys never leave their device.
-   **Verification:** The resulting proof is sent to the backend (or blockchain) for verification, but the generation process is entirely off-chain.

## Installation

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cat > .env << EOF
VITE_API_URL=http://localhost:8000
VITE_BLOCKCHAIN_RPC=http://localhost:8545
VITE_PROMISE_REGISTRY_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
EOF

# Start development server
npm run dev

# Build for production
npm run build
```

## Project Structure

```
frontend/
├── src/
│   ├── routes/                      # SvelteKit pages
│   │   ├── +layout.svelte           # Global layout
│   │   ├── +page.svelte             # Landing page
│   │   ├── auth/                    # Authentication (ZK Login)
│   │   ├── manifestos/              # Manifesto listings & details
│   │   ├── citizen/                 # Voter specific actions
│   │   ├── politician/              # Politician dashboard & tools
│   │   └── verify/                  # Public verification tools
│   │
│   ├── lib/
│   │   ├── api.ts                   # Backend API client
│   │   ├── stores.ts                # State management (auth, theme)
│   │   ├── components/              # Reusable UI components
│   │   └── utils/
│   │       ├── zkProof.ts           # Client-side ZK proof generation
│   │       └── crypto.ts            # Wallet & hashing utilities
│   │
│   ├── app.html                     # HTML entry point
│   └── app.css                      # Global styles (Tailwind)
│
├── static/
│   └── zk/                          # ZK artifacts (publicly accessible)
│       ├── citizen_credential.wasm  # Circuit logic
│       └── circuit_final.zkey       # Proving key
```

## Key Components

### ZK Proof Generation (`src/lib/utils/zkProof.ts`)
Handles the complex logic of downloading ZK artifacts, computing Poseidon hashes, and generating Groth16 proofs using `snarkjs` in the browser.

### Authentication Flow
1.  User inputs Voter ID and Secret.
2.  App fetches the Anonymity Set (Merkle Tree leaves) from Backend.
3.  App generates a ZK Proof locally, proving "I know a secret that corresponds to a leaf in this tree" without revealing which leaf.
4.  App sends the Proof + Nullifier to Backend.
5.  Backend verifies proof and issues a session token.

### Blockchain Interaction
Uses `ethers.js` to read data directly from smart contracts for verification purposes (e.g., verifying a specific promise status on-chain).

## Development

### Running with Local Blockchain
Ensure your local Hardhat node is running and the contracts are deployed. Update `VITE_PROMISE_REGISTRY_ADDRESS` in `.env` with the deployment address.

### ZK Artifacts
The `.wasm` and `.zkey` files in `static/zk/` must match the circuits compiled in the `blockchain` directory. If you modify the circuits, re-compile and copy the new artifacts here.

## Build & Deployment

```bash
# Production build
npm run build

# Preview production build
npm run preview
```
