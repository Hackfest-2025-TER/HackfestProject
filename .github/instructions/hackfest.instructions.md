---
applyTo: '**'
---
# PromiseThread - Decentralized Political Accountability Platform

## Vision

A transparent platform where citizens anonymously track and evaluate political promises through community discussion and voting. Built with Svelte, zero-knowledge proofs, and blockchain.

## Core Innovation: Privacy Meets Transparency

**The Problem:** How do you have transparent, tamper-proof political accountability while protecting citizen privacy?

**The Solution:** Zero-Knowledge Proofs + Hybrid Storage Architecture

### Zero-Knowledge Proof Authentication

- Citizens prove voting eligibility WITHOUT revealing identity
- Generate anonymous credential proving "I am a citizen" not "I am John Doe"
- One credential = one vote per promise (prevents Sybil attacks)
- No personal data stored anywhere
- Use SnarkJS/Circom for implementation

### Hybrid Storage Architecture

**ON-CHAIN (Immutable):**

- Promise hash + metadata
- Vote AGGREGATES only (Kept: 60%, Broken: 25%)
- Status changes with timestamps
- Merkle root of all votes

**OFF-CHAIN (Database):**

- Full promise text
- Individual vote records (linked to anonymous credentials)
- Discussion threads and comments
- Evidence links and upvotes

**Why This Works:** ZKP prevents double voting → no need for individual votes on-chain. Blockchain makes final results tamper-proof. Database handles scale efficiently.

## Key Features

**Promise Lifecycle:**

1. Politicians post promises (title, description, category, deadline)
2. Grace period (6-12 months) before evaluation opens
3. Community discussion with evidence links
4. Time-locked voting until grace period ends
5. Anonymous voting via ZKP credentials
6. Consensus threshold (60%) determines status
7. Final results immutably recorded on blockchain

**Discussion System:**

- Reddit-style threaded comments
- Anonymous posting via ZKP
- Upvote/downvote for quality content
- Evidence shared as URLs only (no uploads)
- All discussions public and permanent

**Blockchain Visualization:** Show how blocks are cryptographically linked:

```
Genesis → Promise A → Promise B → Promise C
   ↓          ↓           ↓           ↓
hash: abc  prevHash: abc  prevHash: def  prevHash: ghi
```

## Vote Integrity Flow

1. Generate ZKP proof → Get anonymous credential (e.g., ABC123)
2. Vote on promise → Stored in database with credential
3. System checks: Has ABC123 voted on this promise? → Prevent duplicates
4. Batch votes (every 1000) → Create Merkle tree → Store root on-chain
5. Final tally → Aggregate and write to blockchain
6. Users verify their vote counted via Merkle proof

## Tech Stack

- **Frontend:** Svelte + SvelteKit
- **Blockchain:** Hardhat with testnet (Polygon Mumbai, Avalanche Fuji)
- **ZKP:** SnarkJS + Circom
- **Database:** PostgreSQL or SQLite
- **Contracts:** Solidity

## Hackathon MVP

**Must Build:**

- ZKP authentication system (simulated citizen verification)
- Promise list with filters (status, politician, category)
- Promise detail page with discussion threads
- Anonymous commenting and voting
- Time-locked voting UI with countdown
- Vote aggregation (totals on-chain, records in DB)
- Blockchain visualizer showing chain links
- 3-5 sample promises at different stages

**Demo Flow:**

1. Generate ZKP credential anonymously
2. Browse promises (locked vs open for voting)
3. Join discussion with anonymous comment
4. Cast vote on open promise
5. Show vote aggregate updating on blockchain
6. Visualize blockchain immutability

## Design Principles

**Fair Timing:** Grace periods prevent premature judgment. UI clearly shows "Voting opens in X days" for locked promises.

**Privacy-First:** Zero-knowledge means zero data collection. No tracking, no personal info, anonymous credentials only.

**Scalability:** Batch votes into Merkle trees. Store aggregates on-chain, not individual votes. Minimal blockchain writes.

**Transparency:** All discussions public. Vote tallies visible. Status changes auditable. Open-source code.

## Key Differentiators

What makes PromiseThread special:

- **True anonymity through ZKP** - First political platform with cryptographic privacy
- **Scalable architecture** - Hybrid storage handles millions of votes efficiently
- **Discussion-driven** - Reddit meets blockchain meets democracy
- **Immutable but private** - Blockchain transparency + ZKP anonymity
- **Community consensus** - No top-down control, citizens decide

## Success Criteria

Your demo must prove:

- ✅ Anonymous voting works (show ZKP verification)
- ✅ Double voting prevented (same credential can't vote twice)
- ✅ Vote aggregates on-chain (not individual votes)
- ✅ Blockchain immutability (visualize chain links)
- ✅ Fair timing (locked promises clearly shown)
- ✅ Privacy preserved (zero personal data)
- ✅ Scalable design (explain hybrid architecture)

## Remember

- **Privacy ≠ Secrecy:** Vote tallies are public, voters are anonymous
- **Blockchain is for results, not records:** Store aggregates, not individual votes
- **ZKP is the killer feature:** This is what sets you apart
- **Make timing visual:** Countdown timers, locked states matter
- **Evidence matters:** Links to news/documents build credibility

Build something that proves democracy can be transparent AND protect citizen privacy.
