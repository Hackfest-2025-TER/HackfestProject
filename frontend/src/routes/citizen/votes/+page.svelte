<script lang="ts">
  import Header from '$lib/components/Header.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import { 
    Vote, CheckCircle, XCircle, Clock, Calendar, Hash,
    ChevronRight, Shield, AlertCircle, ExternalLink, Filter
  } from 'lucide-svelte';
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { browser } from '$app/environment';
  import { authStore, isAuthenticated, credential } from '$lib/stores';
  import { getManifesto } from '$lib/api';
  
  // Reactive auth state
  $: isAuth = $isAuthenticated;
  $: userCredential = $credential;
  
  // Data
  let votedManifestos: any[] = [];
  let isLoading = true;
  let error = '';
  
  // Filter
  let voteFilter = 'all';
  
  onMount(async () => {
    if (!browser) return;
    
    // Check if authenticated
    if (!$isAuthenticated) {
      goto('/auth');
      return;
    }
    
    await loadVotedManifestos();
  });
  
  async function loadVotedManifestos() {
    try {
      isLoading = true;
      const votedIds = userCredential?.usedVotes || [];
      
      // Load details for each voted manifesto
      const manifestoPromises = votedIds.map(async (id: string) => {
        try {
          const manifesto = await getManifesto(id);
          // In a real app, we'd store the vote type with the ID
          // For demo, we'll randomly assign or use local storage
          const storedVote = localStorage.getItem(`vote_${id}`);
          return {
            ...manifesto,
            myVote: storedVote || 'kept', // Default assumption
            votedAt: localStorage.getItem(`vote_time_${id}`) || new Date().toISOString()
          };
        } catch (e) {
          return null;
        }
      });
      
      const results = await Promise.all(manifestoPromises);
      votedManifestos = results.filter(m => m !== null);
    } catch (e: any) {
      error = e.message || 'Failed to load votes';
    } finally {
      isLoading = false;
    }
  }
  
  // Filtered manifestos
  $: filteredManifestos = voteFilter === 'all' 
    ? votedManifestos 
    : votedManifestos.filter(m => m.myVote === voteFilter);
  
  // Stats
  $: stats = {
    total: votedManifestos.length,
    kept: votedManifestos.filter(m => m.myVote === 'kept').length,
    broken: votedManifestos.filter(m => m.myVote === 'broken').length
  };
  
  function formatDate(dateStr: string) {
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  }
  
  function getVoteIcon(vote: string) {
    return vote === 'kept' ? CheckCircle : XCircle;
  }
  
  function getVoteColor(vote: string) {
    return vote === 'kept' 
      ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20'
      : 'text-red-400 bg-red-500/10 border-red-500/20';
  }
</script>

<svelte:head>
  <title>My Votes - PromiseThread</title>
</svelte:head>

<Header />

<main class="min-h-screen bg-gray-50 py-8">
  <div class="max-w-4xl mx-auto px-4">
    <!-- Header -->
    <div class="mb-8">
      <div class="flex items-center gap-3 mb-4">
        <div class="w-12 h-12 rounded-xl bg-[#082770]/10 flex items-center justify-center">
          <Vote class="w-6 h-6 text-[#082770]" />
        </div>
        <div>
          <h1 class="text-3xl font-bold text-[#082770]">My Votes</h1>
          <p class="text-gray-600">Your anonymous voting history</p>
        </div>
      </div>
    </div>
    
    {#if !isAuth}
      <!-- Not authenticated -->
      <div class="bg-slate-800/50 border border-slate-700 rounded-xl p-8 text-center">
        <Shield class="w-12 h-12 text-slate-600 mx-auto mb-4" />
        <h2 class="text-xl font-semibold text-white mb-2">Authentication Required</h2>
        <p class="text-slate-400 mb-6">You need to verify as a citizen to view your votes.</p>
        <a 
          href="/auth"
          class="inline-flex items-center gap-2 bg-emerald-500 hover:bg-emerald-600 text-white px-6 py-3 rounded-lg transition-colors"
        >
          <Shield class="w-5 h-5" />
          Verify as Citizen
        </a>
      </div>
    {:else if isLoading}
      <div class="text-center py-12">
        <div class="w-8 h-8 border-2 border-emerald-500/30 border-t-emerald-500 rounded-full animate-spin mx-auto mb-4"></div>
        <p class="text-slate-400">Loading your votes...</p>
      </div>
    {:else if error}
      <div class="bg-red-500/10 border border-red-500/20 rounded-xl p-6 text-center">
        <AlertCircle class="w-8 h-8 text-red-400 mx-auto mb-2" />
        <p class="text-red-400">{error}</p>
      </div>
    {:else}
      <!-- Stats -->
      <div class="grid grid-cols-3 gap-4 mb-8">
        <div class="bg-white border border-gray-200 rounded-xl p-4 text-center">
          <div class="text-2xl font-bold text-gray-900 mb-1">{stats.total}</div>
          <div class="text-gray-600 text-sm">Total Votes</div>
        </div>
        <div class="bg-white border border-gray-200 rounded-xl p-4 text-center">
          <div class="text-2xl font-bold text-emerald-600 mb-1">{stats.kept}</div>
          <div class="text-gray-600 text-sm">Voted Kept</div>
        </div>
        <div class="bg-white border border-gray-200 rounded-xl p-4 text-center">
          <div class="text-2xl font-bold text-red-600 mb-1">{stats.broken}</div>
          <div class="text-gray-600 text-sm">Voted Broken</div>
        </div>
      </div>
      
      <!-- Privacy Notice -->
      <div class="bg-purple-50 border border-purple-200 rounded-xl p-4 mb-6">
        <div class="flex gap-3">
          <Shield class="w-5 h-5 text-purple-600 flex-shrink-0 mt-0.5" />
          <div>
            <h3 class="text-purple-800 font-medium mb-1">Your Privacy is Protected</h3>
            <p class="text-purple-700 text-sm">
              This history is stored locally in your browser. No one else can see your individual votes.
              Only aggregate totals are public.
            </p>
          </div>
        </div>
      </div>
      
      <!-- Filter -->
      <div class="flex items-center gap-4 mb-6">
        <Filter class="w-5 h-5 text-gray-500" />
        <div class="flex gap-2">
          <button
            on:click={() => voteFilter = 'all'}
            class="px-4 py-2 rounded-lg text-sm font-medium transition-colors
              {voteFilter === 'all' ? 'bg-gray-200 text-gray-900' : 'text-gray-600 hover:text-gray-900'}"
          >
            All
          </button>
          <button
            on:click={() => voteFilter = 'kept'}
            class="px-4 py-2 rounded-lg text-sm font-medium transition-colors
              {voteFilter === 'kept' ? 'bg-emerald-100 text-emerald-700' : 'text-gray-600 hover:text-gray-900'}"
          >
            Kept
          </button>
          <button
            on:click={() => voteFilter = 'broken'}
            class="px-4 py-2 rounded-lg text-sm font-medium transition-colors
              {voteFilter === 'broken' ? 'bg-red-100 text-red-700' : 'text-gray-600 hover:text-gray-900'}"
          >
            Broken
          </button>
        </div>
      </div>
      
      <!-- Votes List -->
      {#if filteredManifestos.length === 0}
        <div class="bg-white border border-gray-200 rounded-xl p-12 text-center">
          <Vote class="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 class="text-xl font-semibold text-gray-900 mb-2">No votes yet</h3>
          <p class="text-gray-600 mb-6">
            {votedManifestos.length === 0 
              ? "You haven't voted on any promises yet."
              : "No votes match this filter."}
          </p>
          {#if votedManifestos.length === 0}
            <a 
              href="/manifestos"
              class="inline-flex items-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white px-5 py-3 rounded-lg transition-colors"
            >
              Browse Promises
              <ChevronRight class="w-5 h-5" />
            </a>
          {/if}
        </div>
      {:else}
        <div class="space-y-4">
          {#each filteredManifestos as manifesto}
            {@const total = (manifesto.vote_kept || 0) + (manifesto.vote_broken || 0)}
            {@const keptPercent = total > 0 ? ((manifesto.vote_kept || 0) / total) * 100 : 50}
            <div class="bg-white border border-gray-200 rounded-xl p-5">
              <div class="flex items-start justify-between gap-4">
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-3 mb-2">
                    <a 
                      href="/manifestos/{manifesto.id}"
                      class="text-lg font-semibold text-gray-900 hover:text-emerald-600 transition-colors truncate"
                    >
                      {manifesto.title}
                    </a>
                  </div>
                  
                  <p class="text-gray-600 text-sm line-clamp-2 mb-3">
                    {manifesto.description}
                  </p>
                  
                  <div class="flex flex-wrap items-center gap-4 text-sm">
                    <div class="flex items-center gap-1 text-gray-500">
                      <span class="text-gray-600">By:</span>
                      <span class="text-gray-900">{manifesto.politician_name}</span>
                    </div>
                    <div class="flex items-center gap-1 text-gray-500">
                      <Calendar class="w-4 h-4" />
                      <span>Voted {formatDate(manifesto.votedAt)}</span>
                    </div>
                  </div>
                </div>
                
                <div class="flex flex-col items-end gap-2">
                  <!-- My Vote Badge -->
                  <span class="inline-flex items-center gap-1 px-3 py-1.5 rounded-full text-sm font-medium border {getVoteColor(manifesto.myVote)}">
                    <svelte:component this={getVoteIcon(manifesto.myVote)} class="w-4 h-4" />
                    {manifesto.myVote === 'kept' ? 'Voted Kept' : 'Voted Broken'}
                  </span>
                  
                  <!-- Current Status -->
                  <span class="text-xs text-gray-500">
                    Current: {manifesto.status || 'pending'}
                  </span>
                </div>
              </div>
              
              <!-- Vote Comparison -->
              <div class="mt-4 pt-4 border-t border-gray-200">
                <div class="flex items-center justify-between text-sm">
                  <span class="text-gray-600">Community Consensus:</span>
                  <div class="flex items-center gap-4">
                    <span class="text-emerald-600">
                      {manifesto.vote_kept || 0} kept
                    </span>
                    <span class="text-red-600">
                      {manifesto.vote_broken || 0} broken
                    </span>
                  </div>
                </div>
                <div class="mt-2 h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div 
                    class="h-full bg-gradient-to-r from-emerald-500 to-emerald-400"
                    style="width: {keptPercent}%"
                  ></div>
                </div>
              </div>
            </div>
          {/each}
        </div>
      {/if}
      
      <!-- Nullifier Info -->
      <div class="mt-8 bg-white border border-gray-200 rounded-xl p-4">
        <div class="flex items-center gap-3 mb-2">
          <Hash class="w-5 h-5 text-gray-500" />
          <span class="text-gray-600 text-sm">Your Anonymous ID:</span>
          <code class="text-emerald-600 font-mono text-xs bg-gray-100 px-2 py-1 rounded">
            {userCredential?.nullifierShort || userCredential?.nullifier?.slice(0, 16) || 'N/A'}...
          </code>
        </div>
        <p class="text-gray-500 text-xs">
          This anonymous identifier prevents double voting without revealing your identity.
        </p>
      </div>
    {/if}
  </div>
</main>

<Footer />
