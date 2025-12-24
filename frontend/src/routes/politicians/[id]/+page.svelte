<script lang="ts">
  import Header from '$lib/components/Header.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import ProgressRing from '$lib/components/ProgressRing.svelte';
  import HashDisplay from '$lib/components/HashDisplay.svelte';
  import { Shield, Award, FileText, Calendar, ExternalLink, CheckCircle, XCircle, Clock, ChevronRight, Share2 } from 'lucide-svelte';
  import { page } from '$app/stores';
  
  $: id = $page.params.id;
  
  // Sample politician data
  const politician = {
    id: 1,
    name: 'Jane Doe',
    title: 'Governor',
    party: 'Progressive Party',
    state: 'State of Democracy',
    avatar: null,
    verified: true,
    integrityScore: 87,
    publicKey: '0x8a72f92b45c1e98d3a7b6f1c2d4e5f6a7b8c9d0e',
    joinedDate: 'Jan 2020',
    manifestos: [
      {
        id: 1,
        title: 'Universal Healthcare Act',
        status: 'kept',
        deadline: '2024-06-30',
        hash: '0x7f8e9d0c1b2a3f4e5d6c7b8a9'
      },
      {
        id: 2,
        title: 'North-South Rail Link',
        status: 'pending',
        deadline: '2025-12-31',
        hash: '0x3c4d5e6f7a8b9c0d1e2f3a4b'
      },
      {
        id: 3,
        title: 'Green Energy Initiative',
        status: 'kept',
        deadline: '2024-03-15',
        hash: '0x9a0b1c2d3e4f5a6b7c8d9e0f'
      },
      {
        id: 4,
        title: 'Education Reform Bill',
        status: 'broken',
        deadline: '2023-09-01',
        hash: '0x1d2e3f4a5b6c7d8e9f0a1b2c'
      },
      {
        id: 5,
        title: 'Housing Affordability Plan',
        status: 'kept',
        deadline: '2024-01-01',
        hash: '0x5f6a7b8c9d0e1f2a3b4c5d6e'
      }
    ]
  };
  
  const stats = {
    kept: politician.manifestos.filter(m => m.status === 'kept').length,
    broken: politician.manifestos.filter(m => m.status === 'broken').length,
    pending: politician.manifestos.filter(m => m.status === 'pending').length
  };
  
  function getStatusBadge(status: string) {
    switch (status) {
      case 'kept': return { icon: CheckCircle, class: 'success', label: 'Kept' };
      case 'broken': return { icon: XCircle, class: 'error', label: 'Broken' };
      default: return { icon: Clock, class: 'warning', label: 'Pending' };
    }
  }
</script>

<svelte:head>
  <title>{politician.name} - PromiseThread</title>
</svelte:head>

<Header />

<main class="politician-profile">
  <div class="container">
    <!-- Profile Header -->
    <div class="profile-header card">
      <div class="profile-main">
        <div class="avatar">
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
          <p class="title">{politician.title} · {politician.state}</p>
          <p class="party">{politician.party}</p>
          
          <div class="meta-row">
            <span class="meta-item">
              <Calendar size={14} />
              Joined {politician.joinedDate}
            </span>
            <span class="meta-item">
              <FileText size={14} />
              {politician.manifestos.length} Manifestos
            </span>
          </div>
        </div>
        
        <div class="score-ring">
          <ProgressRing 
            progress={politician.integrityScore} 
            size={100} 
            strokeWidth={8}
            color="var(--success-500)"
          />
          <div class="score-center">
            <span class="score-value">{politician.integrityScore}%</span>
            <span class="score-label">Integrity</span>
          </div>
        </div>
      </div>
      
      <!-- Public Key -->
      <div class="public-key">
        <span class="key-label">Public Key:</span>
        <HashDisplay hash={politician.publicKey} />
      </div>
      
      <div class="profile-actions">
        <button class="btn-secondary">
          <Share2 size={16} />
          Share Profile
        </button>
        <a href="https://etherscan.io" target="_blank" class="btn-secondary">
          <ExternalLink size={16} />
          View on Etherscan
        </a>
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
                  <span class="hash">
                    <code>{manifesto.hash.slice(0, 12)}...</code>
                  </span>
                  <span class="deadline">Deadline: {manifesto.deadline}</span>
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
    </div>
  </div>
</main>

<Footer />

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
