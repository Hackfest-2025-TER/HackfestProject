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
 * Compute keccak256 hash of text (matches backend's Web3.keccak)
 * Uses ethers.js for proper Ethereum-compatible hashing.
 */
export async function computeSHA256(text: string): Promise<string> {
  try {
    // Use ethers.js keccak256 (matches Web3.keccak in backend)
    const { ethers } = await import('ethers');
    // Web3.keccak(text=x) is equivalent to keccak256(toUtf8Bytes(x))
    // ethers v5 uses ethers.utils.keccak256 and ethers.utils.toUtf8Bytes
    const hash = ethers.utils.keccak256(ethers.utils.toUtf8Bytes(text));
    return hash; // Already has 0x prefix
  } catch (e) {
    console.error('Ethers keccak256 failed, falling back to SHA256:', e);
    // Fallback to SHA256 (won't match backend with eth_account!)
    const encoder = new TextEncoder();
    const data = encoder.encode(text);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return '0x' + hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  }
}

/**
 * Compute keccak256 hash (Ethereum style) - alias for computeSHA256
 */
export async function computeKeccak256(text: string): Promise<string> {
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
  // Try to use ethers.js for proper Ethereum signing
  try {
    const { ethers } = await import('ethers');
    const wallet = new ethers.Wallet(privateKey);
    // message is expected to be the hash string (hex)
    // We must convert it to bytes so ethers signs the data, not the string characters
    const messageBytes = ethers.utils.arrayify(message.startsWith('0x') ? message : '0x' + message);
    return await wallet.signMessage(messageBytes);
  } catch (e) {
    console.warn("Ethers signing failed, using simulated fallback (may fail backend verification):", e);
    // Fallback: Simplified signing for MVP (creates a signature-like format)
    const messageHash = await computeSHA256(message);
    const keyHash = await computeSHA256(privateKey);
    const combinedHash = await computeSHA256(messageHash + keyHash);

    // Use provided signer address if available, otherwise derive from key hash
    const addressPart = signerAddress
      ? signerAddress.toLowerCase()
      : '0x' + keyHash.slice(2, 42);

    return `${addressPart}|${combinedHash.slice(2)}`;
  }
}

/**
 * Decrypt a keystore with passphrase and get private key
 * 
 * Uses ethers.js for proper Ethereum keystore decryption,
 * with fallback to simplified format for development.
 */
export async function decryptKeystore(keystore: Keystore, passphrase: string): Promise<string | null> {
  try {
    // Try ethers.js first (proper Ethereum keystore format)
    try {
      const { ethers } = await import('ethers');
      const keystoreJson = JSON.stringify(keystore);
      const wallet = await ethers.Wallet.fromEncryptedJson(keystoreJson, passphrase);
      return wallet.privateKey;
    } catch (ethersError) {
      console.log('Ethers decryption failed, trying simplified format...', ethersError);
    }

    // Fallback: Simplified decryption for MVP
    // The backend uses a matching simplified encryption when eth_account is not available
    const ciphertext = keystore.crypto.ciphertext;

    // Try to decode (our simplified format stores base64 of "privateKey:passphrase:salt")
    try {
      const decoded = atob(ciphertext);
      const parts = decoded.split(':');
      // Check for match (trimming whitespace just in case)
      if (parts.length >= 2 && parts[1].trim() === passphrase.trim()) {
        return parts[0]; // Return private key
      }
    } catch {
      // Not our simplified format either
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
