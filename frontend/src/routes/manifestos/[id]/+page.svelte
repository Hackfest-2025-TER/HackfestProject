<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import CommentThread from '$lib/components/CommentThread.svelte';
  import VoteBox from '$lib/components/VoteBox.svelte';
  import HashDisplay from '$lib/components/HashDisplay.svelte';
  import { Shield, ThumbsUp, MessageSquare, Share2, ExternalLink, Clock, CheckCircle, Info, Search, Send, AlertCircle } from 'lucide-svelte';
  
  // Get manifesto ID from URL
  $: manifestoId = parseInt($page.params.id);
  
  // State
  let manifesto: any = null;
  let isLoading = true;
  let error = '';
  let commentSortBy = 'top';
  
  // Load manifesto data
  onMount(async () => {
    await loadManifesto();
  });
  
  async function loadManifesto() {
    try {
      const response = await fetch(`http://localhost:8000/api/manifestos/${manifestoId}`);
      if (!response.ok) throw new Error('Manifesto not found');
      manifesto = await response.json();
    } catch (err: any) {
      error = err.message || 'Failed to load manifesto';
    } finally {
      isLoading = false;
    }
  }
  
  function formatDate(dateStr: string) {
    if (!dateStr) return 'N/A';
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    return date.toLocaleDateString();
  }
</script>

<svelte:head>
  <title>{manifesto?.title || 'Loading...'} - PromiseThread</title>
</svelte:head>

{#if isLoading}
  <main class="manifesto-detail">
    <div class="container">
      <div class="loading-state">
        <div class="spinner"></div>
        <p>Loading manifesto...</p>
      </div>
    </div>
  </main>
{:else if error}
  <main class="manifesto-detail">
    <div class="container">
      <div class="error-state">
        <AlertCircle size={48} />
        <h2>Manifesto Not Found</h2>
        <p>{error}</p>
        <a href="/manifestos" class="btn btn-secondary">← Back to Manifestos</a>
      </div>
    </div>
  </main>
{:else if manifesto}
<main class="manifesto-detail">
  <div class="container">
    <div class="content-grid">
      <!-- Main Content -->
      <div class="main-content">
        <!-- Manifesto Header -->
        <div class="manifesto-header card">
          <div class="header-meta">
            <span class="proposal-id">#{manifesto.id}</span>
            <span class="status-badge verified">
              <CheckCircle size={12} />
              Verified
            </span>
            <span class="posted-time">{manifesto.postedAgo}</span>
          </div>
          
          <h1>{manifesto.title}</h1>
          
          <div class="hash-info">
            <div class="hash-item">
              <span class="hash-label"># Hash:</span>
              <HashDisplay hash={manifesto.hash} />
            </div>
            <div class="hash-item">
              <span class="hash-label">🌳 Merkle Root:</span>
              <HashDisplay hash={manifesto.hash?.slice(0, 10) || '0x...'} />
            </div>
            <a href="#" class="view-proof">View On-Chain Proof ↗</a>
          </div>
          
          <p class="description">{manifesto.description}</p>
          
          <div class="manifesto-stats">
            <div class="stat">
              <ThumbsUp size={18} />
              <span>{manifesto.vote_kept + manifesto.vote_broken} Votes</span>
            </div>
            <div class="stat">
              <MessageSquare size={18} />
              <span>Discussion</span>
            </div>
            <button class="share-btn">
              <Share2 size={18} />
              Share
            </button>
          </div>
        </div>
        
        <!-- Discussion Section - Using Dynamic CommentThread -->
        <CommentThread {manifestoId} />
      </div>
      
      <!-- Sidebar -->
      <aside class="sidebar">
        <!-- About Card -->
        <div class="sidebar-card card">
          <div class="sidebar-header">
            <Info size={18} />
            <h4>About this Proposal</h4>
          </div>
          
          <div class="sidebar-section">
            <span class="section-label">TIMELINE</span>
            <div class="timeline-badge">
              <Clock size={14} />
              {manifesto.grace_period_end ? `Until ${new Date(manifesto.grace_period_end).toLocaleDateString()}` : 'Open'}
            </div>
          </div>
          
          <div class="sidebar-section">
            <span class="section-label">VOTE RESULTS</span>
            <div class="quorum-bar">
              <div class="quorum-fill" style="width: {manifesto.vote_kept / Math.max(1, manifesto.vote_kept + manifesto.vote_broken) * 100}%"></div>
            </div>
            <span class="quorum-text">{manifesto.vote_kept} Kept / {manifesto.vote_broken} Broken</span>
          </div>
          
          <div class="sidebar-card card">
            <h4>Community Guidelines</h4>
            <ul class="rules-list">
              <li>
              <Shield size={14} />
              All comments are permanent. You cannot edit or delete after 5 minutes.
            </li>
            <li>
              <Shield size={14} />
              Your identity is hidden, but your reputation is persistent.
            </li>
            <li>
              <Shield size={14} />
              Civil discourse is enforced by community voting.
            </li>
          </ul>
        </div>
        
        <!-- Related Proposals -->
        <div class="sidebar-card card">
          <h4>Related Proposals</h4>
          <div class="related-list">
            <a href="/manifestos/4011" class="related-item">
              <span class="related-id">#4011</span>
              <span class="related-title">Digital ID Implementation</span>
              <span class="related-status closed">Closed</span>
            </a>
            <a href="/manifestos/4088" class="related-item">
              <span class="related-id">#4088</span>
              <span class="related-title">Tax Reform 2024</span>
              <span class="related-status voting">Voting</span>
            </a>
          </div>
        </div>
      </aside>
    </div>
  </div>
</main>
{/if}

<style>
  .manifesto-detail {
    min-height: 100vh;
    background: var(--gray-50);
    padding: var(--space-6) 0;
  }
  
  .loading-state,
  .error-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: var(--space-12);
    text-align: center;
    color: var(--gray-500);
  }
  
  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid var(--gray-200);
    border-top-color: var(--primary-500);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: var(--space-4);
  }
  
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
  
  .error-state h2 {
    margin-bottom: var(--space-2);
    color: var(--gray-700);
  }
  
  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 var(--space-4);
  }
  
  .content-grid {
    display: grid;
    gap: var(--space-6);
  }
  
  @media (min-width: 1024px) {
    .content-grid {
      grid-template-columns: 1fr 320px;
    }
  }
  
  /* Main Content */
  .manifesto-header {
    padding: var(--space-6);
    margin-bottom: var(--space-4);
  }
  
  .header-meta {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    margin-bottom: var(--space-4);
  }
  
  .proposal-id {
    font-family: var(--font-mono);
    font-size: 0.8rem;
    color: var(--gray-500);
  }
  
  .status-badge {
    display: inline-flex;
    align-items: center;
    gap: var(--space-1);
    padding: var(--space-1) var(--space-2);
    font-size: 0.7rem;
    font-weight: 600;
    border-radius: var(--radius-sm);
  }
  
  .status-badge.verified {
    background: var(--success-100);
    color: var(--success-700);
  }
  
  .posted-time {
    font-size: 0.8rem;
    color: var(--gray-400);
    margin-left: auto;
  }
  
  .manifesto-header h1 {
    font-size: 1.75rem;
    margin-bottom: var(--space-4);
  }
  
  .hash-info {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: var(--space-4);
    margin-bottom: var(--space-4);
    padding-bottom: var(--space-4);
    border-bottom: 1px solid var(--gray-200);
  }
  
  .hash-item {
    display: flex;
    align-items: center;
    gap: var(--space-2);
  }
  
  .hash-label {
    font-size: 0.75rem;
    color: var(--gray-500);
  }
  
  .view-proof {
    font-size: 0.8rem;
    color: var(--success-600);
    text-decoration: none;
    margin-left: auto;
  }
  
  .view-proof:hover {
    text-decoration: underline;
  }
  
  .description {
    color: var(--gray-700);
    line-height: 1.7;
    margin-bottom: var(--space-3);
  }
  
  .details {
    color: var(--gray-600);
    font-size: 0.875rem;
    line-height: 1.6;
  }
  
  .manifesto-stats {
    display: flex;
    align-items: center;
    gap: var(--space-6);
    margin-top: var(--space-6);
    padding-top: var(--space-4);
    border-top: 1px solid var(--gray-200);
  }
  
  .stat {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    color: var(--gray-600);
    font-size: 0.875rem;
  }
  
  .stat :global(svg) {
    color: var(--success-500);
  }
  
  .share-btn {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-2) var(--space-3);
    border: 1px solid var(--gray-200);
    background: white;
    border-radius: var(--radius-lg);
    color: var(--gray-600);
    font-size: 0.875rem;
    cursor: pointer;
    margin-left: auto;
  }
  
  .share-btn:hover {
    background: var(--gray-50);
  }
  
  /* Comment Input */
  .comment-input {
    padding: var(--space-4);
    margin-bottom: var(--space-4);
  }
  
  .input-header {
    display: flex;
    gap: var(--space-3);
    margin-bottom: var(--space-3);
  }
  
  .avatar-placeholder {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: var(--gray-200);
    flex-shrink: 0;
  }
  
  .input-wrapper {
    flex: 1;
  }
  
  .input-wrapper input {
    width: 100%;
    padding: var(--space-3);
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-lg);
    font-size: 0.875rem;
  }
  
  .input-wrapper input:focus {
    outline: none;
    border-color: var(--primary-500);
  }
  
  .input-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: var(--space-3);
  }
  
  .posting-as {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    font-size: 0.75rem;
    color: var(--gray-500);
  }
  
  .posting-as :global(svg) {
    color: var(--success-500);
  }
  
  .nullifier-label {
    color: var(--gray-400);
  }
  
  /* Discussion */
  .discussion {
    overflow: hidden;
  }
  
  .discussion-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-4);
    border-bottom: 1px solid var(--gray-200);
  }
  
  .discussion-header h3 {
    font-size: 1rem;
  }
  
  .sort-tabs {
    display: flex;
    gap: var(--space-1);
  }
  
  .sort-btn {
    padding: var(--space-2) var(--space-3);
    border: none;
    background: transparent;
    color: var(--gray-500);
    font-size: 0.8rem;
    font-weight: 500;
    border-radius: var(--radius-md);
    cursor: pointer;
  }
  
  .sort-btn:hover {
    background: var(--gray-100);
  }
  
  .sort-btn.active {
    background: var(--gray-100);
    color: var(--gray-900);
  }
  
  .comments-list {
    max-height: 600px;
    overflow-y: auto;
  }
  
  /* Sidebar */
  .sidebar {
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
  }
  
  .sidebar-card {
    padding: var(--space-4);
  }
  
  .politician-info {
    margin: var(--space-3) 0;
  }
  
  .politician-link {
    color: var(--primary-600);
    text-decoration: none;
    font-size: 0.875rem;
  }
  
  .politician-link:hover {
    text-decoration: underline;
  }
  
  .category-badge {
    display: inline-block;
    padding: var(--space-1) var(--space-3);
    background: var(--primary-100);
    color: var(--primary-700);
    border-radius: var(--radius-full);
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
  }
  
  .voting-locked {
    display: flex;
    align-items: center;
    gap: var(--space-4);
    padding: var(--space-5);
    background: var(--warning-50);
    border: 1px solid var(--warning-200);
    border-radius: var(--radius-xl);
  }
  
  .voting-locked :global(svg) {
    color: var(--warning-600);
    flex-shrink: 0;
  }
  
  .voting-locked h4 {
    margin: 0 0 var(--space-1) 0;
    color: var(--gray-900);
    font-size: 0.95rem;
  }
  
  .voting-locked p {
    margin: 0;
    color: var(--gray-600);
    font-size: 0.85rem;
  }
  
  .auth-prompt {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-4);
    background: var(--gray-50);
    text-align: center;
    justify-content: center;
  }
  
  .auth-prompt :global(svg) {
    color: var(--gray-400);
  }
  
  .auth-prompt a {
    color: var(--primary-600);
    text-decoration: underline;
  }
  
  .empty-comments {
    text-align: center;
    padding: var(--space-8);
    color: var(--gray-500);
  }
  
  .empty-comments :global(svg) {
    margin: 0 auto var(--space-4) auto;
    opacity: 0.5;
  }
  
  .loading-state, .error-state {
    text-align: center;
    padding: var(--space-12) var(--space-4);
  }
  
  .error-state h2 {
    color: var(--error-600);
    margin-bottom: var(--space-4);
  }
  
  .status-display {
    padding: var(--space-2) var(--space-3);
    border-radius: var(--radius-md);
    font-size: 0.85rem;
    font-weight: 600;
    text-transform: uppercase;
  }
  
  .status-display.success {
    background: var(--success-100);
    color: var(--success-700);
  }
  
  .status-display.error {
    background: var(--error-100);
    color: var(--error-700);
  }
  
  .status-display.warning {
    background: var(--warning-100);
    color: var(--warning-700);
  }
  
  .vote-bars {
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
  }
  
  .vote-bar {
    display: flex;
    align-items: center;
    gap: var(--space-2);
  }
  
  .vote-label {
    font-size: 0.75rem;
    color: var(--gray-600);
    width: 50px;
  }
  
  .bar-container {
    flex: 1;
    height: 6px;
    background: var(--gray-200);
    border-radius: var(--radius-full);
    overflow: hidden;
  }
  
  .bar-fill {
    height: 100%;
    transition: width 0.3s ease;
  }
  
  .bar-fill.success {
    background: var(--success-500);
  }
  
  .bar-fill.error {
    background: var(--error-500);
  }
  
  .vote-count {
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--gray-700);
    width: 40px;
    text-align: right;
  }
  
  .category-tag {
    display: inline-block;
    padding: var(--space-1) var(--space-3);
    background: var(--gray-100);
    color: var(--gray-700);
    border-radius: var(--radius-md);
    font-size: 0.75rem;
    font-weight: 500;
  }
  
  .sidebar-header {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    margin-bottom: var(--space-4);
  }
  
  .sidebar-header h4 {
    font-size: 0.9rem;
  }
  
  .sidebar-section {
    margin-bottom: var(--space-4);
  }
  
  .section-label {
    display: block;
    font-size: 0.65rem;
    font-weight: 600;
    color: var(--gray-400);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: var(--space-2);
  }
  
  .timeline-badge {
    display: inline-flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-2) var(--space-3);
    background: var(--success-50);
    color: var(--success-700);
    border-radius: var(--radius-lg);
    font-size: 0.8rem;
    font-weight: 500;
  }
  
  .quorum-bar {
    height: 8px;
    background: var(--gray-200);
    border-radius: var(--radius-full);
    overflow: hidden;
    margin-bottom: var(--space-1);
  }
  
  .quorum-fill {
    height: 100%;
    background: var(--success-500);
  }
  
  .quorum-text {
    font-size: 0.75rem;
    color: var(--gray-600);
  }
  
  .sidebar-card h4 {
    font-size: 0.9rem;
    margin-bottom: var(--space-3);
  }
  
  .rules-list {
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
  }
  
  .rules-list li {
    display: flex;
    gap: var(--space-2);
    font-size: 0.75rem;
    color: var(--gray-600);
    line-height: 1.4;
  }
  
  .rules-list :global(svg) {
    color: var(--success-500);
    flex-shrink: 0;
    margin-top: 2px;
  }
  
  .related-list {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
  }
  
  .related-item {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-2);
    border-radius: var(--radius-md);
    text-decoration: none;
    font-size: 0.8rem;
  }
  
  .related-item:hover {
    background: var(--gray-50);
  }
  
  .related-id {
    color: var(--gray-400);
    font-family: var(--font-mono);
  }
  
  .related-title {
    color: var(--gray-700);
    flex: 1;
  }
  
  .related-status {
    font-size: 0.65rem;
    padding: 2px 6px;
    border-radius: var(--radius-sm);
    font-weight: 500;
  }
  
  .related-status.closed {
    background: var(--gray-100);
    color: var(--gray-500);
  }
  
  .related-status.voting {
    background: var(--success-100);
    color: var(--success-600);
  }
</style>
