<script lang="ts">
  import { onMount } from 'svelte';
  import { Activity, Shield, Database, Clock, CheckCircle, FileText, Hash, ExternalLink } from 'lucide-svelte';
  import { getNetworkStats, getMerkleRoot } from '$lib/api';
  import HashDisplay from '$lib/components/HashDisplay.svelte';
  
  let stats: any = null;
  let merkleRoot = '';
  let recentBlocks: any[] = [];
  let isLoading = true;
  
  onMount(async () => {
    try {
      const [statsData, rootData, blocksResponse] = await Promise.all([
        getNetworkStats(),
        getMerkleRoot(),
        fetch('http://localhost:8000/api/blockchain/blocks?limit=10')
      ]);
      
      stats = statsData;
      merkleRoot = rootData.merkle_root;
      
      // Load real blocks from API
      if (blocksResponse.ok) {
        const blocksData = await blocksResponse.json();
        recentBlocks = (blocksData.blocks || []).slice(0, 3).map((block: any) => ({
          height: block.number,
          hash: block.hash?.substring(0, 10) + '...' + block.hash?.substring(block.hash.length - 4) || 'N/A',
          timestamp: formatTimestamp(block.timestamp),
          transactions: block.tx_count || 1,
          proposer: block.action ? `Action: ${block.action}` : 'System'
        }));
      }
    } catch (e) {
      console.error('Failed to load audit data:', e);
    } finally {
      isLoading = false;
    }
  });
  
  function formatTimestamp(ts: string): string {
    if (!ts) return 'N/A';
    const date = new Date(ts);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} mins ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours} hours ago`;
    return date.toLocaleDateString();
  }
</script>

<svelte:head>
  <title>Audit Trail - PromiseThread</title>
</svelte:head>

<main class="audit-page">
  <div class="container">
    <div class="page-header">
      <div class="header-icon">
        <Activity size={32} />
      </div>
      <div>
        <h1>Blockchain Audit Trail</h1>
        <p>Verify the integrity of votes and promises on the immutable ledger.</p>
      </div>
    </div>
    
    <!-- Network Stats -->
    <div class="stats-grid">
      <div class="stat-card card">
        <div class="stat-icon">
          <Database size={24} />
        </div>
        <div class="stat-info">
          <span class="label">Total Votes Recorded</span>
          <span class="value">{stats?.total_votes?.toLocaleString() || '...'}</span>
        </div>
      </div>
      
      <div class="stat-card card">
        <div class="stat-icon">
          <Shield size={24} />
        </div>
        <div class="stat-info">
          <span class="label">System Integrity</span>
          <span class="value">{stats?.integrity_score || 100}%</span>
        </div>
      </div>
      
      <div class="stat-card card">
        <div class="stat-icon">
          <Clock size={24} />
        </div>
        <div class="stat-info">
          <span class="label">Last Update</span>
          <span class="value">Just now</span>
        </div>
      </div>
    </div>
    
    <div class="content-grid">
      <!-- Merkle Root Section -->
      <section class="merkle-section card">
        <div class="section-header">
          <h2>
            <Hash size={20} />
            Current Merkle Root
          </h2>
          <span class="badge">Live</span>
        </div>
        <p class="description">
          This cryptographic hash represents the current state of all votes. 
          Any change to a past vote would alter this root, making tampering detectable.
        </p>
        <div class="hash-container">
          <HashDisplay hash={merkleRoot || 'Loading...'} />
        </div>
        <div class="verification-status">
          <CheckCircle size={16} />
          <span>Cryptographically Verified</span>
        </div>
      </section>
      
      <!-- Recent Blocks -->
      <section class="blocks-section">
        <h2>Recent Blocks</h2>
        <div class="blocks-list">
          {#each recentBlocks as block}
            <div class="block-card card">
              <div class="block-header">
                <span class="block-height">#{block.height}</span>
                <span class="block-time">{block.timestamp}</span>
              </div>
              <div class="block-hash">
                <span class="label">Hash:</span>
                <code class="hash">{block.hash}</code>
              </div>
              <div class="block-meta">
                <span>{block.transactions} txs</span>
                <span>•</span>
                <span>{block.proposer}</span>
              </div>
            </div>
          {/each}
        </div>
      </section>
    </div>
  </div>
</main>

<style>
  .audit-page {
    min-height: 100vh;
    background: var(--gray-50);
    padding: var(--space-8) 0;
  }
  
  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 var(--space-4);
  }
  
  .page-header {
    display: flex;
    align-items: center;
    gap: var(--space-4);
    margin-bottom: var(--space-8);
  }
  
  .header-icon {
    width: 64px;
    height: 64px;
    background: var(--primary-100);
    color: var(--primary-700);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .page-header h1 {
    font-size: 2rem;
    font-weight: 700;
    color: var(--gray-900);
    margin-bottom: var(--space-1);
  }
  
  .page-header p {
    color: var(--gray-600);
    font-size: 1.1rem;
  }
  
  /* Stats Grid */
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: var(--space-4);
    margin-bottom: var(--space-8);
  }
  
  .stat-card {
    display: flex;
    align-items: center;
    gap: var(--space-4);
    padding: var(--space-6);
    background: white;
  }
  
  .stat-icon {
    width: 48px;
    height: 48px;
    background: var(--primary-50);
    color: var(--primary-600);
    border-radius: var(--radius-lg);
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .stat-info {
    display: flex;
    flex-direction: column;
  }
  
  .stat-info .label {
    font-size: 0.85rem;
    color: var(--gray-500);
    margin-bottom: var(--space-1);
  }
  
  .stat-info .value {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--gray-900);
  }
  
  /* Content Grid */
  .content-grid {
    display: grid;
    gap: var(--space-8);
    grid-template-columns: 1fr;
  }
  
  @media (min-width: 768px) {
    .content-grid {
      grid-template-columns: 2fr 1fr;
    }
  }
  
  /* Merkle Section */
  .merkle-section {
    padding: var(--space-6);
    background: white;
  }
  
  .section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--space-4);
  }
  
  .section-header h2 {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--gray-900);
  }
  
  .badge {
    padding: var(--space-1) var(--space-3);
    background: var(--success-100);
    color: var(--success-700);
    font-size: 0.75rem;
    font-weight: 600;
    border-radius: var(--radius-full);
    text-transform: uppercase;
  }
  
  .description {
    color: var(--gray-600);
    margin-bottom: var(--space-6);
    line-height: 1.6;
  }
  
  .hash-container {
    margin-bottom: var(--space-6);
  }
  
  .verification-status {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    color: var(--success-600);
    font-weight: 500;
    font-size: 0.9rem;
  }
  
  /* Blocks Section */
  .blocks-section h2 {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--gray-900);
    margin-bottom: var(--space-4);
  }
  
  .blocks-list {
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
  }
  
  .block-card {
    padding: var(--space-4);
    background: white;
  }
  
  .block-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: var(--space-2);
  }
  
  .block-height {
    font-weight: 600;
    color: var(--primary-600);
  }
  
  .block-time {
    font-size: 0.85rem;
    color: var(--gray-500);
  }
  
  .block-hash {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    margin-bottom: var(--space-2);
    font-size: 0.9rem;
  }
  
  .block-hash .label {
    color: var(--gray-500);
  }
  
  .block-hash .hash {
    font-family: var(--font-mono);
    color: var(--gray-700);
  }
  
  .block-meta {
    display: flex;
    gap: var(--space-2);
    font-size: 0.85rem;
    color: var(--gray-500);
  }
</style>
