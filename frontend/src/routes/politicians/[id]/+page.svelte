<script lang="ts">
  import { onMount } from 'svelte';
  import ProgressRing from '$lib/components/ProgressRing.svelte';
  import { Shield, Award, FileText, Calendar, ExternalLink, CheckCircle, XCircle, Clock, ChevronRight, Share2 } from 'lucide-svelte';
  import { page } from '$app/stores';
  
  $: id = $page.params.id;
  
  let politician: any = null;
  let loading = true;
  let error = '';
  
  $: stats = politician ? {
    kept: politician.manifestos.filter((m: any) => m.status === 'kept').length,
    broken: politician.manifestos.filter((m: any) => m.status === 'broken').length,
    pending: politician.manifestos.filter((m: any) => m.status === 'pending').length
  } : { kept: 0, broken: 0, pending: 0 };
  
  onMount(async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/politicians/${id}`);
      if (!response.ok) throw new Error('Politician not found');
      const data = await response.json();
      politician = data;
      loading = false;
    } catch (err: any) {
      error = err.message || 'Failed to load politician data';
      loading = false;
    }
  });
  
  function getStatusBadge(status: string) {
    switch (status) {
      case 'kept': return { icon: CheckCircle, class: 'success', label: 'Kept' };
      case 'broken': return { icon: XCircle, class: 'error', label: 'Broken' };
      default: return { icon: Clock, class: 'warning', label: 'Pending' };
    }
  }
  
  function formatDate(dateStr: string) {
    if (!dateStr) return 'N/A';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short' });
  }
  
  function handleImageError(event: Event) {
    const img = event.target as HTMLImageElement;
    img.style.display = 'none';
  }
</script>

<svelte:head>
  <title>{politician?.name || 'Loading...'} - PromiseThread</title>
</svelte:head>

{#if loading}
  <main class="politician-profile">
    <div class="container">
      <div class="loading-state">Loading politician profile...</div>
    </div>
  </main>
{:else if error}
  <main class="politician-profile">
    <div class="container">
      <div class="error-state">
        <h2>Politician Not Found</h2>
        <p>{error}</p>
        <a href="/politicians" class="btn-secondary">← Back to Politicians</a>
      </div>
    </div>
  </main>
{:else if politician}
  <main class="politician-profile">
    <div class="container">
      <!-- Profile Header -->
      <div class="profile-header card">
        <div class="profile-main">
          {#if politician.image_url}
            <img 
              src={politician.image_url} 
              alt={politician.name}
              class="avatar-img"
              on:error={handleImageError}
            />
          {/if}
          <div class="avatar" style={politician.image_url ? 'display: none;' : ''}>
            {politician.name.split(' ').map(n => n[0]).join('')}
          </div>
          
          <div class="profile-info">
            <div class="name-row">
              <h1>{politician.name}</h1>
              {#if politician.verified}
                <span class="verified-badge">
                  <Shield size={18} />
                  Verified
                </span>
              {/if}
            </div>
            <p class="title">{politician.title}</p>
            <p class="party">{politician.party}</p>
            
            <div class="meta-row">
              <span class="meta-item">
                <Calendar size={14} />
                Joined {formatDate(politician.joined_date)}
              </span>
              <span class="meta-item">
                <FileText size={14} />
                {politician.manifestos.length} Manifestos
              </span>
            </div>
          </div>
          
          <div class="score-ring">
            <ProgressRing 
              percentage={politician.integrity_score} 
              size={100} 
              strokeWidth={8}
              color="var(--success-500)"
            />
            <div class="score-center">
              <span class="score-value">{politician.integrity_score}%</span>
              <span class="score-label">Integrity</span>
            </div>
          </div>
        </div>
        
        <div class="profile-actions">
          <button class="btn-secondary">
            <Share2 size={16} />
            Share Profile
          </button>
        </div>
      </div>
      
      <!-- Stats Cards -->
      <div class="stats-grid">
        <div class="stat-card success">
          <CheckCircle size={24} />
          <div class="stat-content">
            <span class="stat-value">{stats.kept}</span>
            <span class="stat-label">Promises Kept</span>
          </div>
        </div>
        <div class="stat-card error">
          <XCircle size={24} />
          <div class="stat-content">
            <span class="stat-value">{stats.broken}</span>
            <span class="stat-label">Promises Broken</span>
          </div>
        </div>
        <div class="stat-card warning">
          <Clock size={24} />
          <div class="stat-content">
            <span class="stat-value">{stats.pending}</span>
            <span class="stat-label">Pending</span>
          </div>
        </div>
      </div>
      
      <!-- Manifestos List -->
      <div class="manifestos-section">
        <h2>Manifesto Records</h2>
        
        {#if politician.manifestos.length > 0}
          <div class="manifestos-list">
            {#each politician.manifestos as manifesto}
              {@const badge = getStatusBadge(manifesto.status)}
              <a href="/manifestos/{manifesto.id}" class="manifesto-item card">
                <div class="manifesto-main">
                  <div class="status-icon {badge.class}">
                    <svelte:component this={badge.icon} size={20} />
                  </div>
                  <div class="manifesto-info">
                    <h3>{manifesto.title}</h3>
                    <div class="manifesto-meta">
                      <span class="deadline">Deadline: {formatDate(manifesto.deadline)}</span>
                      {#if manifesto.category}
                        <span class="category">{manifesto.category}</span>
                      {/if}
                    </div>
                  </div>
                </div>
                <div class="manifesto-status">
                  <span class="status-badge {badge.class}">{badge.label}</span>
                  <ChevronRight size={18} />
                </div>
              </a>
            {/each}
          </div>
        {:else}
          <div class="empty-state">
            <FileText size={48} />
            <p>No manifestos yet</p>
          </div>
        {/if}
      </div>
    </div>
  </main>
{/if}

<style>
  .politician-profile {
    min-height: 100vh;
    background: var(--gray-50);
    padding-bottom: var(--space-12);
  }
  
  .container {
    max-width: 900px;
    margin: 0 auto;
    padding: var(--space-8) var(--space-4);
  }
  
  /* Profile Header */
  .profile-header {
    padding: var(--space-6);
    margin-bottom: var(--space-6);
  }
  
  .profile-main {
    display: flex;
    gap: var(--space-5);
    align-items: flex-start;
    flex-wrap: wrap;
  }
  
  .avatar {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: var(--primary-100);
    color: var(--primary-700);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2rem;
    font-weight: 600;
    flex-shrink: 0;
  }
  
  .avatar-img {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    object-fit: cover;
    flex-shrink: 0;
  }
  
  .loading-state, .error-state {
    text-align: center;
    padding: var(--space-12) var(--space-4);
  }
  
  .error-state h2 {
    color: var(--error-600);
    margin-bottom: var(--space-4);
  }
  
  .empty-state {
    text-align: center;
    padding: var(--space-8);
    color: var(--gray-500);
  }
  
  .empty-state :global(svg) {
    margin-bottom: var(--space-4);
    opacity: 0.5;
  }
  
  .profile-info {
    flex: 1;
    min-width: 250px;
  }
  
  .name-row {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    flex-wrap: wrap;
    margin-bottom: var(--space-2);
  }
  
  .name-row h1 {
    font-size: 1.5rem;
    margin: 0;
  }
  
  .verified-badge {
    display: inline-flex;
    align-items: center;
    gap: var(--space-1);
    padding: var(--space-1) var(--space-2);
    background: var(--primary-100);
    color: var(--primary-700);
    border-radius: var(--radius-full);
    font-size: 0.75rem;
    font-weight: 600;
  }
  
  .title {
    color: var(--gray-700);
    font-size: 0.95rem;
    margin-bottom: var(--space-1);
  }
  
  .party {
    color: var(--gray-500);
    font-size: 0.875rem;
    margin-bottom: var(--space-3);
  }
  
  .meta-row {
    display: flex;
    gap: var(--space-4);
    flex-wrap: wrap;
  }
  
  .meta-item {
    display: flex;
    align-items: center;
    gap: var(--space-1);
    font-size: 0.8rem;
    color: var(--gray-500);
  }
  
  .score-ring {
    position: relative;
    flex-shrink: 0;
  }
  
  .score-center {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    text-align: center;
  }
  
  .score-center .score-value {
    display: block;
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--success-600);
  }
  
  .score-center .score-label {
    font-size: 0.65rem;
    color: var(--gray-500);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  
  .public-key {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-4);
    background: var(--gray-50);
    border-radius: var(--radius-lg);
    margin: var(--space-5) 0;
    flex-wrap: wrap;
  }
  
  .key-label {
    font-size: 0.75rem;
    color: var(--gray-500);
    font-weight: 600;
    text-transform: uppercase;
  }
  
  .profile-actions {
    display: flex;
    gap: var(--space-3);
    flex-wrap: wrap;
  }
  
  .btn-secondary {
    display: inline-flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-2) var(--space-4);
    border: 1px solid var(--gray-300);
    background: white;
    color: var(--gray-700);
    border-radius: var(--radius-lg);
    font-size: 0.85rem;
    font-weight: 500;
    cursor: pointer;
    text-decoration: none;
    transition: all 0.2s;
  }
  
  .btn-secondary:hover {
    border-color: var(--primary-500);
    color: var(--primary-600);
  }
  
  /* Stats Grid */
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: var(--space-4);
    margin-bottom: var(--space-6);
  }
  
  @media (max-width: 640px) {
    .stats-grid {
      grid-template-columns: 1fr;
    }
  }
  
  .stat-card {
    display: flex;
    align-items: center;
    gap: var(--space-4);
    padding: var(--space-5);
    background: white;
    border-radius: var(--radius-xl);
    border: 1px solid var(--gray-200);
  }
  
  .stat-card.success :global(svg) {
    color: var(--success-600);
  }
  
  .stat-card.error :global(svg) {
    color: var(--error-600);
  }
  
  .stat-card.warning :global(svg) {
    color: var(--warning-600);
  }
  
  .stat-content {
    display: flex;
    flex-direction: column;
  }
  
  .stat-content .stat-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--gray-900);
  }
  
  .stat-content .stat-label {
    font-size: 0.8rem;
    color: var(--gray-500);
  }
  
  /* Manifestos Section */
  .manifestos-section h2 {
    font-size: 1.25rem;
    margin-bottom: var(--space-4);
  }
  
  .manifestos-list {
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
  }
  
  .manifesto-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-4);
    text-decoration: none;
    color: inherit;
    transition: all 0.2s;
  }
  
  .manifesto-item:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-1px);
  }
  
  .manifesto-main {
    display: flex;
    align-items: center;
    gap: var(--space-3);
  }
  
  .status-icon {
    width: 40px;
    height: 40px;
    border-radius: var(--radius-lg);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }
  
  .status-icon.success {
    background: var(--success-100);
    color: var(--success-600);
  }
  
  .status-icon.error {
    background: var(--error-100);
    color: var(--error-600);
  }
  
  .status-icon.warning {
    background: var(--warning-100);
    color: var(--warning-600);
  }
  
  .manifesto-info h3 {
    font-size: 0.95rem;
    margin-bottom: var(--space-1);
  }
  
  .manifesto-meta {
    display: flex;
    gap: var(--space-4);
    font-size: 0.75rem;
    color: var(--gray-500);
  }
  
  .hash code {
    font-family: var(--font-mono);
    color: var(--primary-600);
  }
  
  .manifesto-status {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    color: var(--gray-400);
  }
  
  .status-badge {
    padding: var(--space-1) var(--space-3);
    border-radius: var(--radius-full);
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.02em;
  }
  
  .status-badge.success {
    background: var(--success-100);
    color: var(--success-700);
  }
  
  .status-badge.error {
    background: var(--error-100);
    color: var(--error-700);
  }
  
  .status-badge.warning {
    background: var(--warning-100);
    color: var(--warning-700);
  }
</style>
