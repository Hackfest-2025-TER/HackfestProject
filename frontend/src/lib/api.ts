// API client for PromiseThread backend
const API_BASE_URL = 'http://localhost:8000/api';

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
  politician?: string;
  category?: string;
  search?: string;
}) {
  const params = new URLSearchParams();
  if (filters?.status) params.append('status', filters.status);
  if (filters?.politician) params.append('politician', filters.politician);
  if (filters?.category) params.append('category', filters.category);
  if (filters?.search) params.append('search', filters.search);

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
  const response = await fetch(`${API_BASE_URL}/voters/lookup/${voterId}`);
  if (!response.ok) throw new Error('Voter not found');
  return response.json();
}

export async function searchVoters(query: string) {
  const response = await fetch(`${API_BASE_URL}/voters/search?q=${encodeURIComponent(query)}`);
  if (!response.ok) throw new Error('Failed to search voters');
  return response.json();
}

// Comments
export async function getComments(manifestoId: string) {
  const response = await fetch(`${API_BASE_URL}/comments?manifesto_id=${manifestoId}`);
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
  const response = await fetch(`${API_BASE_URL}/comments/${commentId}/upvote`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ nullifier }),
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
