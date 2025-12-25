/**
 * Browser polyfills for Node.js modules
 * Required for snarkjs and circomlibjs to work in browser
 * 
 * Note: Polyfills are handled by vite-plugin-node-polyfills
 */

if (typeof globalThis !== 'undefined') {
    (globalThis as any).global = globalThis;
}

export {};
