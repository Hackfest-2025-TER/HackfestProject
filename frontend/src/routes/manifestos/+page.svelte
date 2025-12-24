<script lang="ts">
  import { browser } from '$app/environment';
  import Header from '$lib/components/Header.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import { Search, Filter, Download, CheckCircle, Clock, FileText, ChevronLeft, ChevronRight, Shield, Fingerprint, AlertCircle, Vote } from 'lucide-svelte';
  import { onMount } from 'svelte';
  import { authStore, isAuthenticated, credential } from '$lib/stores';
  import { getManifestos, getMerkleRoot, getNetworkStats } from '$lib/api';
  
  // Reactive auth state
  $: isAuth = $isAuthenticated;
  $: userCredential = $credential;
  
  // Data state
  let manifestos: any[] = [];
  let networkStats: any = null;
  let merkleRoot = '';
  let isLoading = true;
  let error = '';
  
  let searchQuery = '';
  let statusFilter = 'all';
  
  // Load data on mount
  onMount(async () => {
    if (!browser) return;
    
    try {
      const [manifestoData, rootData, stats] = await Promise.all([
        getManifestos(),
        getMerkleRoot(),
        getNetworkStats()
      ]);
      
      manifestos = manifestoData.manifestos || [];
      merkleRoot = rootData.merkle_root;
      networkStats = stats;
    } catch (e) {
      error = 'Failed to load data. Please try again.';
      console.error(e);
    }
    isLoading = false;
  });
  
  // Check if grace period has passed for voting
  function canVote(manifesto: any): boolean {
    if (!manifesto.grace_period_end) return false;
    const graceEnd = new Date(manifesto.grace_period_end);
    return new Date() >= graceEnd;
  }
  
  // Get remaining time until voting opens
  function getTimeUntilVoting(manifesto: any): string {
    if (!manifesto.grace_period_end) return 'Unknown';
    const graceEnd = new Date(manifesto.grace_period_end);
    const now = new Date();
    
    if (now >= graceEnd) return 'Open';
    
    const diff = graceEnd.getTime() - now.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (days > 0) return `${days} days`;
    
    const hours = Math.floor(diff / (1000 * 60 * 60));
    return `${hours} hours`;
  }
  
  // Check if user has voted on this manifesto
  function hasVoted(manifestoId: string): boolean {
    return userCredential?.usedVotes?.includes(manifestoId) ?? false;
  }
  
  // Filter manifestos based on search and status
  $: filteredManifestos = manifestos.filter(m => {
    const matchesSearch = !searchQuery || 
      m.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      m.hash?.includes(searchQuery);
    const matchesStatus = statusFilter === 'all' || m.status === statusFilter;
    return matchesSearch && matchesStatus;
  });
</script>

<svelte:head>
  <title>Manifestos - PromiseThread</title>
</svelte:head>

<Header variant="default" />

<main class="manifestos-page">
  <div class="container">
    <div class="page-header">
      <h1>Political Promises</h1>
      <p>Track and evaluate political commitments. Vote anonymously when evaluation periods open.</p>
    </div>
    
    <!-- Auth Status Banner -->
    {#if isAuth}
      <div class="auth-banner verified">
        <div class="auth-info">
          <Shield size={20} />
          <div>
            <strong>Anonymous Credential Active</strong>
            <span>Nullifier: {userCredential?.nullifierShort}</span>
          </div>
        </div>
        <span class="votes-cast">
          <Vote size={14} />
          {userCredential?.usedVotes?.length || 0} votes cast
        </span>
      </div>
    {:else}
      <div class="auth-banner warning">
        <div class="auth-info">
          <AlertCircle size={20} />
          <div>
            <strong>Not Verified</strong>
            <span>Generate a ZK credential to vote on promises</span>
          </div>
        </div>
        <a href="/auth" class="verify-btn">
          <Fingerprint size={16} />
          Verify Identity
        </a>
      </div>
    {/if}
    
    <!-- Stats -->
    <div class="stats-grid">
      <div class="stat-card card">
        <div class="stat-header">
          <span class="stat-label">Total Promises</span>
          <FileText size={20} />
        </div>
        <div class="stat-value">{manifestos.length}</div>
        <div class="stat-trend positive">From verified politicians</div>
      </div>
      
      <div class="stat-card card">
        <div class="stat-header">
          <span class="stat-label">Voter Registry</span>
          <Shield size={20} />
        </div>
        <div class="stat-value">{networkStats?.total_votes?.toLocaleString() || '...'}</div>
        <div class="stat-meta">
          <Fingerprint size={14} />
          Total votes recorded
        </div>
      </div>
      
      <div class="stat-card card">
        <div class="stat-header">
          <span class="stat-label">ZK Integrity Score</span>
        </div>
        <div class="stat-value">{networkStats?.integrity_score || 99.97}%</div>
        <div class="integrity-bar">
          <div class="integrity-fill" style="width: {networkStats?.integrity_score || 99.97}%"></div>
        </div>
      </div>
    </div>
    
    <!-- Search & Filter -->
    <div class="toolbar card">
      <div class="search-box">
        <Search size={18} />
        <input 
          type="text" 
          placeholder="Search by title or Merkle root hash (0x...)" 
          bind:value={searchQuery}
        />
      </div>
      <div class="toolbar-actions">
        <button class="btn btn-secondary">
          <Filter size={16} />
          Filter
        </button>
        <button class="btn btn-secondary">
          <Download size={16} />
          Export
        </button>
      </div>
    </div>
    
    <!-- Manifestos Table -->
    <div class="table-card card">
      {#if isLoading}
        <div class="loading-state">
          <div class="spinner"></div>
          <p>Loading promises...</p>
        </div>
      {:else if error}
        <div class="error-state">
          <AlertCircle size={24} />
          <p>{error}</p>
        </div>
      {:else}
        <table class="manifestos-table">
          <thead>
            <tr>
              <th>PROMISE</th>
              <th>CATEGORY</th>
              <th>STATUS</th>
              <th>VOTES</th>
              <th>VOTING</th>
              <th>ACTIONS</th>
            </tr>
          </thead>
          <tbody>
            {#each filteredManifestos as manifesto}
              <tr>
                <td class="title-cell">
                  <div class="title-content">
                    <span class="title">{manifesto.title}</span>
                    <span class="politician-name">by {manifesto.politician_name}</span>
                  </div>
                </td>
                <td>
                  <span class="category-badge">{manifesto.category}</span>
                </td>
                <td>
                  <span class="status-badge {manifesto.status}">
                    {#if manifesto.status === 'kept'}
                      <CheckCircle size={12} /> Kept
                    {:else if manifesto.status === 'broken'}
                      <AlertCircle size={12} /> Broken
                    {:else}
                      <Clock size={12} /> Pending
                    {/if}
                  </span>
                </td>
                <td class="votes-cell">
                  <div class="vote-bars">
                    <div class="vote-bar kept" style="width: {manifesto.vote_kept / (manifesto.vote_kept + manifesto.vote_broken + 1) * 100}%"></div>
                    <div class="vote-bar broken" style="width: {manifesto.vote_broken / (manifesto.vote_kept + manifesto.vote_broken + 1) * 100}%"></div>
                  </div>
                  <span class="vote-counts">
                    <span class="kept">{manifesto.vote_kept}</span> / 
                    <span class="broken">{manifesto.vote_broken}</span>
                  </span>
                </td>
                <td>
                  {#if canVote(manifesto)}
                    {#if hasVoted(manifesto.id)}
                      <span class="voted-badge">
                        <CheckCircle size={12} /> Voted
                      </span>
                    {:else if isAuth}
                      <a href="/citizen/attestation?id={manifesto.id}" class="vote-btn">
                        <Vote size={14} /> Vote
                      </a>
                    {:else}
                      <span class="login-to-vote">Login to vote</span>
                    {/if}
                  {:else}
                    <span class="grace-period">
                      <Clock size={12} />
                      Opens in {getTimeUntilVoting(manifesto)}
                    </span>
                  {/if}
                </td>
                <td class="actions-cell">
                  <a href="/manifestos/{manifesto.id}" class="action-link">
                    View Details
                  </a>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      {/if}
      
      <div class="table-footer">
        <span class="showing">Showing {filteredManifestos.length} of {manifestos.length} promises</span>
        <div class="merkle-info">
          <Fingerprint size={14} />
          Registry Root: {merkleRoot ? merkleRoot.slice(0, 12) + '...' : 'Loading...'}
        </div>
      </div>
    </div>
  </div>
  
  <!-- Footer Status Bar -->
  <div class="status-bar">
    <div class="status-item">
      <span class="status-dot online"></span>
      BLOCK HEIGHT: 19,230,442
    </div>
    <div class="status-item">
      SESSION ID: 0x992...fa21
    </div>
    <div class="status-item right">
      <CheckCircle size={14} />
      Secured by Politician Protocol v2.1
    </div>
  </div>
</main>

<Footer />

<style>
  .manifestos-page {
    min-height: 100vh;
    background: var(--gray-50);
  }
  
  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: var(--space-8) var(--space-4);
  }
  
  .page-header {
    margin-bottom: var(--space-6);
  }
  
  .page-header h1 {
    font-size: 1.75rem;
    margin-bottom: var(--space-2);
  }
  
  .page-header p {
    color: var(--gray-500);
  }
  
  /* Auth Banner */
  .auth-banner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-4);
    border-radius: var(--radius-lg);
    margin-bottom: var(--space-6);
  }
  
  .auth-banner.verified {
    background: var(--success-50);
    border: 1px solid var(--success-200);
  }
  
  .auth-banner.warning {
    background: var(--warning-50);
    border: 1px solid var(--warning-200);
  }
  
  .auth-info {
    display: flex;
    align-items: center;
    gap: var(--space-3);
  }
  
  .auth-banner.verified .auth-info :global(svg) {
    color: var(--success-600);
  }
  
  .auth-banner.warning .auth-info :global(svg) {
    color: var(--warning-600);
  }
  
  .auth-info strong {
    display: block;
    color: var(--gray-900);
  }
  
  .auth-info span {
    font-size: 0.875rem;
    color: var(--gray-600);
    font-family: var(--font-mono);
  }
  
  .votes-cast {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    font-size: 0.875rem;
    color: var(--success-700);
  }
  
  .verify-btn {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-2) var(--space-4);
    background: var(--primary-600);
    color: white;
    border-radius: var(--radius-md);
    text-decoration: none;
    font-weight: 500;
    font-size: 0.875rem;
  }
  
  .verify-btn:hover {
    background: var(--primary-700);
  }
  
  .stats-grid {
    display: grid;
    gap: var(--space-4);
    margin-bottom: var(--space-6);
  }
  
  @media (min-width: 768px) {
    .stats-grid {
      grid-template-columns: repeat(3, 1fr);
    }
  }
  
  .stat-card {
    padding: var(--space-5);
  }
  
  .stat-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--space-3);
    color: var(--gray-400);
  }
  
  .stat-label {
    font-size: 0.875rem;
    color: var(--gray-500);
  }
  
  .stat-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--gray-900);
    margin-bottom: var(--space-2);
  }
  
  .stat-trend {
    font-size: 0.75rem;
    font-weight: 500;
  }
  
  .stat-trend.positive {
    color: var(--success-600);
  }
  
  .integrity-bar {
    height: 6px;
    background: var(--gray-200);
    border-radius: var(--radius-full);
    overflow: hidden;
  }
  
  .integrity-fill {
    height: 100%;
    background: var(--success-500);
    border-radius: var(--radius-full);
  }
  
  .stat-meta {
    display: flex;
    align-items: center;
    gap: var(--space-1);
    font-size: 0.75rem;
    color: var(--primary-600);
  }
  
  .toolbar {
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
    padding: var(--space-4);
    margin-bottom: var(--space-4);
  }
  
  @media (min-width: 640px) {
    .toolbar {
      flex-direction: row;
      justify-content: space-between;
      align-items: center;
    }
  }
  
  .search-box {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    flex: 1;
    max-width: 500px;
    padding: var(--space-2) var(--space-3);
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-lg);
    background: var(--gray-50);
  }
  
  .search-box :global(svg) {
    color: var(--gray-400);
  }
  
  .search-box input {
    flex: 1;
    border: none;
    background: transparent;
    font-size: 0.875rem;
    outline: none;
  }
  
  .toolbar-actions {
    display: flex;
    gap: var(--space-2);
  }
  
  .table-card {
    overflow: hidden;
    background: white;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-sm);
  }
  
  .loading-state,
  .error-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: var(--space-12);
    color: var(--gray-500);
  }
  
  .spinner {
    width: 32px;
    height: 32px;
    border: 3px solid var(--gray-200);
    border-top-color: var(--primary-500);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: var(--space-3);
  }
  
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
  
  .manifestos-table {
    width: 100%;
    border-collapse: collapse;
  }
  
  .manifestos-table th {
    text-align: left;
    padding: var(--space-4);
    font-size: 0.7rem;
    font-weight: 600;
    color: var(--gray-500);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    border-bottom: 1px solid var(--gray-200);
    background: var(--gray-50);
  }
  
  .manifestos-table td {
    padding: var(--space-4);
    border-bottom: 1px solid var(--gray-100);
    font-size: 0.875rem;
  }
  
  .title-cell {
    max-width: 280px;
  }
  
  .title-content {
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
  }
  
  .title {
    font-weight: 600;
    color: var(--gray-900);
  }
  
  .politician-name {
    font-size: 0.75rem;
    color: var(--gray-500);
  }
  
  .category-badge {
    display: inline-block;
    padding: var(--space-1) var(--space-2);
    background: var(--gray-100);
    border-radius: var(--radius-md);
    font-size: 0.75rem;
    font-weight: 500;
    color: var(--gray-600);
  }
  
  .status-badge {
    display: inline-flex;
    align-items: center;
    gap: var(--space-1);
    padding: var(--space-1) var(--space-2);
    border-radius: var(--radius-md);
    font-size: 0.75rem;
    font-weight: 500;
  }
  
  .status-badge.kept {
    background: var(--success-100);
    color: var(--success-700);
  }
  
  .status-badge.broken {
    background: var(--error-100);
    color: var(--error-700);
  }
  
  .status-badge.pending {
    background: var(--warning-100);
    color: var(--warning-700);
  }
  
  .votes-cell {
    min-width: 120px;
  }
  
  .vote-bars {
    display: flex;
    height: 6px;
    background: var(--gray-200);
    border-radius: var(--radius-full);
    overflow: hidden;
    margin-bottom: var(--space-1);
  }
  
  .vote-bar.kept {
    background: var(--success-500);
  }
  
  .vote-bar.broken {
    background: var(--error-500);
  }
  
  .vote-counts {
    font-size: 0.75rem;
    color: var(--gray-500);
  }
  
  .vote-counts .kept {
    color: var(--success-600);
  }
  
  .vote-counts .broken {
    color: var(--error-600);
  }
  
  .voted-badge {
    display: inline-flex;
    align-items: center;
    gap: var(--space-1);
    color: var(--success-600);
    font-size: 0.75rem;
    font-weight: 500;
  }
  
  .vote-btn {
    display: inline-flex;
    align-items: center;
    gap: var(--space-1);
    padding: var(--space-1) var(--space-3);
    background: var(--primary-600);
    color: white;
    border-radius: var(--radius-md);
    font-size: 0.75rem;
    font-weight: 500;
    text-decoration: none;
  }
  
  .vote-btn:hover {
    background: var(--primary-700);
  }
  
  .login-to-vote {
    font-size: 0.75rem;
    color: var(--gray-400);
    font-style: italic;
  }
  
  .grace-period {
    display: inline-flex;
    align-items: center;
    gap: var(--space-1);
    font-size: 0.75rem;
    color: var(--warning-600);
  }
  
  .actions-cell {
    display: flex;
    gap: var(--space-3);
  }
  
  .action-link {
    font-size: 0.8rem;
    color: var(--primary-600);
    text-decoration: none;
  }
  
  .action-link:hover {
    text-decoration: underline;
  }
  
  .table-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-4);
    background: var(--gray-50);
    border-top: 1px solid var(--gray-200);
  }
  
  .showing {
    font-size: 0.8rem;
    color: var(--gray-500);
  }
  
  .merkle-info {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    font-family: var(--font-mono);
    font-size: 0.75rem;
    color: var(--gray-400);
  }
  
  .status-bar {
    display: flex;
    align-items: center;
    gap: var(--space-6);
    padding: var(--space-3) var(--space-6);
    background: var(--gray-900);
    color: white;
    font-family: var(--font-mono);
    font-size: 0.75rem;
  }
  
  .status-item {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    color: var(--gray-400);
  }
  
  .status-item .status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
  }
  
  .status-item .status-dot.online {
    background: var(--success-500);
  }
  
  .status-item.right {
    margin-left: auto;
    color: var(--gray-500);
  }
  
  .status-item.right :global(svg) {
    color: var(--success-500);
  }
</style>
