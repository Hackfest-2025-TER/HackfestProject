# Authentication Test Guide

## Understanding the Issue

**The Problem:** Authentication was showing voter name and ward, violating zero-knowledge principles.

**The Fix:** 
1. ✅ Removed `/api/registry/lookup` endpoint that leaked voter information
2. ✅ Removed "Voter Found" card displaying name and ward
3. ✅ Simplified to single-step authentication without revealing identity
4. ✅ All authentication now happens with pure zero-knowledge proofs

## How Authentication Works Now

### Secret Format
For demo purposes, the secret for each voter is: `CITIZENSHIP_{voter_id}`

Example:
- Voter ID: `25327456` → Secret: `CITIZENSHIP_25327456`
- Voter ID: `27090917` → Secret: `CITIZENSHIP_27090917`
- Voter ID: `25226252` → Secret: `CITIZENSHIP_25226252`

### Test Voters (from CSV)

| Voter ID | Secret | Name (NOT revealed to system) | Ward |
|----------|--------|-------------------------------|------|
| 25327456 | CITIZENSHIP_25327456 | अकल तामाङ | 1 |
| 27090917 | CITIZENSHIP_27090917 | अकल बहादुर - | 1 |
| 25226252 | CITIZENSHIP_25226252 | अकल सिं तामाङ | 1 |
| 5651368  | CITIZENSHIP_5651368  | अक्‍कल बाहादुर तामाङ | 1 |
| 5654566  | CITIZENSHIP_5654566  | अजय तामाङ | 1 |

## Testing Steps

### 1. Start the Backend
```bash
cd backend
python main.py
```

### 2. Start the Frontend
```bash
cd frontend
npm run dev
```

### 3. Test Authentication

Go to `http://localhost:3000/auth`

**Test Case 1:** First Voter
- Voter ID: `25327456`
- Secret: `CITIZENSHIP_25327456`
- Expected: ✅ Authentication succeeds WITHOUT showing name/ward

**Test Case 2:** Second Voter
- Voter ID: `27090917`
- Secret: `CITIZENSHIP_27090917`
- Expected: ✅ Authentication succeeds WITHOUT showing name/ward

**Test Case 3:** Invalid Secret
- Voter ID: `25327456`
- Secret: `wrong_secret`
- Expected: ❌ "Invalid credentials" error

### 4. Verify Zero-Knowledge Privacy

After successful authentication, check that:
- ✅ No voter name is displayed anywhere
- ✅ No ward information is shown
- ✅ Only anonymous nullifier is visible (truncated)
- ✅ "Zero-Knowledge Authentication" heading is shown
- ✅ No "Voter Found" card exists

## API Endpoint for Demo Secret Lookup

For testing, you can look up the secret for any voter:

```bash
curl http://localhost:8000/api/zk/demo-secret/25327456
```

Response:
```json
{
  "voter_id": "25327456",
  "demo_secret": "CITIZENSHIP_25327456",
  "commitment": "abc123...",
  "found_in_tree": true,
  "leaf_index": 42,
  "warning": "DEMO ONLY - In production, voters must know their citizenship number"
}
```

## Why It Works Now

### Before (PRIVACY VIOLATION):
1. User enters Voter ID
2. Server looks up voter → returns name + ward 😱
3. UI shows "Voter Found - Name: छत*** - Ward: 3" 😱
4. User enters secret
5. ZK verification happens

**Problem:** Name and ward leaked before ZK proof!

### After (TRUE ZERO-KNOWLEDGE):
1. User enters Voter ID + Secret together
2. Client computes: `commitment = hash(secret + voterID)`
3. Client downloads shuffled commitments from server
4. Client finds their commitment in shuffled array
5. Client builds Merkle proof locally
6. Client sends only nullifier to server (anonymous)
7. No personal information ever revealed! ✅

## Production Notes

In production:
- Voters would use their real citizenship number as secret
- The `/api/zk/demo-secret` endpoint would NOT exist
- Election Commission would delete all voter→secret mappings after tree construction
- Only the shuffled Merkle tree leaves would be published
