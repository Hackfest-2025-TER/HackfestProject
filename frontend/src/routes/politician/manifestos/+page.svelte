<script lang="ts">
  import Header from '$lib/components/Header.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import { 
    FileText, Plus, Clock, CheckCircle, XCircle, Eye, 
    Filter, Search, Calendar, TrendingUp, ChevronRight,
    Hash, Shield, BarChart
  } from 'lucide-svelte';
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { getManifestos } from '$lib/api';
  
  // Politician session (in production, get from auth)
  let politicianSession: any = null;
  let manifestos: any[] = [];
  let isLoading = true;
  let error = '';
  
  // Filters
  let statusFilter = 'all';
  let searchQuery = '';
  
  onMount(async () => {
    // Check if logged in
    const session = localStorage.getItem('politician_session');
    if (!session) {
      goto('/politician/login');
      return;
    }
    politicianSession = JSON.parse(session);
    
    await loadManifestos();
  });
  
  async function loadManifestos() {
    try {
      isLoading = true;
      const data = await getManifestos({ politician_id: politicianSession?.id });
      manifestos = data.manifestos || [];
    } catch (e: any) {
      error = e.message;
    } finally {
      isLoading = false;
    }
  }
  
  // Filter manifestos
  $: filteredManifestos = manifestos.filter(m => {
    const matchesStatus = statusFilter === 'all' || m.status === statusFilter;
    const matchesSearch = !searchQuery || 
      m.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      m.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesStatus && matchesSearch;
  });
  
  // Stats
  $: stats = {
    total: manifestos.length,
    pending: manifestos.filter(m => m.status === 'pending').length,
    kept: manifestos.filter(m => m.status === 'kept').length,
    broken: manifestos.filter(m => m.status === 'broken').length
  };
  
  function getStatusColor(status: string) {
    switch (status) {
      case 'kept': return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20';
      case 'broken': return 'text-red-400 bg-red-500/10 border-red-500/20';
      default: return 'text-amber-400 bg-amber-500/10 border-amber-500/20';
    }
  }
  
  function getStatusIcon(status: string) {
    switch (status) {
      case 'kept': return CheckCircle;
      case 'broken': return XCircle;
      default: return Clock;
    }
  }
  
  function formatDate(dateStr: string) {
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  }
</script>

<svelte:head>
  <title>My Manifestos - PromiseThread</title>
</svelte:head>

<Header />

<main class="min-h-screen bg-gray-50 py-8">
  <div class="max-w-6xl mx-auto px-4">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8">
      <div>
        <h1 class="text-3xl font-bold text-white mb-2">My Manifestos</h1>
        <p class="text-slate-400">
          {#if politicianSession}
            Manage your commitments as {politicianSession.name}
          {:else}
            Loading...
          {/if}
        </p>
      </div>
      <a 
        href="/politician/new-manifesto"
        class="inline-flex items-center gap-2 bg-emerald-500 hover:bg-emerald-600 text-white px-5 py-3 rounded-lg transition-colors font-medium"
      >
        <Plus class="w-5 h-5" />
        New Manifesto
      </a>
    </div>
    
    <!-- Stats Cards -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
      <div class="bg-slate-800/50 border border-slate-700 rounded-xl p-4">
        <div class="flex items-center gap-3 mb-2">
          <FileText class="w-5 h-5 text-blue-400" />
          <span class="text-slate-400 text-sm">Total</span>
        </div>
        <div class="text-2xl font-bold text-white">{stats.total}</div>
      </div>
      <div class="bg-slate-800/50 border border-slate-700 rounded-xl p-4">
        <div class="flex items-center gap-3 mb-2">
          <Clock class="w-5 h-5 text-amber-400" />
          <span class="text-slate-400 text-sm">Pending</span>
        </div>
        <div class="text-2xl font-bold text-white">{stats.pending}</div>
      </div>
      <div class="bg-slate-800/50 border border-slate-700 rounded-xl p-4">
        <div class="flex items-center gap-3 mb-2">
          <CheckCircle class="w-5 h-5 text-emerald-400" />
          <span class="text-slate-400 text-sm">Kept</span>
        </div>
        <div class="text-2xl font-bold text-white">{stats.kept}</div>
      </div>
      <div class="bg-slate-800/50 border border-slate-700 rounded-xl p-4">
        <div class="flex items-center gap-3 mb-2">
          <XCircle class="w-5 h-5 text-red-400" />
          <span class="text-slate-400 text-sm">Broken</span>
        </div>
        <div class="text-2xl font-bold text-white">{stats.broken}</div>
      </div>
    </div>
    
    <!-- Filters -->
    <div class="bg-slate-800/50 border border-slate-700 rounded-xl p-4 mb-6">
      <div class="flex flex-col md:flex-row gap-4">
        <!-- Search -->
        <div class="flex-1 relative">
          <Search class="w-5 h-5 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            bind:value={searchQuery}
            placeholder="Search manifestos..."
            class="w-full bg-slate-900/50 border border-slate-600 rounded-lg pl-10 pr-4 py-2 text-white placeholder-slate-500 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 outline-none"
          />
        </div>
        
        <!-- Status Filter -->
        <div class="flex items-center gap-2">
          <Filter class="w-5 h-5 text-slate-500" />
          <select
            bind:value={statusFilter}
            class="bg-slate-900/50 border border-slate-600 rounded-lg px-3 py-2 text-white focus:border-emerald-500 outline-none"
          >
            <option value="all">All Status</option>
            <option value="pending">Pending</option>
            <option value="kept">Kept</option>
            <option value="broken">Broken</option>
          </select>
        </div>
      </div>
    </div>
    
    <!-- Manifestos List -->
    {#if isLoading}
      <div class="text-center py-12">
        <div class="w-8 h-8 border-2 border-emerald-500/30 border-t-emerald-500 rounded-full animate-spin mx-auto mb-4"></div>
        <p class="text-slate-400">Loading your manifestos...</p>
      </div>
    {:else if error}
      <div class="bg-red-500/10 border border-red-500/20 rounded-xl p-6 text-center">
        <XCircle class="w-8 h-8 text-red-400 mx-auto mb-2" />
        <p class="text-red-400">{error}</p>
      </div>
    {:else if filteredManifestos.length === 0}
      <div class="bg-slate-800/50 border border-slate-700 rounded-xl p-12 text-center">
        <FileText class="w-12 h-12 text-slate-600 mx-auto mb-4" />
        <h3 class="text-xl font-semibold text-white mb-2">No manifestos found</h3>
        <p class="text-slate-400 mb-6">
          {manifestos.length === 0 
            ? "You haven't created any manifestos yet." 
            : "No manifestos match your filters."}
        </p>
        {#if manifestos.length === 0}
          <a 
            href="/politician/new-manifesto"
            class="inline-flex items-center gap-2 bg-emerald-500 hover:bg-emerald-600 text-white px-5 py-3 rounded-lg transition-colors"
          >
            <Plus class="w-5 h-5" />
            Create Your First Manifesto
          </a>
        {/if}
      </div>
    {:else}
      <div class="space-y-4">
        {#each filteredManifestos as manifesto}
          <a 
            href="/manifestos/{manifesto.id}"
            class="block bg-slate-800/50 border border-slate-700 rounded-xl p-6 hover:border-emerald-500/50 transition-all group"
          >
            <div class="flex items-start justify-between gap-4">
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-3 mb-2">
                  <h3 class="text-lg font-semibold text-white truncate group-hover:text-emerald-400 transition-colors">
                    {manifesto.title}
                  </h3>
                  <span class="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium border {getStatusColor(manifesto.status)}">
                    <svelte:component this={getStatusIcon(manifesto.status)} class="w-3 h-3" />
                    {manifesto.status}
                  </span>
                </div>
                
                <p class="text-slate-400 text-sm line-clamp-2 mb-4">
                  {manifesto.description}
                </p>
                
                <div class="flex flex-wrap items-center gap-4 text-sm">
                  <div class="flex items-center gap-1 text-slate-500">
                    <Calendar class="w-4 h-4" />
                    <span>{formatDate(manifesto.created_at)}</span>
                  </div>
                  <div class="flex items-center gap-1 text-slate-500">
                    <span class="px-2 py-0.5 bg-slate-700 rounded text-xs">{manifesto.category}</span>
                  </div>
                  {#if manifesto.hash}
                    <div class="flex items-center gap-1 text-slate-500">
                      <Hash class="w-4 h-4" />
                      <span class="font-mono text-xs">{manifesto.hash.slice(0, 10)}...</span>
                    </div>
                  {/if}
                  <div class="flex items-center gap-2 text-slate-500">
                    <TrendingUp class="w-4 h-4" />
                    <span>
                      {manifesto.vote_kept || 0} kept / {manifesto.vote_broken || 0} broken
                    </span>
                  </div>
                </div>
              </div>
              
              <ChevronRight class="w-5 h-5 text-slate-600 group-hover:text-emerald-400 transition-colors flex-shrink-0" />
            </div>
          </a>
        {/each}
      </div>
    {/if}
    
    <!-- Quick Actions -->
    <div class="mt-8 grid md:grid-cols-3 gap-4">
      <a 
        href="/politician/wallet"
        class="bg-slate-800/50 border border-slate-700 rounded-xl p-4 hover:border-blue-500/50 transition-all group"
      >
        <Shield class="w-6 h-6 text-blue-400 mb-2" />
        <h3 class="text-white font-medium group-hover:text-blue-400 transition-colors">Wallet & Keys</h3>
        <p class="text-slate-500 text-sm">Manage your signing keys</p>
      </a>
      <a 
        href="/politician/dashboard"
        class="bg-slate-800/50 border border-slate-700 rounded-xl p-4 hover:border-emerald-500/50 transition-all group"
      >
        <BarChart class="w-6 h-6 text-emerald-400 mb-2" />
        <h3 class="text-white font-medium group-hover:text-emerald-400 transition-colors">Dashboard</h3>
        <p class="text-slate-500 text-sm">View analytics and insights</p>
      </a>
      <a 
        href="/politician/profile"
        class="bg-slate-800/50 border border-slate-700 rounded-xl p-4 hover:border-purple-500/50 transition-all group"
      >
        <Eye class="w-6 h-6 text-purple-400 mb-2" />
        <h3 class="text-white font-medium group-hover:text-purple-400 transition-colors">Public Profile</h3>
        <p class="text-slate-500 text-sm">See how citizens view you</p>
      </a>
    </div>
  </div>
</main>

<Footer />
