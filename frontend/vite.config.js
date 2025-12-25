import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
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
	resolve: {
		alias: {
			// Polyfills for Node.js modules in browser
			buffer: 'buffer/',
			events: 'events/',
			util: 'util/',
			stream: 'stream-browserify',
			crypto: 'crypto-browserify'
		}
	},
	define: {
		// Define global for browser compatibility
		global: 'globalThis',
		'process.env': {}
	},
	optimizeDeps: {
		esbuildOptions: {
			// Enable polyfills
			define: {
				global: 'globalThis'
			}
		},
		include: ['buffer', 'events', 'util', 'stream-browserify', 'crypto-browserify']
	}
});
