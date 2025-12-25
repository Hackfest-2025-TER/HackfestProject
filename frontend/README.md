# PromiseThread Frontend

**SvelteKit-based web application with client-side ZK proof generation.**

## Technology Stack

- **Framework:** SvelteKit 2.0 (SSR + SPA hybrid)
- **Language:** TypeScript 5.0
- **Styling:** Tailwind CSS 3.4
- **ZK Libraries:** snarkjs 0.7.5, circomlibjs 0.1.7
- **Blockchain:** ethers.js 5.7.2
- **Build Tool:** Vite 5.0

## Installation

```bash
cd frontend

# Install dependencies
npm install
# or
pnpm install

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

# Preview production build
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── routes/                      # SvelteKit pages
│   │   ├── +layout.svelte           # Global layout
│   │   ├── +page.svelte             # Landing page
│   │   ├── auth/+page.svelte        # ZK authentication
│   │   ├── manifestos/
│   │   │   ├── +page.svelte         # List view
│   │   │   └── [id]/+page.svelte    # Detail view
│   │   ├── citizen/
│   │   │   └── attestation/+page.svelte  # Voting
│   │   ├── politician/
│   │   │   ├── dashboard/+page.svelte
│   │   │   └── wallet/+page.svelte
│   │   └── verify/+page.svelte      # Vote verification
│   │
│   ├── lib/
│   │   ├── api.ts                   # Backend API client
│   │   ├── stores.ts                # Svelte stores
│   │   ├── components/              # Reusable components
│   │   │   ├── Header.svelte
│   │   │   ├── VoteBox.svelte
│   │   │   ├── CommentThread.svelte
│   │   │   └── BlockchainVisualizer.svelte
│   │   └── utils/
│   │       ├── zkProof.ts           # ZK proof generation
│   │       └── crypto.ts            # Cryptographic utils
│   │
│   ├── app.html                     # HTML template
│   └── app.css                      # Global styles
│
├── static/
│   └── zk/                          # ZK artifacts (WASM, keys)
│       ├── citizen_credential.wasm
│       ├── circuit_final.zkey
│       └── verification_key.json
│
├── svelte.config.js
├── vite.config.js
├── tailwind.config.js
└── package.json
```

## Key Routes

### Public Routes

**`/` - Landing Page**
- Platform overview
- Feature highlights
- Call-to-action for authentication

**`/auth` - Authentication**
- Voter ID lookup
- ZK proof generation
- Anonymous credential issuance

**`/manifestos` - Browse Promises**
- Filter by status (pending/kept/broken)
- Filter by category
- Filter by politician
- Sort by votes, date, etc.

**`/manifestos/[id]` - Promise Detail**
- Full manifesto text
- Vote aggregates with visualization
- Discussion thread (threaded comments)
- Evidence links
- Grace period countdown (if applicable)

**`/politicians` - Politician Directory**
- List all politicians with track records
- Filter by party, position

**`/politicians/[id]` - Politician Profile**
- Bio and contact
- All promises made
- Fulfillment statistics

### Authenticated Routes (Require ZK Credential)

**`/citizen/attestation` - Voting**
- Select manifesto to vote on
- Cast vote (kept/broken)
- Add evidence URL
- View voting history

**`/verify` - Vote Verification**
- Enter vote hash
- View Merkle proof
- Verify inclusion in batch

### Politician Routes

**`/politician/dashboard` - Dashboard**
- View all your promises
- See vote statistics
- Respond to comments

**`/politician/new-manifesto` - Create Promise**
- Title, description, category
- Set grace period
- Sign with digital wallet

**`/politician/wallet` - Digital Signature Wallet**
- Generate Ethereum wallet
- Download encrypted keystore
- Sign manifestos

## Component Library

### VoteBox
Vote aggregation display with progress bars.

```svelte
<VoteBox
  voteKept={45}
  voteBroken={12}
  status="pending"
  gracePeriodEnd={new Date('2025-06-01')}
/>
```

### CommentThread
Threaded discussion with upvote/downvote.

```svelte
<CommentThread
  manifestoId={1}
  comments={commentsData}
  userNullifier={$authStore.credential?.nullifier}
/>
```

### BlockchainVisualizer
Visual representation of blockchain with linked blocks.

```svelte
<BlockchainVisualizer blocks={blockData} />
```

### ManifestoCard
Card component for manifesto list view.

```svelte
<ManifestoCard
  manifesto={data}
  onClick={() => goto(`/manifestos/${data.id}`)}
/>
```

## State Management

### Auth Store (`stores.ts`)

```typescript
interface AuthState {
  isAuthenticated: boolean;
  nullifier: string | null;
  credential: Credential | null;
  isLoading?: boolean;
  error?: string | null;
}

// Usage
import { authStore } from '$lib/stores';

authStore.setCredential(credential);
authStore.markVoted(manifestoId);
authStore.logout();
```

**Storage:** Uses `localStorage` for persistence (consider `sessionStorage` for production).

## API Integration

### API Client (`api.ts`)

All backend communication goes through `api.ts`:

```typescript
import { getManifestos, submitVote, verifyZKProof } from '$lib/api';

// Fetch manifestos
const manifestos = await getManifestos({ status: 'pending' });

// Submit vote
const result = await submitVote({
  manifesto_id: 1,
  vote_type: 'kept',
  nullifier: credential.nullifier
});

// Verify ZK proof
const verification = await verifyZKProof(proof);
```

**Base URL:** Set via `VITE_API_URL` environment variable.

## ZK Proof Generation

### Client-Side Proof Flow

```typescript
import { authenticate } from '$lib/zk/zkAuth';

// 1. User enters voterId + secret
// 2. System fetches Merkle proof and generates ZK proof
const result = await authenticate(voterId, secret);

// 3. Result contains:
{
  success: true,
  credential: "...",
  nullifier: "0x...",
  message: "Authenticated successfully"
}

// 4. Store credential locally
authStore.setCredential(result.credential);
```

### Nullifier Generation

Nullifier is generated inside the ZK circuit:
`Nullifier = Poseidon(voterId, secret)`

**Properties:**
- Deterministic (same inputs = same output)
- Anonymous (reveals nothing about voterId)
- Unique per voter (prevents double-voting)

**Note:** Uses `snarkjs` with WASM circuits for real client-side proof generation.

## Styling

### Tailwind Configuration

```javascript
// tailwind.config.js
export default {
  theme: {
    extend: {
      colors: {
        primary: '#3B82F6',
        secondary: '#10B981',
        accent: '#F59E0B',
      }
    }
  }
}
```

### CSS Variables

```css
/* app.css */
:root {
  --color-bg: #ffffff;
  --color-text: #1f2937;
  --color-border: #e5e7eb;
}

@media (prefers-color-scheme: dark) {
  :root {
    --color-bg: #1f2937;
    --color-text: #f9fafb;
    --color-border: #374151;
  }
}
```

## Performance Optimization

### Code Splitting
SvelteKit automatically code-splits routes. Heavy ZK libraries are loaded only on auth pages.

### Image Optimization
Use `<img>` with `loading="lazy"` for politician photos and evidence images.

### Merkle Proof Caching
Cache downloaded anonymity set in `sessionStorage`:

```typescript
const cached = sessionStorage.getItem('anonymity_set');
if (cached) {
  anonymitySet = JSON.parse(cached);
} else {
  anonymitySet = await fetch('/api/registry/anonymity-set');
  sessionStorage.setItem('anonymity_set', JSON.stringify(anonymitySet));
}
```

## Testing

```bash
# Run tests (when implemented)
npm test

# Type checking
npm run check

# Lint
npm run lint
```

## Build & Deployment

```bash
# Production build
npm run build

# Output: build/ directory
# - build/client - Static assets
# - build/server - SSR server

# Preview
npm run preview

# Deploy to Node.js server
node build
```

### Environment Variables (Production)

```env
VITE_API_URL=https://api.promisethread.com
VITE_BLOCKCHAIN_RPC=https://polygon-rpc.com
VITE_PROMISE_REGISTRY_ADDRESS=0x...deployed...address
```

## Security Considerations

### Current Limitations

1. **LocalStorage for credentials** - Vulnerable to XSS
   - **Fix:** Use `sessionStorage` + encryption or HTTP-only cookies

2. **No HTTPS enforcement** - MITM attacks possible
   - **Fix:** Always use HTTPS in production

### Production Checklist

- [ ] Switch to `sessionStorage` for credentials
- [ ] Add Content Security Policy headers
- [ ] Enable HTTPS with HSTS
- [ ] Implement rate limiting on voter lookup
- [ ] Clear sensitive data after use

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

**Note:** ZK proof generation requires WebAssembly support.

## Data Flow Example

### Complete Authentication Flow

```typescript
// 1. User visits /auth
// 2. Enters voter ID and secret
const result = await authenticate(voterId, secret);
// Internally:
// - Fetches Merkle proof
// - Generates ZK proof (snarkjs)
// - Verifies with backend

// 3. Store credential
if (result.success) {
  authStore.setCredential({
    nullifier: result.nullifier,
    credential: result.credential,
    usedVotes: result.used_votes
  });
  
  // 4. Redirect to manifestos
  goto('/manifestos');
}
```

### Complete Voting Flow

```typescript
// 1. User authenticated (has credential)
const { nullifier } = $authStore.credential;

// 2. Select manifesto and vote type
const voteData = {
  manifesto_id: manifestoId,
  vote_type: 'kept',
  nullifier: nullifier,
  evidence_url: evidenceInput // optional
};

// 3. Submit vote
const result = await submitVote(voteData);

// 4. Mark as voted locally
authStore.markVoted(manifestoId);

// 5. Show success message with vote_hash
alert(`Vote recorded! Hash: ${result.vote_hash}`);
```

---

For backend API details, see [../backend/README.md](../backend/README.md)
For blockchain contracts, see [../blockchain/README.md](../blockchain/README.md)
