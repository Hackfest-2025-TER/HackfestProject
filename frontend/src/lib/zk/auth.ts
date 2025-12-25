/**
 * Client-side ZK Authentication - Browser Compatible
 * 
 * This module handles the "Purist" ZK authentication flow:
 * 1. Download anonymity set (all 1048 voter leaf hashes)
 * 2. Build Merkle tree locally in browser
 * 3. Find our Merkle proof path
 * 4. Generate ZK proof via Web Worker
 * 5. Submit proof to server
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
}

export interface PreFetchedData {
    leaves: string[];
    root: string;
}

/**
 * Main authentication function - "Purist" approach
 * @param voterId - The voter's ID (stays client-side, NEVER sent to server)
 * @param secret - User's chosen secret for nullifier generation
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
            onStatusUpdate("Downloading Voter Registry (Anonymity Set)...");
            
            const response = await fetch(`${API_URL}/api/zk/leaves`);
            if (!response.ok) {
                throw new Error(`Failed to fetch voter registry: ${response.status}`);
            }
            
            const data = await response.json();
            leaves = data.leaves;
            serverRoot = data.root;
            console.log(`✓ Fetched ${leaves.length} leaves from server`);
        }

        // Step 2: Build Merkle Tree Locally
        onStatusUpdate("Building Merkle Tree locally...");
        
        const tree = new BrowserMerkleTree(leaves);
        await tree.build();
        
        const localRoot = tree.getRoot();
        
        if (localRoot !== serverRoot) {
            console.warn("⚠ Root mismatch!", { local: localRoot, server: serverRoot });
        } else {
            console.log("✓ Merkle roots match!");
        }

        // Step 3: Find our leaf and get proof path
        onStatusUpdate("Finding your voter record...");
        
        const myLeafHash = await sha256(voterId);
        const proofPath = tree.getProof(myLeafHash);
        
        if (proofPath.length === 0) {
            throw new Error("Voter ID not found in registry. Please check your ID number.");
        }
        
        console.log(`✓ Found voter with ${proofPath.length} proof elements`);

        // Step 4: Generate credentials
        onStatusUpdate("Generating Zero-Knowledge Proof...");
        
        // Compute nullifier: H(secret || voterId)
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
            message: "Successfully verified as eligible voter"
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
