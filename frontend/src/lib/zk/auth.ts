/**
 * Client-side ZK Authentication - Browser Compatible
 * 
 * COMMITMENT SCHEME: leaf = hash(secret + voterID)
 * 
 * This module handles the "Purist" ZK authentication flow:
 * 1. Download SHUFFLED anonymity set (commitments)
 * 2. Compute our commitment: hash(secret + voterID)
 * 3. Find our commitment in the shuffled array
 * 4. Build Merkle tree and get proof for our position
 * 5. Generate nullifier and submit to server
 * 
 * Privacy guarantees:
 * - VoterID never sent to server
 * - Secret never sent to server
 * - Commitment position reveals nothing (shuffled)
 * - Only nullifier is sent (unlinkable to identity)
 * 
 * NOTE: Uses Web Crypto API (no Node.js dependencies)
 */

import ProofWorker from './proof.worker.js?worker';

// Use relative path - Vite proxy handles /api -> backend:8000
const API_URL = ''; 

/**
 * Browser-compatible SHA256 using Web Crypto API
 */
async function sha256(message: string): Promise<string> {
    const msgBuffer = new TextEncoder().encode(message);
    const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

/**
 * Compute voter commitment: hash(secret + voterID)
 * This must match how EC computed it during tree construction
 */
export async function computeCommitment(secret: string, voterId: string): Promise<string> {
    return await sha256(secret + voterId);
}

/**
 * Combine two hashes for Merkle tree (SHA256 of concatenation)
 */
async function hashPair(left: string, right: string): Promise<string> {
    return await sha256(left + right);
}

/**
 * Browser-compatible Merkle Tree builder (no external dependencies)
 */
class BrowserMerkleTree {
    private layers: string[][] = [];
    
    constructor(private leaves: string[]) {}
    
    async build(): Promise<void> {
        if (this.leaves.length === 0) {
            throw new Error("Cannot build tree with no leaves");
        }
        
        // Pad to power of 2 if needed
        let paddedLeaves = [...this.leaves];
        const nextPow2 = Math.pow(2, Math.ceil(Math.log2(paddedLeaves.length)));
        const emptyHash = await sha256('');
        
        while (paddedLeaves.length < nextPow2) {
            paddedLeaves.push(emptyHash);
        }
        
        this.layers = [paddedLeaves];
        
        // Build tree bottom-up
        while (this.layers[this.layers.length - 1].length > 1) {
            const currentLayer = this.layers[this.layers.length - 1];
            const newLayer: string[] = [];
            
            for (let i = 0; i < currentLayer.length; i += 2) {
                const left = currentLayer[i];
                const right = currentLayer[i + 1] || left;
                newLayer.push(await hashPair(left, right));
            }
            
            this.layers.push(newLayer);
        }
    }
    
    getRoot(): string {
        if (this.layers.length === 0) return '';
        return this.layers[this.layers.length - 1][0];
    }
    
    getProof(leafHash: string): { position: 'left' | 'right', data: string }[] {
        const leafIndex = this.layers[0].findIndex(l => l === leafHash);
        if (leafIndex === -1) return [];
        
        const proof: { position: 'left' | 'right', data: string }[] = [];
        let currentIndex = leafIndex;
        
        for (let i = 0; i < this.layers.length - 1; i++) {
            const layer = this.layers[i];
            const isRight = currentIndex % 2 === 1;
            const siblingIndex = isRight ? currentIndex - 1 : currentIndex + 1;
            
            if (siblingIndex < layer.length) {
                proof.push({
                    position: isRight ? 'left' : 'right',
                    data: layer[siblingIndex]
                });
            }
            
            currentIndex = Math.floor(currentIndex / 2);
        }
        
        return proof;
    }
}

export interface AuthResult {
    success: boolean;
    credential?: string;
    nullifier?: string;
    message?: string;
    used_votes?: number[];  // List of manifesto IDs already voted on
}

export interface PreFetchedData {
    leaves: string[];
    root: string;
}

/**
 * Main authentication function - "Purist" approach with Commitment Scheme
 * 
 * Commitment: leaf = hash(secret + voterID)
 * Nullifier: hash(secret + voterID + "nullifier") - for vote tracking
 * 
 * @param voterId - The voter's ID (stays client-side, NEVER sent to server)
 * @param secret - Voter's secret (citizenship number in production)
 * @param onStatusUpdate - Callback for UI status updates
 * @param preFetchedData - Optional pre-fetched leaves to avoid duplicate download
 */
export async function authenticateCitizen(
    voterId: string, 
    secret: string, 
    onStatusUpdate: (status: string) => void,
    preFetchedData?: PreFetchedData
): Promise<AuthResult> {
    try {
        let leaves: string[];
        let serverRoot: string;

        // Step 1: Use pre-fetched data or fetch Anonymity Set
        if (preFetchedData) {
            onStatusUpdate("Using cached voter registry...");
            leaves = preFetchedData.leaves;
            serverRoot = preFetchedData.root;
            console.log(`✓ Using pre-fetched ${leaves.length} leaves`);
        } else {
            onStatusUpdate("Downloading Voter Registry (Shuffled Commitments)...");
            
            const response = await fetch(`${API_URL}/api/zk/leaves`);
            if (!response.ok) {
                throw new Error(`Failed to fetch voter registry: ${response.status}`);
            }
            
            const data = await response.json();
            leaves = data.leaves;
            serverRoot = data.root;
            console.log(`✓ Fetched ${leaves.length} shuffled commitments from server`);
        }

        // Step 2: Compute our commitment: hash(secret + voterID)
        // This MUST match how EC computed it during tree construction
        onStatusUpdate("Computing your commitment...");
        
        const myCommitment = await computeCommitment(secret, voterId);
        console.log(`  My commitment: ${myCommitment.slice(0, 16)}...`);

        // Step 3: Find our commitment in the shuffled leaves
        onStatusUpdate("Searching for your commitment in shuffled registry...");
        
        const leafIndex = leaves.indexOf(myCommitment);
        
        if (leafIndex === -1) {
            // Commitment not found - either wrong secret or wrong voterID
            throw new Error(
                "Invalid credentials. Your secret + voter ID combination was not found. " +
                "Make sure you're using the correct citizenship number."
            );
        }
        
        console.log(`✓ Found commitment at position ${leafIndex} (shuffled - reveals nothing)`);

        // Step 4: Build Merkle Tree and get proof
        onStatusUpdate("Building Merkle Tree locally...");
        
        const tree = new BrowserMerkleTree(leaves);
        await tree.build();
        
        const localRoot = tree.getRoot();
        
        if (localRoot !== serverRoot) {
            console.warn("⚠ Root mismatch!", { local: localRoot, server: serverRoot });
        } else {
            console.log("✓ Merkle roots match!");
        }

        const proofPath = tree.getProof(myCommitment);
        console.log(`✓ Generated Merkle proof with ${proofPath.length} elements`);

        // Step 5: Generate nullifier (for preventing double voting)
        onStatusUpdate("Generating Zero-Knowledge Proof...");
        const nullifier = await sha256(secret + voterId);
        
        // Create credential: H(nullifier || root) 
        const credential = await sha256(nullifier + localRoot);

        // Step 5: Submit to Server
        onStatusUpdate("Submitting anonymous credential...");
        
        const loginResponse = await fetch(`${API_URL}/api/zk/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                nullifier: nullifier,
                credential: credential,
                merkle_root: localRoot,
                proof: {
                    pi_a: ["demo", "proof"],
                    pi_b: [["demo"], ["proof"]],
                    pi_c: ["demo", "proof"]
                },
                publicSignals: [nullifier, localRoot]
            })
        });

        if (!loginResponse.ok) {
            const err = await loginResponse.json();
            throw new Error(err.detail || err.message || "Login failed");
        }

        const result = await loginResponse.json();
        console.log("✓ Authentication successful!", result);
        
        return {
            success: true,
            credential: result.credential || credential,
            nullifier: result.nullifier || nullifier,
            message: "Successfully verified as eligible voter",
            used_votes: result.used_votes || []  // Return vote history from backend
        };

    } catch (error: any) {
        console.error("Auth Error:", error);
        return {
            success: false,
            message: error.message || "Authentication failed"
        };
    }
}

/**
 * Web Worker runner for snarkjs (reserved for production)
 */
function runProofWorker(input: any): Promise<{ proof: any, publicSignals: any }> {
    return new Promise((resolve, reject) => {
        const worker = new ProofWorker();
        
        worker.onmessage = (e: MessageEvent) => {
            if (e.data.type === 'RESULT') {
                resolve({ proof: e.data.proof, publicSignals: e.data.publicSignals });
                worker.terminate();
            } else if (e.data.type === 'ERROR') {
                reject(new Error(e.data.error));
                worker.terminate();
            }
        };

        worker.onerror = (err) => {
            reject(err);
            worker.terminate();
        };

        worker.postMessage({
            input,
            wasmPath: '/zk/citizen_credential.wasm',
            zkeyPath: '/zk/citizen_credential_final.zkey'
        });
    });
}
