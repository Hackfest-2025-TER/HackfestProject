/**
 * Browser polyfills for Node.js modules
 * Required for snarkjs and circomlibjs to work in browser
 */

import { Buffer } from 'buffer';

// Make Buffer available globally
if (typeof window !== 'undefined') {
    (window as any).Buffer = Buffer;
    (window as any).global = window;
    (window as any).process = { env: {} };
}

export {};
