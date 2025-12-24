<script lang="ts">
  import Header from '$lib/components/Header.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import ManifestoCard from '$lib/components/ManifestoCard.svelte';
  import HashDisplay from '$lib/components/HashDisplay.svelte';
  import { Search, Filter, Download, CheckCircle, Clock, FileText, ChevronLeft, ChevronRight } from 'lucide-svelte';
  
  // Sample data
  const manifestos = [
    {
      id: '1',
      title: '2024 Economic Reform Promise',
      description: 'A comprehensive framework for revitalizing the national economy through tax incentives for small businesses, digital currency integration, and sustainable energy subsidies.',
      status: 'published',
      merkleRoot: '0x4f...9a2b',
      publicationDate: 'Oct 12, 2023',
      integrityScore: 99,
      commentCount: 124
    },
    {
      id: '2',
      title: 'Education Infrastructure Plan',
      description: 'Proposal to modernize educational facilities nationwide with updated technology labs and sustainable building practices.',
      status: 'published',
      merkleRoot: '0x83...d29c',
      publicationDate: 'Sep 01, 2023',
      integrityScore: 95,
      commentCount: 82
    },
    {
      id: '3',
      title: 'Healthcare Transparency Act',
      description: 'Initiative to make all healthcare pricing publicly accessible through blockchain-verified records.',
      status: 'published',
      merkleRoot: '0xa1...b42f',
      publicationDate: 'Aug 15, 2023',
      integrityScore: 98,
      commentCount: 203
    },
    {
      id: '4',
      title: 'Urban Mobility Framework',
      description: 'A sustainable transportation plan focusing on electric vehicle infrastructure and public transit improvements.',
      status: 'verification_pending',
      merkleRoot: 'Generating...',
      publicationDate: 'Today, 10:45 AM',
      integrityScore: 0,
      commentCount: 0
    }
  ];
  
  let searchQuery = '';
  let statusFilter = 'all';
</script>

<svelte:head>
  <title>Manifestos - PromiseThread</title>
</svelte:head>

<Header variant="default" />

<main class="manifestos-page">
  <div class="container">
    <div class="page-header">
      <h1>Manifesto Dashboard</h1>
      <p>Manage your immutable commitments and view cryptographic audit trails.</p>
    </div>
    
    <!-- Stats -->
    <div class="stats-grid">
      <div class="stat-card card">
        <div class="stat-header">
          <span class="stat-label">Active Manifestos</span>
          <FileText size={20} />
        </div>
        <div class="stat-value">3</div>
        <div class="stat-trend positive">↗ 1 new this month</div>
      </div>
      
      <div class="stat-card card">
        <div class="stat-header">
          <span class="stat-label">Avg. Integrity Score</span>
        </div>
        <div class="stat-value">98.5%</div>
        <div class="integrity-bar">
          <div class="integrity-fill" style="width: 98.5%"></div>
        </div>
      </div>
      
      <div class="stat-card card">
        <div class="stat-header">
          <span class="stat-label">Verified Signatures</span>
        </div>
        <div class="stat-value">1,240</div>
        <div class="stat-meta">
          <CheckCircle size={14} />
          From verified voter IDs
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
      <table class="manifestos-table">
        <thead>
          <tr>
            <th>MANIFESTO TITLE</th>
            <th>MERKLE ROOT (HASH)</th>
            <th>PUBLICATION DATE</th>
            <th>INTEGRITY</th>
            <th>ACTIONS</th>
          </tr>
        </thead>
        <tbody>
          {#each manifestos as manifesto}
            <tr>
              <td class="title-cell">
                <div class="title-content">
                  <span class="title">{manifesto.title}</span>
                  <span class="status-badge {manifesto.status}">
                    {#if manifesto.status === 'published'}
                      <CheckCircle size={12} /> Published
                    {:else if manifesto.status === 'verification_pending'}
                      <Clock size={12} /> Verification Pending
                    {:else}
                      {manifesto.status}
                    {/if}
                  </span>
                </div>
              </td>
              <td>
                {#if manifesto.merkleRoot.startsWith('0x')}
                  <HashDisplay hash={manifesto.merkleRoot} />
                {:else}
                  <span class="generating">{manifesto.merkleRoot}</span>
                {/if}
              </td>
              <td class="date-cell">{manifesto.publicationDate}</td>
              <td>
                {#if manifesto.integrityScore > 0}
                  <div class="integrity-cell">
                    <div class="mini-bar">
                      <div class="mini-fill" style="width: {manifesto.integrityScore}%"></div>
                    </div>
                    <span>{manifesto.integrityScore}%</span>
                  </div>
                {:else}
                  <span class="generating">--</span>
                {/if}
              </td>
              <td class="actions-cell">
                {#if manifesto.status === 'published'}
                  <a href="/manifestos/{manifesto.id}" class="action-link">
                    Details
                  </a>
                  <a href="/manifestos/{manifesto.id}/comments" class="action-link primary">
                    Comments ({manifesto.commentCount})
                  </a>
                {:else}
                  <a href="/politician/manifestos/{manifesto.id}/edit" class="action-link">
                    Edit Draft
                  </a>
                {/if}
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
      
      <div class="table-footer">
        <span class="showing">Showing 1 to {manifestos.length} of {manifestos.length} manifestos</span>
        <div class="pagination">
          <button class="page-btn" disabled><ChevronLeft size={16} /></button>
          <button class="page-btn" disabled><ChevronRight size={16} /></button>
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
    margin-bottom: var(--space-8);
  }
  
  .page-header h1 {
    font-size: 1.75rem;
    margin-bottom: var(--space-2);
  }
  
  .page-header p {
    color: var(--gray-500);
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
  
  .status-badge {
    display: inline-flex;
    align-items: center;
    gap: var(--space-1);
    font-size: 0.7rem;
    font-weight: 500;
  }
  
  .status-badge.published {
    color: var(--success-600);
  }
  
  .status-badge.verification_pending {
    color: var(--warning-600);
  }
  
  .date-cell {
    color: var(--gray-500);
  }
  
  .generating {
    color: var(--gray-400);
    font-style: italic;
  }
  
  .integrity-cell {
    display: flex;
    align-items: center;
    gap: var(--space-2);
  }
  
  .mini-bar {
    width: 80px;
    height: 6px;
    background: var(--gray-200);
    border-radius: var(--radius-full);
    overflow: hidden;
  }
  
  .mini-fill {
    height: 100%;
    background: var(--success-500);
  }
  
  .actions-cell {
    display: flex;
    gap: var(--space-3);
  }
  
  .action-link {
    font-size: 0.8rem;
    color: var(--gray-600);
    text-decoration: none;
  }
  
  .action-link:hover {
    color: var(--gray-900);
  }
  
  .action-link.primary {
    color: var(--primary-600);
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
  
  .pagination {
    display: flex;
    gap: var(--space-2);
  }
  
  .page-btn {
    width: 32px;
    height: 32px;
    border: 1px solid var(--gray-200);
    background: white;
    border-radius: var(--radius-md);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--gray-400);
    cursor: pointer;
  }
  
  .page-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
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
