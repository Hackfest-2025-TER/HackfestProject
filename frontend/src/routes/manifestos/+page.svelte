<script lang="ts">
  import { browser } from '$app/environment';
  import Header from '$lib/components/Header.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import { Search, CheckCircle, Clock, FileText, Shield, AlertCircle, Users, MessageCircle, ChevronRight, Info, ExternalLink } from 'lucide-svelte';
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
      
      manifestos = (manifestoData.manifestos || []) as any[];
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
  
  // Get human-readable status
  function getStatusLabel(status: string): string {
    switch(status) {
      case 'kept': return 'Being Kept';
      case 'broken': return 'Not Being Kept';
      default: return 'Under Review';
    }
  }
  
  // Get citizen feedback text
  function getFeedbackText(kept: number, broken: number): string {
    const total = kept + broken;
    if (total === 0) return 'No feedback yet';
    const keptPercent = (kept / total) * 100;
    if (keptPercent >= 70) return 'Most citizens say this is being kept';
    if (keptPercent >= 50) return 'Citizens are divided on this promise';
    if (keptPercent >= 30) return 'Many citizens say this is not being kept';
    return 'Most citizens say this is not being kept';
  }
  
  // Filter manifestos based on search and status
  $: filteredManifestos = manifestos.filter(m => {
    const matchesSearch = !searchQuery || 
      m.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      m.category?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || m.status === statusFilter;
    return matchesSearch && matchesStatus;
  });
</script>

<svelte:head>
  <title>Election Promises - PromiseThread</title>
</svelte:head>

<Header variant="default" />

<main class="manifestos-page">
  <div class="container">
    <!-- Page Header -->
    <div class="page-header">
      <h1>Election Promises</h1>
      <p>Browse official election promises published by political parties. These promises cannot be changed after publication.</p>
    </div>
    
    <!-- Auth Status Banner - Soft, non-blocking -->
    {#if isAuth}
      <div class="auth-banner verified">
        <div class="auth-info">
          <Shield size={20} />
          <div>
            <strong>You're verified</strong>
            <span>You can share your opinion anonymously</span>
          </div>
        </div>
        <span class="opinions-shared">
          <MessageCircle size={14} />
          {userCredential?.usedVotes?.length || 0} opinions shared
        </span>
      </div>
    {:else}
      <div class="auth-banner info">
        <div class="auth-info">
          <Info size={20} />
          <div>
            <strong>Want to share your opinion?</strong>
            <span>Verify once to participate anonymously</span>
          </div>
        </div>
        <a href="/auth" class="verify-btn">
          Verify as Citizen
        </a>
      </div>
    {/if}
    
    <!-- Stats - Simplified -->
    <div class="stats-grid">
      <div class="stat-card card">
        <div class="stat-header">
          <span class="stat-label">Total Promises</span>
          <FileText size={20} />
        </div>
        <div class="stat-value">{manifestos.length}</div>
        <div class="stat-trend">From all political parties</div>
      </div>
      
      <div class="stat-card card">
        <div class="stat-header">
          <span class="stat-label">Citizen Opinions</span>
          <Users size={20} />
        </div>
        <div class="stat-value">{networkStats?.total_votes?.toLocaleString() || '...'}</div>
        <div class="stat-trend">Total feedback received</div>
      </div>
      
      <div class="stat-card card">
        <div class="stat-header">
          <span class="stat-label">System Trust Score</span>
          <Shield size={20} />
        </div>
        <div class="stat-value">{networkStats?.integrity_score || 99.97}%</div>
        <div class="integrity-bar">
          <div class="integrity-fill" style="width: {networkStats?.integrity_score || 99.97}%"></div>
        </div>
      </div>
    </div>
    
    <!-- Search & Filter - Simplified -->
    <div class="toolbar card">
      <div class="search-box">
        <Search size={18} />
        <input 
          type="text" 
          placeholder="Search promises by keyword (e.g. health, roads, education)" 
          bind:value={searchQuery}
        />
      </div>
      <div class="filter-tabs">
        <button 
          class="filter-tab" 
          class:active={statusFilter === 'all'}
          on:click={() => statusFilter = 'all'}
        >
          All Promises
        </button>
        <button 
          class="filter-tab kept" 
          class:active={statusFilter === 'kept'}
          on:click={() => statusFilter = 'kept'}
        >
          Being Kept
        </button>
        <button 
          class="filter-tab broken" 
          class:active={statusFilter === 'broken'}
          on:click={() => statusFilter = 'broken'}
        >
          Not Being Kept
        </button>
        <button 
          class="filter-tab pending" 
          class:active={statusFilter === 'pending'}
          on:click={() => statusFilter = 'pending'}
        >
          Under Review
        </button>
      </div>
    </div>
    
    <!-- Promise Cards -->
    <div class="promises-section">
      {#if isLoading}
        <div class="loading-state card">
          <div class="spinner"></div>
          <p>Loading promises...</p>
        </div>
      {:else if error}
        <div class="error-state card">
          <AlertCircle size={32} />
          <p>{error}</p>
          <button class="btn btn-primary" on:click={() => location.reload()}>Try Again</button>
        </div>
      {:else if filteredManifestos.length === 0}
        <div class="empty-state card">
          <FileText size={32} />
          <p>No promises found matching your search.</p>
        </div>
      {:else}
        <div class="promises-grid">
          {#each filteredManifestos as manifesto}
            <div class="promise-card card">
              <!-- Header: Party / Category -->
              <div class="promise-header">
                <span class="promise-party">{manifesto.politician_name || 'Political Party'}</span>
                <span class="promise-category">{manifesto.category}</span>
              </div>
              
              <!-- Title -->
              <h3 class="promise-title">{manifesto.title}</h3>
              
              <!-- Status Badge -->
              <div class="promise-status {manifesto.status}">
                {#if manifesto.status === 'kept'}
                  <CheckCircle size={16} />
                {:else if manifesto.status === 'broken'}
                  <AlertCircle size={16} />
                {:else}
                  <Clock size={16} />
                {/if}
                <span>Promise Status: {getStatusLabel(manifesto.status)}</span>
              </div>
              
              <!-- Citizen Feedback -->
              <div class="citizen-feedback">
                <span class="feedback-label">Citizen Feedback:</span>
                <div class="feedback-bar">
                  <div 
                    class="feedback-fill kept" 
                    style="width: {manifesto.vote_kept / (manifesto.vote_kept + manifesto.vote_broken + 1) * 100}%"
                  ></div>
                </div>
                <span class="feedback-text">{getFeedbackText(manifesto.vote_kept, manifesto.vote_broken)}</span>
              </div>
              
              <!-- Actions -->
              <div class="promise-actions">
                <a href="/manifestos/{manifesto.id}" class="btn-view">
                  View Details
                  <ChevronRight size={16} />
                </a>
                
                {#if canVote(manifesto)}
                  {#if hasVoted(manifesto.id)}
                    <span class="already-shared">
                      <CheckCircle size={14} />
                      Opinion shared
                    </span>
                  {:else if isAuth}
                    <a href="/citizen/attestation?id={manifesto.id}" class="btn-opinion">
                      Share Opinion
                    </a>
                  {:else}
                    <a href="/auth" class="btn-opinion-disabled">
                      Share Opinion
                    </a>
                  {/if}
                {:else}
                  <span class="voting-opens">
                    <Clock size={14} />
                    Opens in {getTimeUntilVoting(manifesto)}
                  </span>
                {/if}
              </div>
              
              <!-- Privacy note (shown on hover or small text) -->
              <p class="privacy-note">No name. No public identity.</p>
            </div>
          {/each}
        </div>
      {/if}
      
      <!-- Results count -->
      <div class="results-info">
        <span>Showing {filteredManifestos.length} of {manifestos.length} promises</span>
      </div>
    </div>
  </div>
  
  <!-- Footer Status Bar - Simplified -->
  <div class="status-bar">
    <div class="status-left">
      <span class="status-dot"></span>
      <span>Data secured and publicly verifiable</span>
    </div>
    <div class="status-right">
      <span class="system-status">System status: Active</span>
      <a href="/about" class="learn-more">
        <Info size={14} />
        Learn how data is secured
      </a>
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
  
  /* Page Header */
  .page-header {
    margin-bottom: var(--space-6);
  }
  
  .page-header h1 {
    font-size: 2rem;
    margin-bottom: var(--space-2);
    color: #082770;
  }
  
  .page-header p {
    color: var(--gray-600);
    font-size: 1.1rem;
    max-width: 600px;
  }
  
  /* Auth Banner - Softer, info style */
  .auth-banner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-4) var(--space-5);
    border-radius: var(--radius-lg);
    margin-bottom: var(--space-6);
    flex-wrap: wrap;
    gap: var(--space-4);
  }
  
  .auth-banner.verified {
    background: var(--success-50);
    border: 1px solid var(--success-200);
  }
  
  .auth-banner.info {
    background: #e8f4fc;
    border: 1px solid #b3d4fc;
  }
  
  .auth-info {
    display: flex;
    align-items: center;
    gap: var(--space-3);
  }
  
  .auth-banner.verified .auth-info :global(svg) {
    color: var(--success-600);
  }
  
  .auth-banner.info .auth-info :global(svg) {
    color: #082770;
  }
  
  .auth-info strong {
    display: block;
    color: var(--gray-900);
    font-size: 0.95rem;
  }
  
  .auth-info span {
    font-size: 0.875rem;
    color: var(--gray-600);
  }
  
  .opinions-shared {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    font-size: 0.875rem;
    color: var(--success-700);
    font-weight: 500;
  }
  
  .verify-btn {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-3) var(--space-5);
    background: #082770;
    color: white;
    border-radius: var(--radius-lg);
    text-decoration: none;
    font-weight: 600;
    font-size: 0.9rem;
    transition: all 0.2s;
  }
  
  .verify-btn:hover {
    background: #0a3490;
    transform: translateY(-1px);
  }
  
  /* Stats Grid */
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
    font-size: 0.8rem;
    color: var(--gray-500);
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
  
  /* Toolbar */
  .toolbar {
    padding: var(--space-4);
    margin-bottom: var(--space-6);
  }
  
  .search-box {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-3) var(--space-4);
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-lg);
    background: var(--gray-50);
    margin-bottom: var(--space-4);
  }
  
  .search-box :global(svg) {
    color: var(--gray-400);
    flex-shrink: 0;
  }
  
  .search-box input {
    flex: 1;
    border: none;
    background: transparent;
    font-size: 0.9rem;
    outline: none;
  }
  
  .filter-tabs {
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-2);
  }
  
  .filter-tab {
    padding: var(--space-2) var(--space-4);
    background: white;
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-full);
    font-size: 0.85rem;
    color: var(--gray-600);
    cursor: pointer;
    transition: all 0.2s;
  }
  
  .filter-tab:hover {
    border-color: var(--gray-300);
    background: var(--gray-50);
  }
  
  .filter-tab.active {
    background: #082770;
    color: white;
    border-color: #082770;
  }
  
  .filter-tab.kept.active {
    background: var(--success-600);
    border-color: var(--success-600);
  }
  
  .filter-tab.broken.active {
    background: var(--error-600);
    border-color: var(--error-600);
  }
  
  .filter-tab.pending.active {
    background: var(--warning-600);
    border-color: var(--warning-600);
  }
  
  /* Promises Grid */
  .promises-grid {
    display: grid;
    gap: var(--space-5);
  }
  
  @media (min-width: 768px) {
    .promises-grid {
      grid-template-columns: repeat(2, 1fr);
    }
  }
  
  @media (min-width: 1024px) {
    .promises-grid {
      grid-template-columns: repeat(3, 1fr);
    }
  }
  
  /* Promise Card */
  .promise-card {
    padding: var(--space-5);
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
    transition: all 0.2s;
    border: 1px solid var(--gray-100);
  }
  
  .promise-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
  }
  
  .promise-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: var(--space-2);
    flex-wrap: wrap;
  }
  
  .promise-party {
    font-size: 0.8rem;
    color: var(--gray-500);
    font-weight: 500;
  }
  
  .promise-category {
    font-size: 0.7rem;
    padding: var(--space-1) var(--space-2);
    background: var(--gray-100);
    color: var(--gray-600);
    border-radius: var(--radius-md);
    text-transform: capitalize;
  }
  
  .promise-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--gray-900);
    line-height: 1.4;
    margin: 0;
  }
  
  /* Status Badge */
  .promise-status {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-2) var(--space-3);
    border-radius: var(--radius-md);
    font-size: 0.85rem;
    font-weight: 500;
  }
  
  .promise-status.kept {
    background: var(--success-100);
    color: var(--success-700);
  }
  
  .promise-status.broken {
    background: var(--error-100);
    color: var(--error-700);
  }
  
  .promise-status.pending {
    background: var(--warning-100);
    color: var(--warning-700);
  }
  
  /* Citizen Feedback */
  .citizen-feedback {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
  }
  
  .feedback-label {
    font-size: 0.8rem;
    color: var(--gray-500);
    font-weight: 500;
  }
  
  .feedback-bar {
    height: 8px;
    background: var(--gray-200);
    border-radius: var(--radius-full);
    overflow: hidden;
  }
  
  .feedback-fill.kept {
    height: 100%;
    background: linear-gradient(90deg, var(--success-500), var(--success-400));
    border-radius: var(--radius-full);
  }
  
  .feedback-text {
    font-size: 0.8rem;
    color: var(--gray-600);
    font-style: italic;
  }
  
  /* Promise Actions */
  .promise-actions {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    flex-wrap: wrap;
    margin-top: auto;
  }
  
  .btn-view {
    display: flex;
    align-items: center;
    gap: var(--space-1);
    padding: var(--space-2) var(--space-3);
    background: white;
    color: #082770;
    border: 1px solid #082770;
    border-radius: var(--radius-md);
    font-size: 0.85rem;
    font-weight: 500;
    text-decoration: none;
    transition: all 0.2s;
  }
  
  .btn-view:hover {
    background: #082770;
    color: white;
  }
  
  .btn-opinion {
    padding: var(--space-2) var(--space-3);
    background: #082770;
    color: white;
    border-radius: var(--radius-md);
    font-size: 0.85rem;
    font-weight: 500;
    text-decoration: none;
    transition: all 0.2s;
  }
  
  .btn-opinion:hover {
    background: #0a3490;
  }
  
  .btn-opinion-disabled {
    padding: var(--space-2) var(--space-3);
    background: var(--gray-200);
    color: var(--gray-500);
    border-radius: var(--radius-md);
    font-size: 0.85rem;
    font-weight: 500;
    text-decoration: none;
  }
  
  .already-shared {
    display: flex;
    align-items: center;
    gap: var(--space-1);
    font-size: 0.8rem;
    color: var(--success-600);
    font-weight: 500;
  }
  
  .voting-opens {
    display: flex;
    align-items: center;
    gap: var(--space-1);
    font-size: 0.8rem;
    color: var(--warning-600);
  }
  
  .privacy-note {
    font-size: 0.7rem;
    color: var(--gray-400);
    margin: 0;
    text-align: center;
  }
  
  /* Loading / Error / Empty States */
  .loading-state,
  .error-state,
  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: var(--space-12);
    color: var(--gray-500);
    text-align: center;
    gap: var(--space-4);
  }
  
  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid var(--gray-200);
    border-top-color: #082770;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
  
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
  
  /* Results Info */
  .results-info {
    padding: var(--space-4) 0;
    text-align: center;
    font-size: 0.9rem;
    color: var(--gray-500);
  }
  
  /* Status Bar - Simplified */
  .status-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: var(--space-4);
    padding: var(--space-4) var(--space-6);
    background: #082770;
    color: white;
    font-size: 0.85rem;
  }
  
  .status-left {
    display: flex;
    align-items: center;
    gap: var(--space-2);
  }
  
  .status-dot {
    width: 8px;
    height: 8px;
    background: #10b981;
    border-radius: 50%;
    animation: pulse 2s infinite;
  }
  
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }
  
  .status-right {
    display: flex;
    align-items: center;
    gap: var(--space-6);
  }
  
  .system-status {
    color: rgba(255, 255, 255, 0.8);
  }
  
  .learn-more {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    color: white;
    text-decoration: none;
    opacity: 0.9;
    transition: opacity 0.2s;
  }
  
  .learn-more:hover {
    opacity: 1;
    text-decoration: underline;
  }
</style>
