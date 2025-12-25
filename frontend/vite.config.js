import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import { nodePolyfills } from 'vite-plugin-node-polyfills';

export default defineConfig({
	plugins: [
		sveltekit(),
		nodePolyfills({
			include: ['buffer', 'crypto', 'stream', 'util', 'events'],
			globals: {
				Buffer: true,
				global: true,
				process: true
			},
			protocolImports: true
		})
	],
	server: {
		host: '0.0.0.0',
		port: 3000,
		proxy: {
			'/api': {
				target: 'http://localhost:8000',
				changeOrigin: true
			}
		}
	},
	define: {
		global: 'globalThis'
	},
	optimizeDeps: {
		include: ['snarkjs', 'circomlibjs', 'ethers']
	},
	ssr: {
		noExternal: ['snarkjs', 'circomlibjs', 'ffjavascript']
	}
});
