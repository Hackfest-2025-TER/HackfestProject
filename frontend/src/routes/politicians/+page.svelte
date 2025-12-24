<script lang="ts">
  import { onMount } from 'svelte';
  import Header from '$lib/components/Header.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import { Search, Filter, Shield, Award, Clock, FileText, ChevronRight, CheckCircle, AlertCircle } from 'lucide-svelte';
  
  // Fetch politicians from API
  let politicians: any[] = [];
  let loading = true;
  let error = '';
  let searchQuery = '';
  let selectedParty = 'all';
  
  // Get unique parties for filter
  $: parties = [...new Set(politicians.map(p => p.party))];
  
  onMount(async () => {
    try {
      const response = await fetch('http://localhost:8000/api/politicians');
      const data = await response.json();
      politicians = data.politicians || [];
      loading = false;
    } catch (err) {
      error = 'Failed to load politicians data';
      loading = false;
      console.error('Error fetching politicians:', err);
    }
  });
  
  $: filteredPoliticians = politicians.filter(p => {
    const matchesSearch = p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          p.title.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesParty = selectedParty === 'all' || p.party === selectedParty;
    return matchesSearch && matchesParty;
  });
  
  function getScoreColor(score: number) {
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    return 'error';
  }
  
  // Calculate kept/broken/pending from manifestos
  function getPoliticianStats(politician: any) {
    // This will be computed from manifestos later
    // For now, use placeholder based on integrity score
    const total = politician.manifestos || 0;
    const score = politician.integrity_score || 0;
    const kept = Math.floor((total * score) / 100);
    const broken = total - kept;
    return { kept, broken, pending: 0 };
  }
  
  // Get human-readable overall status
  function getOverallStatus(score: number) {
    if (score >= 80) return 'Mostly Kept';
    if (score >= 60) return 'Mixed Progress';
    if (score >= 40) return 'Needs Attention';
    return 'Mostly Not Kept';
  }
  
  // Handle image error - fallback to placeholder
  function handleImageError(event: Event) {
    const img = event.target as HTMLImageElement;
    img.style.display = 'none';
    const placeholder = img.nextElementSibling as HTMLElement;
    if (placeholder) {
      placeholder.style.display = 'flex';
    }
  }
</script>

<svelte:head>
  <title>Elected Representatives - PromiseThread</title>
</svelte:head>

<Header />

<main class="politicians-page">
  <div class="container">
    <!-- Page Header -->
    <div class="page-header">
      <h1>Elected Representatives</h1>
      <p>See what elected leaders promised and how those promises are progressing.</p>
    </div>
    
    <!-- Search & Filters -->
    <div class="controls-bar">
      <div class="search-box">
        <Search size={18} />
        <input 
          type="text" 
          placeholder="Search by name or title..."
          bind:value={searchQuery}
        />
      </div>
      
      <div class="filters">
        <select bind:value={selectedParty}>
          <option value="all">All Parties</option>
          {#each parties as party}
            <option value={party}>{party}</option>
          {/each}
        </select>
      </div>
    </div>
    
    <!-- Loading State -->
    {#if loading}
      <div class="loading-state">
        <p>Loading politicians...</p>
      </div>
    {:else if error}
      <div class="error-state">
        <p>{error}</p>
      </div>
    {:else}
    
    <!-- Politicians Grid -->
    <div class="politicians-grid">
      {#each filteredPoliticians as politician}
        {@const stats = getPoliticianStats(politician)}
        <a href="/politicians/{politician.id}" class="politician-card card">
          <div class="card-header">
            <div class="avatar">
              {#if politician.image_url}
                <img 
                  src={politician.image_url} 
                  alt={politician.name}
                  on:error={handleImageError}
                />
                <div class="avatar-placeholder" style="display: none;">
                  {politician.name.charAt(0)}
                </div>
              {:else}
                <div class="avatar-placeholder">{politician.name.charAt(0)}</div>
              {/if}
            </div>
            <div class="info">
              <div class="name-row">
                <h3>{politician.name}</h3>
                {#if politician.verified}
                  <span class="verified-badge" title="Verified">
                    <Shield size={14} />
                  </span>
                {/if}
              </div>
              <p class="title">{politician.title} • {politician.party}</p>
            </div>
          </div>
          
          <!-- Promise Summary (Primary Focus) -->
          <div class="promise-summary">
            <h4>Promise Summary</h4>
            <div class="promise-stats">
              <div class="stat kept">
                <CheckCircle size={16} />
                <span class="stat-value">{stats.kept}</span>
                <span class="stat-label">Being Kept</span>
              </div>
              <div class="stat broken">
                <AlertCircle size={16} />
                <span class="stat-value">{stats.broken}</span>
                <span class="stat-label">Not Being Kept</span>
              </div>
              <div class="stat pending">
                <Clock size={16} />
                <span class="stat-value">{stats.pending}</span>
                <span class="stat-label">Under Review</span>
              </div>
            </div>
          </div>
          
          <!-- Promise Fulfillment Bar -->
          <div class="fulfillment-section">
            <div class="fulfillment-header">
              <span class="fulfillment-label">Promise Fulfillment</span>
              <span class="fulfillment-percentage">{politician.integrity_score}%</span>
            </div>
            <div class="fulfillment-bar">
              <div 
                class="fulfillment-fill {getScoreColor(politician.integrity_score)}" 
                style="width: {politician.integrity_score}%"
              ></div>
            </div>
          </div>
          
          <!-- Overall Status (Human-readable) -->
          <div class="overall-status">
            <span class="status-label">Overall Status:</span>
            <span class="status-value {getScoreColor(politician.integrity_score)}">
              {getOverallStatus(politician.integrity_score)}
            </span>
          </div>
          
          <div class="card-footer">
            <span class="manifesto-count">
              <FileText size={14} />
              {politician.manifestos} Promises Published
            </span>
            <ChevronRight size={18} />
          </div>
        </a>
      {/each}
    </div>
    {/if}
    
    {#if !loading && !error && filteredPoliticians.length === 0}
      <div class="empty-state">
        <p>No politicians found matching your criteria.</p>
      </div>
    {/if}
  </div>
</main>

<Footer />

<style>
  .politicians-page {
    min-height: 100vh;
    background: var(--gray-50);
    padding-bottom: var(--space-12);
  }
  
  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: var(--space-8) var(--space-4);
  }
  
  .page-header {
    text-align: center;
    margin-bottom: var(--space-8);
  }
  
  .page-header h1 {
    font-size: 2rem;
    margin-bottom: var(--space-2);
    color: #082770;
  }
  
  .page-header p {
    color: var(--gray-600);
    font-size: 1.1rem;
  }
  
  .controls-bar {
    display: flex;
    gap: var(--space-4);
    margin-bottom: var(--space-6);
    flex-wrap: wrap;
  }
  
  .search-box {
    flex: 1;
    min-width: 250px;
    display: flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-3) var(--space-4);
    background: white;
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-lg);
  }
  
  .search-box :global(svg) {
    color: var(--gray-400);
  }
  
  .search-box input {
    flex: 1;
    border: none;
    font-size: 0.9rem;
  }
  
  .search-box input:focus {
    outline: none;
  }
  
  .filters select {
    padding: var(--space-3) var(--space-4);
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-lg);
    background: white;
    font-size: 0.9rem;
    color: var(--gray-700);
  }
  
  .politicians-grid {
    display: grid;
    gap: var(--space-4);
  }
  
  @media (min-width: 640px) {
    .politicians-grid {
      grid-template-columns: repeat(2, 1fr);
    }
  }
  
  @media (min-width: 1024px) {
    .politicians-grid {
      grid-template-columns: repeat(3, 1fr);
    }
  }
  
  .politician-card {
    padding: var(--space-5);
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
    text-decoration: none;
    color: inherit;
    transition: all 0.2s;
  }
  
  .politician-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
  }
  
  .card-header {
    display: flex;
    gap: var(--space-3);
  }
  
  .avatar {
    width: 56px;
    height: 56px;
    border-radius: 50%;
    background: var(--primary-100);
    color: var(--primary-700);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
    font-weight: 600;
    flex-shrink: 0;
    position: relative;
    overflow: hidden;
  }
  
  .avatar img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    position: absolute;
    top: 0;
    left: 0;
  }
  
  .avatar-placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #082770;
    color: white;
    font-size: 1.5rem;
    font-weight: 600;
  }
  
  .info {
    flex: 1;
    min-width: 0;
  }
  
  .name-row {
    display: flex;
    align-items: center;
    gap: var(--space-2);
  }
  
  .name-row h3 {
    font-size: 1rem;
    margin: 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  .verified-badge {
    color: var(--primary-600);
  }
  
  .title {
    font-size: 0.875rem;
    color: var(--gray-600);
    margin: var(--space-1) 0;
  }
  
  .party {
    font-size: 0.75rem;
    color: var(--gray-400);
  }
  
  /* Promise Summary Section */
  .promise-summary {
    padding: var(--space-4);
    background: var(--gray-50);
    border-radius: var(--radius-lg);
  }
  
  .promise-summary h4 {
    font-size: 0.875rem;
    color: var(--gray-600);
    margin: 0 0 var(--space-3) 0;
    font-weight: 500;
  }
  
  .promise-stats {
    display: flex;
    gap: var(--space-4);
    flex-wrap: wrap;
  }
  
  .stat {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--space-1);
    flex: 1;
    min-width: 70px;
  }
  
  .stat.kept {
    color: var(--success-600);
  }
  
  .stat.broken {
    color: var(--error-600);
  }
  
  .stat.pending {
    color: var(--warning-600);
  }
  
  .stat-value {
    font-size: 1.5rem;
    font-weight: 700;
  }
  
  .stat-label {
    font-size: 0.7rem;
    color: var(--gray-500);
    text-align: center;
  }
  
  /* Promise Fulfillment Bar */
  .fulfillment-section {
    padding: var(--space-3);
    background: white;
    border: 1px solid var(--gray-100);
    border-radius: var(--radius-md);
  }
  
  .fulfillment-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--space-2);
  }
  
  .fulfillment-label {
    font-size: 0.8rem;
    color: var(--gray-600);
    font-weight: 500;
  }
  
  .fulfillment-percentage {
    font-size: 0.9rem;
    font-weight: 700;
    color: var(--gray-900);
  }
  
  .fulfillment-bar {
    height: 8px;
    background: var(--gray-200);
    border-radius: var(--radius-full);
    overflow: hidden;
  }
  
  .fulfillment-fill {
    height: 100%;
    border-radius: var(--radius-full);
    transition: width 0.5s ease-out;
  }
  
  .fulfillment-fill.success {
    background: linear-gradient(90deg, #10b981, #34d399);
  }
  
  .fulfillment-fill.warning {
    background: linear-gradient(90deg, #f59e0b, #fbbf24);
  }
  
  .fulfillment-fill.error {
    background: linear-gradient(90deg, #ef4444, #f87171);
  }
  
  /* Overall Status */
  .overall-status {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-3);
    background: var(--gray-50);
    border-radius: var(--radius-md);
  }
  
  .status-label {
    font-size: 0.8rem;
    color: var(--gray-500);
    font-weight: 500;
  }
  
  .status-value {
    font-size: 0.95rem;
    font-weight: 600;
  }
  
  .status-value.success {
    color: var(--success-600);
  }
  
  .status-value.warning {
    color: var(--warning-600);
  }
  
  .status-value.error {
    color: var(--error-600);
  }
  
  .card-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-top: var(--space-3);
    border-top: 1px solid var(--gray-100);
    color: var(--gray-400);
  }
  
  .manifesto-count {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    font-size: 0.8rem;
  }
  
  .empty-state,
  .loading-state,
  .error-state {
    text-align: center;
    padding: var(--space-12);
    color: var(--gray-500);
  }
  
  .error-state {
    color: var(--error);
  }
</style>
