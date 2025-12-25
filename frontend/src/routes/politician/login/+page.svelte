<script lang="ts">
  import Header from '$lib/components/Header.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import { Shield, User, Lock, Eye, EyeOff, AlertCircle, ArrowRight, Building2 } from 'lucide-svelte';
  import { goto } from '$app/navigation';
  
  // Form state
  let email = '';
  let password = '';
  let showPassword = false;
  let isLoading = false;
  let error = '';
  
  // Demo politicians for quick login
  const demoPoliticians = [
    { id: 1, name: 'KP Sharma Oli', party: 'CPN-UML', email: 'oli@demo.np' },
    { id: 2, name: 'Pushpa Kamal Dahal', party: 'CPN-MC', email: 'prachanda@demo.np' },
    { id: 3, name: 'Sher Bahadur Deuba', party: 'Nepali Congress', email: 'deuba@demo.np' },
  ];
  
  async function handleLogin(event: Event) {
    event.preventDefault();
    error = '';
    
    if (!email || !password) {
      error = 'Please enter email and password';
      return;
    }
    
    isLoading = true;
    
    try {
      // Demo login - in production this would be a real API call
      const demoPolitician = demoPoliticians.find(p => p.email === email);
      
      if (demoPolitician && password === 'demo123') {
        // Store politician session
        localStorage.setItem('politician_session', JSON.stringify({
          id: demoPolitician.id,
          name: demoPolitician.name,
          party: demoPolitician.party,
          email: demoPolitician.email,
          loggedInAt: new Date().toISOString()
        }));
        
        // Redirect to dashboard
        goto('/politician/dashboard');
      } else {
        error = 'Invalid credentials. Try demo login below.';
      }
    } catch (e: any) {
      error = e.message || 'Login failed';
    } finally {
      isLoading = false;
    }
  }
  
  function quickLogin(politician: typeof demoPoliticians[0]) {
    email = politician.email;
    password = 'demo123';
  }
</script>

<svelte:head>
  <title>Politician Login - PromiseThread</title>
</svelte:head>

<Header />

<main class="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4">
  <div class="w-full max-w-md">
    <!-- Header -->
    <div class="text-center mb-8">
      <div class="w-16 h-16 rounded-2xl bg-[#082770]/10 flex items-center justify-center mx-auto mb-4">
        <Building2 class="w-8 h-8 text-[#082770]" />
      </div>
      <h1 class="text-3xl font-bold text-[#082770] mb-2">Politician Portal</h1>
      <p class="text-gray-600">Sign in to manage your manifestos and commitments</p>
    </div>
    
    <!-- Login Form -->
    <div class="bg-white border border-gray-200 rounded-2xl p-6 shadow-lg">
      <form on:submit={handleLogin} class="space-y-4">
        {#if error}
          <div class="bg-red-500/10 border border-red-500/20 rounded-lg p-3 flex items-start gap-2">
            <AlertCircle class="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
            <span class="text-red-400 text-sm">{error}</span>
          </div>
        {/if}
        
        <div>
          <label for="email" class="block text-sm font-medium text-slate-300 mb-2">Email</label>
          <div class="relative">
            <User class="w-5 h-5 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="email"
              id="email"
              bind:value={email}
              placeholder="your@email.com"
              class="w-full bg-slate-900/50 border border-slate-600 rounded-lg pl-10 pr-4 py-3 text-white placeholder-slate-500 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition-colors"
            />
          </div>
        </div>
        
        <div>
          <label for="password" class="block text-sm font-medium text-slate-300 mb-2">Password</label>
          <div class="relative">
            <Lock class="w-5 h-5 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
            {#if showPassword}
              <input
                type="text"
                id="password"
                bind:value={password}
                placeholder="••••••••"
                class="w-full bg-slate-900/50 border border-slate-600 rounded-lg pl-10 pr-12 py-3 text-white placeholder-slate-500 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition-colors"
              />
            {:else}
              <input
                type="password"
                id="password"
                bind:value={password}
                placeholder="••••••••"
                class="w-full bg-slate-900/50 border border-slate-600 rounded-lg pl-10 pr-12 py-3 text-white placeholder-slate-500 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition-colors"
              />
            {/if}
            <button
              type="button"
              on:click={() => showPassword = !showPassword}
              class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
            >
              {#if showPassword}
                <EyeOff class="w-5 h-5" />
              {:else}
                <Eye class="w-5 h-5" />
              {/if}
            </button>
          </div>
        </div>
        
        <button
          type="submit"
          disabled={isLoading}
          class="w-full bg-blue-500 hover:bg-blue-600 disabled:bg-blue-500/50 text-white font-medium py-3 rounded-lg transition-colors flex items-center justify-center gap-2"
        >
          {#if isLoading}
            <div class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
            Signing in...
          {:else}
            Sign In
            <ArrowRight class="w-5 h-5" />
          {/if}
        </button>
      </form>
      
      <!-- Demo Login Section -->
      <div class="mt-6 pt-6 border-t border-slate-700">
        <p class="text-center text-slate-400 text-sm mb-4">Quick Demo Login</p>
        <div class="space-y-2">
          {#each demoPoliticians as politician}
            <button
              on:click={() => quickLogin(politician)}
              class="w-full bg-slate-700/50 hover:bg-slate-700 border border-slate-600 rounded-lg p-3 text-left transition-colors group"
            >
              <div class="flex items-center justify-between">
                <div>
                  <div class="text-white font-medium">{politician.name}</div>
                  <div class="text-slate-400 text-sm">{politician.party}</div>
                </div>
                <ArrowRight class="w-5 h-5 text-slate-500 group-hover:text-blue-400 transition-colors" />
              </div>
            </button>
          {/each}
        </div>
        <p class="text-center text-slate-500 text-xs mt-4">
          Password for demo accounts: <code class="bg-slate-700 px-1 py-0.5 rounded">demo123</code>
        </p>
      </div>
    </div>
    
    <!-- Info Note -->
    <div class="mt-6 text-center">
      <p class="text-slate-500 text-sm">
        Are you a citizen? <a href="/auth" class="text-emerald-400 hover:underline">Verify anonymously here</a>
      </p>
    </div>
  </div>
</main>

<Footer />
