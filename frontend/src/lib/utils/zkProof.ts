// Zero-Knowledge Proof utilities (simplified for MVP)

// Simple SHA256 hash using Web Crypto API (browser-native)
async function sha256(message: string): Promise<string> {
  const encoder = new TextEncoder();
  const data = encoder.encode(message);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

export function isValidVoterId(voterId: string): boolean {
  // Voter ID format: numeric, 5-15 characters (Nepal voter IDs are numeric)
  const regex = /^[0-9]{5,15}$/;
  return regex.test(voterId);
}

export function isValidSecret(secret: string): boolean {
  // Secret must be at least 6 characters
  return secret.length >= 6;
}

// MUST match backend's compute_expected_nullifier function!
// Backend: sha256(f"{voter_id}:{secret}")
export async function generateNullifier(voterId: string, secret: string): Promise<string> {
  const combined = `${voterId}:${secret}`;
  const hash = await sha256(combined);
  return `0x${hash}`;
}

export function formatNullifier(nullifier: string): string {
  // Display first 12 chars + ... + last 12 chars
  if (nullifier.length <= 24) return nullifier;
  return `${nullifier.substring(0, 12)}...${nullifier.substring(nullifier.length - 12)}`;
}

export interface ZKProof {
  commitment: string;
  proof: string;
  nullifier: string;
  voter_id_hash?: string;
  merkle_proof?: Array<{hash: string, position: string}>;
}

export async function generateZKProof(
  voterId: string,
  secret: string,
  merkleProof?: Array<{hash: string, position: string}>
): Promise<ZKProof> {
  // Generate nullifier deterministically using same algorithm as backend
  const nullifier = await generateNullifier(voterId, secret);
  
  // Generate voter ID hash (one-way hash of voter ID for privacy)
  const voterIdHash = await sha256(`voter:${voterId}`);
  
  // Simulate commitment (hash of public inputs)
  const commitment = await sha256(`${voterId}:commitment:${Date.now()}`);
  
  // Simulate proof (would be actual SNARK proof in production)
  const proof = await sha256(`proof:${voterId}:${Date.now()}`);
  
  return {
    commitment: `0x${commitment}`,
    proof: `0x${proof}`,
    nullifier,
    voter_id_hash: `0x${voterIdHash.substring(0, 40)}`,
    merkle_proof: merkleProof
  };
}

export async function verifyZKProof(proof: ZKProof): Promise<boolean> {
  // In production, this would verify the actual zk-SNARK proof
  // For MVP, we do basic validation
  return (
    proof.commitment.length > 0 &&
    proof.proof.length > 0 &&
    proof.nullifier.length > 0
  );
}

export function hashVote(
  manifestoId: string,
  voteType: string,
  nullifier: string
): string {
  // Create a unique hash for the vote (for Merkle tree)
  const combined = `${manifestoId}:${voteType}:${nullifier}`;
  return btoa(combined).replace(/[+/=]/g, '').substring(0, 64);
}
