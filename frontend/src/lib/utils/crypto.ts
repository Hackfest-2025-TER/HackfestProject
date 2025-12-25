/**
 * Cryptographic utilities for digital signatures
 * 
 * This module handles:
 * - SHA256 hashing (for manifesto commitment)
 * - Keystore file parsing/encryption
 * - Message signing with private keys
 * 
 * Security: Private keys are handled only in memory, never stored
 */

// ============= Hash Functions =============

/**
 * Compute SHA256 hash of text (for manifesto commitment)
 */
export async function computeSHA256(text: string): Promise<string> {
  const encoder = new TextEncoder();
  const data = encoder.encode(text);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return '0x' + hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

/**
 * Compute keccak256 hash (Ethereum style) - simplified version
 * In production, use ethers.js or web3.js for proper keccak256
 */
export async function computeKeccak256(text: string): Promise<string> {
  // For now, use SHA256 as fallback (proper keccak256 requires library)
  return computeSHA256(text);
}

// ============= Keystore Handling =============

export interface Keystore {
  version: number;
  id: string;
  address: string;
  crypto: {
    cipher: string;
    ciphertext: string;
    cipherparams: { iv: string };
    kdf: string;
    kdfparams: {
      dklen: number;
      salt: string;
      n: number;
      r: number;
      p: number;
    };
    mac: string;
  };
  meta?: {
    created_at: string;
    platform: string;
  };
}

/**
 * Parse a keystore JSON file
 */
export function parseKeystore(content: string): Keystore | null {
  try {
    const keystore = JSON.parse(content);
    if (keystore.version && keystore.address && keystore.crypto) {
      return keystore;
    }
    return null;
  } catch {
    return null;
  }
}

/**
 * Get address from keystore
 */
export function getAddressFromKeystore(keystore: Keystore): string {
  return '0x' + keystore.address.toLowerCase();
}

/**
 * Download keystore as JSON file
 */
export function downloadKeystore(keystore: Keystore, filename: string): void {
  const blob = new Blob([JSON.stringify(keystore, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

// ============= Signing (Simplified for MVP) =============

/**
 * Sign a message with a private key
 * 
 * NOTE: For production, use ethers.js:
 * const wallet = new ethers.Wallet(privateKey);
 * const signature = await wallet.signMessage(message);
 * 
 * This simplified version is for demonstration.
 * 
 * @param message - The message to sign (typically a hash)
 * @param privateKey - The private key to sign with
 * @param signerAddress - Optional: The actual wallet address (for simplified verification)
 */
export async function signMessage(message: string, privateKey: string, signerAddress?: string): Promise<string> {
  // In production with ethers.js:
  // import { ethers } from 'ethers';
  // const wallet = new ethers.Wallet(privateKey);
  // return await wallet.signMessage(ethers.getBytes(await computeKeccak256(message)));
  
  // Simplified signing for MVP (creates a signature-like format)
  // The backend will verify using the same simplified method
  const messageHash = await computeSHA256(message);
  const keyHash = await computeSHA256(privateKey);
  const combinedHash = await computeSHA256(messageHash + keyHash);
  
  // Use provided signer address if available, otherwise derive from key hash
  const addressPart = signerAddress 
    ? signerAddress.toLowerCase()
    : '0x' + keyHash.slice(2, 42);
  
  // Create signature in format: address|signature_data
  // This allows the backend to verify by matching the address
  return `${addressPart}|${combinedHash.slice(2)}`;
}

/**
 * Decrypt a keystore with passphrase and get private key
 * 
 * NOTE: For production, use ethers.js:
 * const wallet = await ethers.Wallet.fromEncryptedJson(keystoreJson, passphrase);
 * return wallet.privateKey;
 * 
 * This simplified version is for demonstration.
 */
export async function decryptKeystore(keystore: Keystore, passphrase: string): Promise<string | null> {
  try {
    // In production with ethers.js:
    // import { ethers } from 'ethers';
    // const wallet = await ethers.Wallet.fromEncryptedJson(JSON.stringify(keystore), passphrase);
    // return wallet.privateKey;
    
    // Simplified decryption for MVP
    // The backend uses a matching simplified encryption
    const ciphertext = keystore.crypto.ciphertext;
    
    // Try to decode (our simplified format stores base64 of "privateKey:passphrase:salt")
    try {
      const decoded = atob(ciphertext);
      const parts = decoded.split(':');
      if (parts.length >= 2 && parts[1] === passphrase) {
        return parts[0]; // Return private key
      }
    } catch {
      // Not our simplified format, might be real encrypted keystore
    }
    
    return null;
  } catch {
    return null;
  }
}

/**
 * Verify a private key matches an address
 */
export async function verifyKeyMatchesAddress(privateKey: string, address: string): Promise<boolean> {
  // In production with ethers.js:
  // const wallet = new ethers.Wallet(privateKey);
  // return wallet.address.toLowerCase() === address.toLowerCase();
  
  // Simplified verification
  const keyHash = await computeSHA256(privateKey);
  const derivedAddress = '0x' + keyHash.slice(2, 42);
  return derivedAddress.toLowerCase() === address.toLowerCase();
}

// ============= Utility Functions =============

/**
 * Format address for display (0x1234...5678)
 */
export function formatAddress(address: string): string {
  if (!address || address.length < 10) return address || '';
  return `${address.slice(0, 6)}...${address.slice(-4)}`;
}

/**
 * Validate Ethereum address format
 */
export function isValidAddress(address: string): boolean {
  return /^0x[a-fA-F0-9]{40}$/.test(address);
}

/**
 * Validate private key format
 */
export function isValidPrivateKey(key: string): boolean {
  return /^0x[a-fA-F0-9]{64}$/.test(key);
}

/**
 * Read file as text
 */
export function readFileAsText(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = () => reject(reader.error);
    reader.readAsText(file);
  });
}
