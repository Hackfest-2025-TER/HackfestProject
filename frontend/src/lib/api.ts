// API client for PromiseThread backend
// Use Vite's import.meta.env for environment variables
// In Docker/Production, we use relative path /api which is proxied
const API_BASE_URL = '/api';

// Helper function to handle fetch errors
async function fetchWithErrorHandling(url: string, options?: RequestInit) {
  try {
    const response = await fetch(url, options);
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }
    return response.json();
  } catch (error: any) {
    if (error.message.includes('fetch')) {
      throw new Error('Backend server is not running. Please start it on port 8000.');
    }
    throw error;
  }
}

// Manifestos
export async function getManifestos(filters?: {
  status?: string;
  politician_id?: number;
  category?: string;
}) {
  const params = new URLSearchParams();
  if (filters?.status) params.append('status', filters.status);
  if (filters?.politician_id) params.append('politician_id', filters.politician_id.toString());
  if (filters?.category) params.append('category', filters.category);

  const url = `${API_BASE_URL}/manifestos?${params.toString()}`;
  return fetchWithErrorHandling(url);
}

export async function getManifesto(id: string) {
  return fetchWithErrorHandling(`${API_BASE_URL}/manifestos/${id}`);
}

// Votes
export async function submitVote(data: {
  manifesto_id: string;
  vote_type: 'kept' | 'broken';
  nullifier: string;
  evidence_url?: string;
}) {
  const response = await fetch(`${API_BASE_URL}/votes`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to submit vote');
  }
  return response.json();
}

export async function getVoteVerification(voteHash: string) {
  const response = await fetch(`${API_BASE_URL}/votes/verify/${voteHash}`);
  if (!response.ok) throw new Error('Failed to verify vote');
  return response.json();
}

// ZK Proofs
export async function verifyZKProof(proof: {
  commitment: string;
  proof?: string;
  nullifier: string;
  voter_id_hash?: string;
  merkle_proof?: string[];
}) {
  const response = await fetch(`${API_BASE_URL}/zk/verify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(proof),
  });
  if (!response.ok) throw new Error('Failed to verify ZK proof');
  return response.json();
}

// Voter lookup
export async function lookupVoter(voterId: string) {
  const response = await fetch(`${API_BASE_URL}/registry/lookup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ voter_id: voterId }),
  });
  if (!response.ok) throw new Error('Voter not found');
  return response.json();
}

export async function searchVoters(query: string) {
  const response = await fetch(`${API_BASE_URL}/registry/search?q=${encodeURIComponent(query)}`);
  if (!response.ok) throw new Error('Failed to search voters');
  return response.json();
}

// Comments
export async function getComments(manifestoId: string) {
  const response = await fetch(`${API_BASE_URL}/manifestos/${manifestoId}/comments`);
  if (!response.ok) throw new Error('Failed to fetch comments');
  return response.json();
}

export async function addComment(data: {
  manifesto_id: string;
  content: string;
  nullifier: string;
  parent_id?: string;
}) {
  const response = await fetch(`${API_BASE_URL}/comments`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error('Failed to add comment');
  return response.json();
}

export async function upvoteComment(commentId: string, nullifier: string) {
  const response = await fetch(`${API_BASE_URL}/comments/${commentId}/vote`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ nullifier, vote_type: 'up' }),
  });
  if (!response.ok) throw new Error('Failed to upvote comment');
  return response.json();
}

// Blockchain/Audit
export async function getMerkleRoot() {
  const response = await fetch(`${API_BASE_URL}/registry/merkle-root`);
  if (!response.ok) throw new Error('Failed to fetch Merkle root');
  return response.json();
}

export async function getBlocks(limit: number = 10) {
  const response = await fetch(`${API_BASE_URL}/blockchain/blocks?limit=${limit}`);
  if (!response.ok) throw new Error('Failed to fetch blocks');
  return response.json();
}

export async function getNetworkStats() {
  const response = await fetch(`${API_BASE_URL}/network/stats`);
  if (!response.ok) throw new Error('Failed to fetch network stats');
  return response.json();
}

// Politicians
export async function getPoliticians() {
  const response = await fetch(`${API_BASE_URL}/politicians`);
  if (!response.ok) throw new Error('Failed to fetch politicians');
  return response.json();
}

export async function getPolitician(id: string) {
  const response = await fetch(`${API_BASE_URL}/politicians/${id}`);
  if (!response.ok) throw new Error('Failed to fetch politician');
  return response.json();
}

// ============= Digital Signature APIs =============

export async function generatePoliticianWallet(politicianId: number, passphrase: string) {
  const response = await fetch(`${API_BASE_URL}/politicians/${politicianId}/generate-wallet`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ passphrase }),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to generate wallet');
  }
  return response.json();
}

export async function getPoliticianWalletStatus(politicianId: number) {
  const response = await fetch(`${API_BASE_URL}/politicians/${politicianId}/wallet-status`);
  if (!response.ok) throw new Error('Failed to fetch wallet status');
  return response.json();
}

export async function rotateKey(politicianId: number, reason: string, newPassphrase: string, adminToken: string) {
  const response = await fetch(`${API_BASE_URL}/politicians/${politicianId}/rotate-key`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      politician_id: politicianId,
      reason,
      new_passphrase: newPassphrase,
      admin_token: adminToken,
    }),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to rotate key');
  }
  return response.json();
}

export async function submitSignedManifesto(data: {
  title: string;
  description: string;
  category: string;
  politician_id: number;
  grace_period_days?: number;
  manifesto_hash: string;
  signature: string;
}) {
  const response = await fetch(`${API_BASE_URL}/manifestos/submit-signed`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      ...data,
      grace_period_days: data.grace_period_days || 7,
    }),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to submit manifesto');
  }
  return response.json();
}

export async function verifyManifesto(manifestoId: number) {
  const response = await fetch(`${API_BASE_URL}/manifestos/${manifestoId}/verify`);
  if (!response.ok) throw new Error('Failed to verify manifesto');
  return response.json();
}

export async function verifyManifestoText(manifestoId: number, manifestoText: string) {
  const response = await fetch(`${API_BASE_URL}/manifestos/verify-text`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ manifesto_id: manifestoId, manifesto_text: manifestoText }),
  });
  if (!response.ok) throw new Error('Failed to verify manifesto text');
  return response.json();
}
