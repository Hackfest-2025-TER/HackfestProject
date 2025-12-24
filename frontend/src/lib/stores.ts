import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';

// Credential type
interface Credential {
  nullifier: string;
  credential: string;
  nullifierShort: string;
  verified: boolean;
  usedVotes: string[];
  voterIdHash?: string;
  merkleProof?: string[];  createdAt?: string;}

// Auth store type
interface AuthState {
  isAuthenticated: boolean;
  nullifier: string | null;
  credential: Credential | null;
  isLoading?: boolean;
  error?: string | null;
}

// Initialize auth state from localStorage
function createAuthStore() {
  const initialState: AuthState = {
    isAuthenticated: false,
    nullifier: null,
    credential: null
  };

  // Load from localStorage if in browser
  if (browser) {
    const stored = localStorage.getItem('auth');
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        Object.assign(initialState, parsed);
      } catch (e) {
        console.error('Failed to parse auth from localStorage', e);
      }
    }
  }

  const { subscribe, set, update } = writable<AuthState>(initialState);

  return {
    subscribe,
    set: (value: AuthState) => {
      if (browser) {
        localStorage.setItem('auth', JSON.stringify(value));
      }
      set(value);
    },
    update: (fn: (state: AuthState) => AuthState) => {
      update((state) => {
        const newState = fn(state);
        if (browser) {
          localStorage.setItem('auth', JSON.stringify(newState));
        }
        return newState;
      });
    },
    setLoading: (loading: boolean) => {
      update((state) => ({ ...state, isLoading: loading }));
    },
    setError: (error: string | null) => {
      update((state) => ({ ...state, error }));
    },
    setCredential: (credential: Credential) => {
      update((state) => {
        const newState = { ...state, credential, isAuthenticated: true };
        if (browser) {
          localStorage.setItem('auth', JSON.stringify(newState));
        }
        return newState;
      });
    },
    markVoted: (manifestoId: string) => {
      update((state) => {
        if (state.credential) {
          const newState = {
            ...state,
            credential: {
              ...state.credential,
              usedVotes: [...state.credential.usedVotes, manifestoId]
            }
          };
          if (browser) {
            localStorage.setItem('auth', JSON.stringify(newState));
          }
          return newState;
        }
        return state;
      });
    },
    login: (nullifier: string, credentialData: Credential) => {
      const authState = {
        isAuthenticated: true,
        nullifier,
        credential: credentialData
      };
      if (browser) {
        localStorage.setItem('auth', JSON.stringify(authState));
      }
      set(authState);
    },
    logout: () => {
      const authState: AuthState = {
        isAuthenticated: false,
        nullifier: null,
        credential: null
      };
      if (browser) {
        localStorage.removeItem('auth');
      }
      set(authState);
    }
  };
}

// Main auth store
export const authStore = createAuthStore();

// Derived stores for convenience
export const isAuthenticated = derived(authStore, ($auth) => $auth.isAuthenticated);
export const credential = derived(authStore, ($auth) => $auth.credential);
export const nullifier = derived(authStore, ($auth) => $auth.nullifier);

// Export types for use in components
export type { Credential, AuthState };
