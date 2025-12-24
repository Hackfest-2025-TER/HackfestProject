<script lang="ts">
  import Header from '$lib/components/Header.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import { Building2, Shield, CheckCircle, Lock, ChevronRight, Calendar, AlertCircle, Fingerprint, Clock, ThumbsUp, ThumbsDown, ExternalLink } from 'lucide-svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  import { authStore, isAuthenticated, credential } from '$lib/stores';
  import { getManifesto, submitVote, getMerkleRoot, getBlocks } from '$lib/api';
  
  // Get manifesto ID from URL
  $: manifestoId = $page.url.searchParams.get('id') || 'MAN-2023-0002';
  
  // Reactive auth state
  $: isAuth = $isAuthenticated;
  $: userCredential = $credential;
  
  // Data state
  let manifesto: any = null;
  let merkleRoot = '';
  let currentBlock = 0;
  let isLoading = true;
  let error = '';
  
  // Vote state
  let voteType: 'kept' | 'broken' | null = null;
  let isSubmitting = false;
  let voteSubmitted = false;
  let voteResult: any = null;
  
  // Load data on mount
  onMount(async () => {
    if (!$isAuthenticated) {
      // Redirect to auth if not logged in
      goto('/auth');
      return;
    }
    
    try {
      const [manifestoData, rootData, blocksData] = await Promise.all([
        getManifesto(manifestoId),
        getMerkleRoot(),
        getBlocks(1)
      ]);
      
      manifesto = manifestoData;
      merkleRoot = rootData.merkle_root;
      currentBlock = blocksData.blocks?.[0]?.number || 19230442;
      
      // Check if already voted
      if (userCredential?.usedVotes?.includes(manifestoId)) {
        voteSubmitted = true;
      }
    } catch (e) {
      error = 'Failed to load manifesto data.';
      console.error(e);
    }
    isLoading = false;
  });
  
  // Check if voting is open (grace period passed)
  $: canVote = manifesto && new Date() >= new Date(manifesto.grace_period_end);
  $: hasAlreadyVoted = userCredential?.usedVotes?.includes(manifestoId);
  
  // Time until voting opens
  $: timeUntilVoting = (() => {
    if (!manifesto?.grace_period_end) return 'Unknown';
    const graceEnd = new Date(manifesto.grace_period_end);
    const now = new Date();
    if (now >= graceEnd) return null;
    
    const diff = graceEnd.getTime() - now.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    
    if (days > 0) return `${days} days, ${hours} hours`;
    return `${hours} hours`;
  })();
  
  // Submit vote
  async function handleSubmitVote() {
    if (!voteType || !userCredential || hasAlreadyVoted) return;
    
    isSubmitting = true;
    error = '';
    
    try {
      const result = await submitVote({
        manifesto_id: manifestoId,
        vote_type: voteType,
        nullifier: userCredential.nullifier
      });
      
      if (result.success) {
        voteResult = result;
        voteSubmitted = true;
        
        // Update local credential with new vote
        authStore.markVoted(manifestoId);
      } else {
        error = result.message || 'Vote submission failed.';
      }
    } catch (e) {
      error = 'Failed to submit vote. Please try again.';
      console.error(e);
    }
    
    isSubmitting = false;
  }
</script>

<svelte:head>
  <title>Vote on Promise - PromiseThread</title>
</svelte:head>

<Header variant="citizen" />

<main class="attestation-page">
  <div class="container">
    <!-- Page Header -->
    <div class="page-header">
      <span class="header-badge">
        <Building2 size={14} />
        ANONYMOUS VOTING PORTAL
      </span>
      <h1>Cast Your Vote</h1>
      <p>Evaluate this political promise anonymously. Your vote is cryptographically verified but your identity remains hidden.</p>
    </div>
    
    <!-- ZK Identity Banner -->
    {#if isAuth}
      <div class="zk-banner">
        <div class="zk-left">
          <Shield size={20} />
          <div>
            <strong>Identity: Verified (Zero-Knowledge)</strong>
            <span>Nullifier: {userCredential?.nullifierShort}</span>
          </div>
        </div>
        <span class="session-badge">
          <span class="status-dot online"></span>
          Secure Session Active
        </span>
      </div>
    {:else}
      <div class="zk-banner warning">
        <div class="zk-left">
          <AlertCircle size={20} />
          <div>
            <strong>Not Verified</strong>
            <span>Please verify your identity to vote</span>
          </div>
        </div>
        <a href="/auth" class="verify-btn">
          <Fingerprint size={16} />
          Verify Now
        </a>
      </div>
    {/if}
    
    {#if isLoading}
      <div class="loading-state">
        <div class="spinner"></div>
        <p>Loading promise data...</p>
      </div>
    {:else if error && !manifesto}
      <div class="error-state">
        <AlertCircle size={24} />
        <p>{error}</p>
        <a href="/manifestos" class="back-link">Back to Promises</a>
      </div>
    {:else if manifesto}
      <div class="content-grid">
        <!-- Promise Card -->
        <div class="promise-section">
          <div class="promise-card card">
            <span class="category-badge">{manifesto.category?.toUpperCase()}</span>
            <h2>{manifesto.title}</h2>
            <p class="promise-description">{manifesto.description}</p>
            
            <div class="promise-meta">
              <div class="meta-item">
                <span class="meta-label">Politician</span>
                <span class="meta-value">{manifesto.politician_name}</span>
              </div>
              <div class="meta-item">
                <span class="meta-label">Deadline</span>
                <span class="meta-value">{manifesto.deadline}</span>
              </div>
              <div class="meta-item">
                <span class="meta-label">Current Status</span>
                <span class="status-badge {manifesto.status}">{manifesto.status}</span>
              </div>
            </div>
            
            <!-- Current Vote Tally -->
            <div class="vote-tally">
              <h4>Current Vote Tally</h4>
              <div class="tally-bars">
                <div class="tally-row">
                  <span class="tally-label">
                    <ThumbsUp size={14} />
                    Kept
                  </span>
                  <div class="tally-bar">
                    <div class="tally-fill kept" style="width: {manifesto.vote_kept / (manifesto.vote_kept + manifesto.vote_broken + 1) * 100}%"></div>
                  </div>
                  <span class="tally-count">{manifesto.vote_kept}</span>
                </div>
                <div class="tally-row">
                  <span class="tally-label">
                    <ThumbsDown size={14} />
                    Broken
                  </span>
                  <div class="tally-bar">
                    <div class="tally-fill broken" style="width: {manifesto.vote_broken / (manifesto.vote_kept + manifesto.vote_broken + 1) * 100}%"></div>
                  </div>
                  <span class="tally-count">{manifesto.vote_broken}</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Voting Form -->
          {#if voteSubmitted}
            <div class="vote-success card">
              <div class="success-icon">
                <CheckCircle size={48} />
              </div>
              <h3>Vote Recorded!</h3>
              <p>Your anonymous vote has been recorded on the blockchain.</p>
              
              {#if voteResult}
                <div class="vote-receipt">
                  <div class="receipt-row">
                    <span>Vote Hash</span>
                    <code>{voteResult.vote_hash?.slice(0, 20)}...</code>
                  </div>
                  <div class="receipt-row">
                    <span>Block Height</span>
                    <code>#{voteResult.block_height?.toLocaleString()}</code>
                  </div>
                </div>
              {/if}
              
              <a href="/manifestos" class="back-btn">
                <ChevronRight size={18} />
                Back to Promises
              </a>
            </div>
          {:else if !canVote}
            <div class="grace-period-card card">
              <Clock size={32} />
              <h3>Voting Not Yet Open</h3>
              <p>This promise is in its grace period. Evaluation opens in:</p>
              <div class="countdown">
                <span class="countdown-value">{timeUntilVoting}</span>
              </div>
              <p class="grace-note">
                Grace periods ensure fair evaluation by preventing premature judgment.
              </p>
            </div>
          {:else if hasAlreadyVoted}
            <div class="already-voted card">
              <CheckCircle size={32} />
              <h3>You've Already Voted</h3>
              <p>Your nullifier shows you have already cast a vote on this promise. Each citizen can only vote once.</p>
              <a href="/manifestos" class="back-btn">
                Back to Promises
              </a>
            </div>
          {:else}
            <div class="attestation-form card">
              <div class="form-header">
                <Fingerprint size={20} />
                <h3>Your Assessment</h3>
              </div>
              
              <div class="attestation-options">
                <label class="attestation-option" class:selected={voteType === 'kept'}>
                  <input type="radio" bind:group={voteType} value="kept" />
                  <div class="option-radio"></div>
                  <div class="option-content">
                    <strong>
                      <ThumbsUp size={16} />
                      Promise Kept
                    </strong>
                    <span>I believe this promise has been fulfilled based on available evidence.</span>
                  </div>
                </label>
                
                <label class="attestation-option" class:selected={voteType === 'broken'}>
                  <input type="radio" bind:group={voteType} value="broken" />
                  <div class="option-radio"></div>
                  <div class="option-content">
                    <strong>
                      <ThumbsDown size={16} />
                      Promise Broken
                    </strong>
                    <span>I see insufficient evidence that this promise was fulfilled.</span>
                  </div>
                </label>
              </div>
              
              {#if error}
                <div class="error-banner">
                  <AlertCircle size={16} />
                  <span>{error}</span>
                </div>
              {/if}
              
              <button 
                class="submit-btn" 
                on:click={handleSubmitVote}
                disabled={!voteType || isSubmitting}
              >
                {#if isSubmitting}
                  <span class="spinner small"></span>
                  Recording Vote...
                {:else}
                  <Fingerprint size={18} />
                  Submit Anonymous Vote
                {/if}
              </button>
              
              <p class="disclaimer">
                <Lock size={14} />
                Your vote is irreversible. Only your nullifier is recorded, not your identity.
              </p>
            </div>
          {/if}
        </div>
        
        <!-- Sidebar -->
        <aside class="sidebar">
          <!-- Blockchain Record -->
          <div class="sidebar-card card">
            <div class="card-header">
              <span class="card-label">BLOCKCHAIN RECORD</span>
              <Lock size={14} />
            </div>
            
            <div class="record-field">
              <span class="field-label">YOUR NULLIFIER</span>
              <div class="field-value mono">{userCredential?.nullifierShort || '...'}</div>
              <span class="field-hint">Prevents double-voting without revealing identity</span>
            </div>
            
            <div class="record-field">
              <span class="field-label">CURRENT BLOCK</span>
              <div class="field-value">#{currentBlock.toLocaleString()}</div>
            </div>
            
            <div class="record-field">
              <span class="field-label">MERKLE ROOT</span>
              <div class="field-value mono">{merkleRoot?.slice(0, 16)}...</div>
            </div>
            
            <a href="/audit-trail" class="audit-link">
              <ExternalLink size={14} />
              View Full Audit Trail
            </a>
          </div>
          
          <!-- Privacy Guarantee -->
          <div class="sidebar-card card">
            <h4>
              <Shield size={16} />
              Privacy Guarantee
            </h4>
            <ul class="privacy-list">
              <li>Your vote is verified using Zero-Knowledge Proofs</li>
              <li>Only your <strong>nullifier</strong> is stored - never your voter ID</li>
              <li>Vote aggregates are public; individual votes are private</li>
              <li>All records are immutably stored on-chain</li>
            </ul>
          </div>
          
          <!-- How It Works -->
          <div class="sidebar-card card">
            <h4>How Voting Works</h4>
            <ol class="how-list">
              <li>Your ZK credential proves you're an eligible voter</li>
              <li>Your nullifier ensures one vote per promise</li>
              <li>Vote is recorded with only the nullifier</li>
              <li>Aggregates update on-chain immediately</li>
            </ol>
          </div>
        </aside>
      </div>
    {/if}
  </div>
</main>

<Footer />

<style>
  .attestation-page {
    min-height: 100vh;
    background: var(--gray-50);
  }
  
  .container {
    max-width: 1100px;
    margin: 0 auto;
    padding: var(--space-8) var(--space-4);
  }
  
  .page-header {
    margin-bottom: var(--space-6);
  }
  
  .header-badge {
    display: inline-flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-1) var(--space-3);
    background: var(--primary-100);
    color: var(--primary-700);
    border-radius: var(--radius-full);
    font-size: 0.75rem;
    font-weight: 600;
    margin-bottom: var(--space-3);
  }
  
  .page-header h1 {
    font-size: 1.75rem;
    margin-bottom: var(--space-2);
  }
  
  .page-header p {
    color: var(--gray-500);
  }
  
  /* ZK Banner */
  .zk-banner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-4);
    background: var(--success-50);
    border: 1px solid var(--success-200);
    border-radius: var(--radius-lg);
    margin-bottom: var(--space-6);
  }
  
  .zk-banner.warning {
    background: var(--warning-50);
    border-color: var(--warning-200);
  }
  
  .zk-left {
    display: flex;
    align-items: center;
    gap: var(--space-3);
  }
  
  .zk-banner :global(svg) {
    color: var(--success-600);
  }
  
  .zk-banner.warning :global(svg) {
    color: var(--warning-600);
  }
  
  .zk-left strong {
    display: block;
    color: var(--gray-900);
  }
  
  .zk-left span {
    font-size: 0.875rem;
    color: var(--gray-600);
    font-family: var(--font-mono);
  }
  
  .session-badge {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    font-size: 0.875rem;
    color: var(--success-700);
  }
  
  .status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
  }
  
  .status-dot.online {
    background: var(--success-500);
    animation: pulse 2s infinite;
  }
  
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
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
  }
  
  /* Loading/Error States */
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
  
  .spinner.small {
    width: 18px;
    height: 18px;
    border-width: 2px;
    margin: 0;
  }
  
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
  
  .back-link {
    margin-top: var(--space-4);
    color: var(--primary-600);
  }
  
  /* Content Grid */
  .content-grid {
    display: grid;
    gap: var(--space-6);
  }
  
  @media (min-width: 768px) {
    .content-grid {
      grid-template-columns: 1fr 320px;
    }
  }
  
  /* Promise Card */
  .promise-card {
    padding: var(--space-6);
    margin-bottom: var(--space-4);
  }
  
  .category-badge {
    display: inline-block;
    padding: var(--space-1) var(--space-3);
    background: var(--primary-100);
    color: var(--primary-700);
    border-radius: var(--radius-md);
    font-size: 0.75rem;
    font-weight: 600;
    margin-bottom: var(--space-3);
  }
  
  .promise-card h2 {
    font-size: 1.25rem;
    margin-bottom: var(--space-3);
  }
  
  .promise-description {
    color: var(--gray-600);
    line-height: 1.6;
    margin-bottom: var(--space-4);
  }
  
  .promise-meta {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: var(--space-4);
    padding-top: var(--space-4);
    border-top: 1px solid var(--gray-200);
    margin-bottom: var(--space-4);
  }
  
  .meta-item {
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
  }
  
  .meta-label {
    font-size: 0.75rem;
    color: var(--gray-500);
    text-transform: uppercase;
  }
  
  .meta-value {
    font-weight: 600;
  }
  
  .status-badge {
    display: inline-block;
    padding: var(--space-1) var(--space-2);
    border-radius: var(--radius-md);
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: capitalize;
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
  
  /* Vote Tally */
  .vote-tally {
    padding-top: var(--space-4);
    border-top: 1px solid var(--gray-200);
  }
  
  .vote-tally h4 {
    font-size: 0.875rem;
    margin-bottom: var(--space-3);
    color: var(--gray-700);
  }
  
  .tally-row {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    margin-bottom: var(--space-2);
  }
  
  .tally-label {
    display: flex;
    align-items: center;
    gap: var(--space-1);
    width: 80px;
    font-size: 0.875rem;
    color: var(--gray-600);
  }
  
  .tally-bar {
    flex: 1;
    height: 8px;
    background: var(--gray-200);
    border-radius: var(--radius-full);
    overflow: hidden;
  }
  
  .tally-fill {
    height: 100%;
    border-radius: var(--radius-full);
    transition: width 0.3s;
  }
  
  .tally-fill.kept {
    background: var(--success-500);
  }
  
  .tally-fill.broken {
    background: var(--error-500);
  }
  
  .tally-count {
    width: 50px;
    text-align: right;
    font-weight: 600;
    font-size: 0.875rem;
  }
  
  /* Grace Period Card */
  .grace-period-card,
  .already-voted {
    padding: var(--space-8);
    text-align: center;
  }
  
  .grace-period-card :global(svg),
  .already-voted :global(svg) {
    color: var(--warning-500);
    margin-bottom: var(--space-4);
  }
  
  .already-voted :global(svg) {
    color: var(--success-500);
  }
  
  .grace-period-card h3,
  .already-voted h3 {
    margin-bottom: var(--space-2);
  }
  
  .countdown {
    margin: var(--space-4) 0;
  }
  
  .countdown-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--warning-600);
  }
  
  .grace-note {
    font-size: 0.875rem;
    color: var(--gray-500);
  }
  
  /* Attestation Form */
  .attestation-form {
    padding: var(--space-6);
  }
  
  .form-header {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    margin-bottom: var(--space-4);
  }
  
  .form-header :global(svg) {
    color: var(--primary-600);
  }
  
  .form-header h3 {
    font-size: 1rem;
  }
  
  .attestation-options {
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
    margin-bottom: var(--space-4);
  }
  
  .attestation-option {
    display: flex;
    align-items: flex-start;
    gap: var(--space-3);
    padding: var(--space-4);
    border: 2px solid var(--gray-200);
    border-radius: var(--radius-lg);
    cursor: pointer;
    transition: all 0.2s;
  }
  
  .attestation-option:hover {
    border-color: var(--primary-300);
  }
  
  .attestation-option.selected {
    border-color: var(--primary-500);
    background: var(--primary-50);
  }
  
  .attestation-option input {
    display: none;
  }
  
  .option-radio {
    width: 20px;
    height: 20px;
    border: 2px solid var(--gray-300);
    border-radius: 50%;
    flex-shrink: 0;
    margin-top: 2px;
    transition: all 0.2s;
  }
  
  .attestation-option.selected .option-radio {
    border-color: var(--primary-500);
    background: var(--primary-500);
    box-shadow: inset 0 0 0 3px white;
  }
  
  .option-content strong {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    margin-bottom: var(--space-1);
    color: var(--gray-900);
  }
  
  .option-content span {
    font-size: 0.875rem;
    color: var(--gray-500);
  }
  
  .error-banner {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-3);
    background: var(--error-50);
    border: 1px solid var(--error-200);
    border-radius: var(--radius-md);
    color: var(--error-700);
    font-size: 0.875rem;
    margin-bottom: var(--space-4);
  }
  
  .submit-btn {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--space-2);
    padding: var(--space-4);
    background: var(--primary-600);
    color: white;
    border: none;
    border-radius: var(--radius-lg);
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }
  
  .submit-btn:hover:not(:disabled) {
    background: var(--primary-700);
  }
  
  .submit-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  .disclaimer {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--space-2);
    margin-top: var(--space-4);
    font-size: 0.75rem;
    color: var(--gray-500);
  }
  
  /* Vote Success */
  .vote-success {
    padding: var(--space-8);
    text-align: center;
  }
  
  .success-icon {
    width: 80px;
    height: 80px;
    margin: 0 auto var(--space-4);
    background: var(--success-100);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .success-icon :global(svg) {
    color: var(--success-600);
  }
  
  .vote-success h3 {
    margin-bottom: var(--space-2);
  }
  
  .vote-success > p {
    color: var(--gray-500);
    margin-bottom: var(--space-4);
  }
  
  .vote-receipt {
    background: var(--gray-900);
    border-radius: var(--radius-lg);
    padding: var(--space-4);
    margin-bottom: var(--space-4);
    text-align: left;
  }
  
  .receipt-row {
    display: flex;
    justify-content: space-between;
    padding: var(--space-2) 0;
    border-bottom: 1px solid var(--gray-700);
  }
  
  .receipt-row:last-child {
    border-bottom: none;
  }
  
  .receipt-row span {
    color: var(--gray-400);
    font-size: 0.875rem;
  }
  
  .receipt-row code {
    color: var(--success-400);
    font-family: var(--font-mono);
    font-size: 0.8rem;
  }
  
  .back-btn {
    display: inline-flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-3) var(--space-6);
    background: var(--gray-100);
    color: var(--gray-700);
    border-radius: var(--radius-lg);
    text-decoration: none;
    font-weight: 500;
  }
  
  .back-btn:hover {
    background: var(--gray-200);
  }
  
  /* Sidebar */
  .sidebar {
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
  }
  
  .sidebar-card {
    padding: var(--space-5);
  }
  
  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--space-4);
  }
  
  .card-label {
    font-size: 0.7rem;
    font-weight: 600;
    color: var(--gray-500);
    letter-spacing: 0.05em;
  }
  
  .record-field {
    margin-bottom: var(--space-4);
  }
  
  .field-label {
    display: block;
    font-size: 0.7rem;
    color: var(--gray-500);
    margin-bottom: var(--space-1);
    letter-spacing: 0.05em;
  }
  
  .field-value {
    font-weight: 600;
    color: var(--gray-900);
  }
  
  .field-value.mono {
    font-family: var(--font-mono);
    font-size: 0.8rem;
    word-break: break-all;
  }
  
  .field-hint {
    font-size: 0.7rem;
    color: var(--gray-400);
    margin-top: var(--space-1);
  }
  
  .audit-link {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    color: var(--primary-600);
    font-size: 0.875rem;
    text-decoration: none;
  }
  
  .audit-link:hover {
    text-decoration: underline;
  }
  
  .sidebar-card h4 {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    font-size: 0.875rem;
    margin-bottom: var(--space-3);
  }
  
  .privacy-list,
  .how-list {
    list-style: none;
    padding: 0;
    margin: 0;
  }
  
  .privacy-list li,
  .how-list li {
    font-size: 0.8rem;
    color: var(--gray-600);
    padding-left: var(--space-4);
    position: relative;
    margin-bottom: var(--space-2);
  }
  
  .privacy-list li::before {
    content: '✓';
    position: absolute;
    left: 0;
    color: var(--success-500);
  }
  
  .how-list {
    counter-reset: step;
  }
  
  .how-list li {
    counter-increment: step;
  }
  
  .how-list li::before {
    content: counter(step);
    position: absolute;
    left: 0;
    width: 18px;
    height: 18px;
    background: var(--primary-100);
    color: var(--primary-700);
    border-radius: 50%;
    font-size: 0.7rem;
    font-weight: 600;
    display: flex;
    align-items: center;
    justify-content: center;
  }
</style>
