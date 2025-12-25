<script>
  import { ThumbsUp, ThumbsDown, Lock, Clock, CheckCircle, AlertCircle, Shield, TrendingUp } from 'lucide-svelte';
  import { onMount } from 'svelte';
  import { authStore } from '$lib/stores';
  
  export let manifestoId;
  export let isLocked = false;
  export let gracePeriodEnd = new Date().toISOString();
  export let voteKept = 0;
  export let voteBroken = 0;
  
  let hasVoted = false;
  let userVote = null;
  let isVoting = false;
  let error = null;
  
  $: totalVotes = voteKept + voteBroken;
  $: keptPercent = totalVotes > 0 ? Math.round((voteKept / totalVotes) * 100) : 0;
  $: brokenPercent = totalVotes > 0 ? Math.round((voteBroken / totalVotes) * 100) : 0;
  $: daysRemaining = Math.max(0, Math.ceil((new Date(gracePeriodEnd).getTime() - Date.now()) / (1000 * 60 * 60 * 24)));
  
  // Reactive credential from auth store
  $: credential = $authStore.credential;
  
  // Check if user has voted on this manifesto whenever credential changes
  $: if (credential) {
    checkVoteStatus();
  }
  
  function checkVoteStatus() {
    // Check from auth store's usedVotes
    if (credential?.usedVotes?.includes(manifestoId) || credential?.usedVotes?.includes(String(manifestoId))) {
      hasVoted = true;
      const votes = JSON.parse(localStorage.getItem('user_votes') || '{}');
      userVote = votes[manifestoId] || 'kept';
    } else {
      // Fallback: Check local votes storage
      const votes = JSON.parse(localStorage.getItem('user_votes') || '{}');
      if (votes[manifestoId]) {
        hasVoted = true;
        userVote = votes[manifestoId];
      }
    }
  }
  
  onMount(() => {
    checkVoteStatus();
  });
  
  async function submitVote(voteType) {
    if (isLocked || hasVoted || isVoting || !credential) return;
    
    isVoting = true;
    error = null;
    
    try {
      const response = await fetch('http://localhost:8000/api/votes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          manifesto_id: manifestoId,
          nullifier: credential.nullifier,
          vote_type: voteType
        })
      });
      
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to submit vote');
      }
      
      // Store vote locally
      const votes = JSON.parse(localStorage.getItem('user_votes') || '{}');
      votes[manifestoId] = voteType;
      localStorage.setItem('user_votes', JSON.stringify(votes));
      
      // Update auth store with voted manifesto
      authStore.markVoted(manifestoId);
      
      hasVoted = true;
      userVote = voteType;
      
      // Update local counts
      if (voteType === 'kept') {
        voteKept += 1;
      } else {
        voteBroken += 1;
      }
    } catch (err) {
      error = err.message;
    } finally {
      isVoting = false;
    }
  }
</script>

<div class="vote-box card">
  <div class="vote-header">
    {#if isLocked}
      <div class="header-icon locked">
        <Lock size={20} />
      </div>
      <div class="header-text">
        <h3>Voting Locked</h3>
        <p>Grace period active</p>
      </div>
    {:else}
      <div class="header-icon active">
        <TrendingUp size={20} />
      </div>
      <div class="header-text">
        <h3>Share Your Feedback</h3>
        <p>Anonymous & Verifiable</p>
      </div>
    {/if}
  </div>
  
  {#if isLocked}
    <div class="status-banner warning">
      <div class="banner-content">
        <Clock size={18} />
        <div>
          <strong>Grace Period Active</strong>
          <span>Voting opens in <strong>{daysRemaining} days</strong></span>
        </div>
      </div>
    </div>
  {:else if !credential}
    <div class="status-banner info">
      <div class="banner-content">
        <Shield size={18} />
        <div>
          <strong>Verification Required</strong>
          <span>Verify once to vote anonymously</span>
        </div>
      </div>
      <a href="/auth" class="verify-link">Get Verified</a>
    </div>
  {:else if hasVoted}
    <div class="status-banner success">
      <div class="banner-content">
        <CheckCircle size={18} />
        <div>
          <strong>Vote Recorded</strong>
          <span class="vote-label {userVote === 'kept' ? 'kept' : 'broken'}">
            {userVote === 'kept' ? 'Promise Being Kept' : 'Promise Not Being Kept'}
          </span>
        </div>
      </div>
    </div>
  {/if}
  
  {#if error}
    <div class="error-message">
      <AlertCircle size={16} />
      <span>{error}</span>
    </div>
  {/if}
  
  <!-- Vote Buttons -->
  <div class="vote-buttons">
    <button
      on:click={() => submitVote('kept')}
      disabled={isLocked || hasVoted || isVoting || !credential}
      class="vote-btn kept"
      class:active={hasVoted && userVote === 'kept'}
      class:disabled={isLocked || hasVoted || isVoting || !credential}
    >
      <div class="btn-icon">
        <ThumbsUp size={24} />
      </div>
      <div class="btn-content">
        <span class="btn-label">Being Kept</span>
        <span class="btn-count">{voteKept}</span>
      </div>
    </button>
    
    <button
      on:click={() => submitVote('broken')}
      disabled={isLocked || hasVoted || isVoting || !credential}
      class="vote-btn broken"
      class:active={hasVoted && userVote === 'broken'}
      class:disabled={isLocked || hasVoted || isVoting || !credential}
    >
      <div class="btn-icon">
        <ThumbsDown size={24} />
      </div>
      <div class="btn-content">
        <span class="btn-label">Not Being Kept</span>
        <span class="btn-count">{voteBroken}</span>
      </div>
    </button>
  </div>
  
  <!-- Results -->
  <div class="vote-results">
    <div class="results-header">
      <span class="results-title">Community Feedback</span>
      <span class="results-total">{totalVotes} votes</span>
    </div>
    
    <div class="progress-bar">
      <div class="progress-fill kept" style="width: {keptPercent}%"></div>
      <div class="progress-fill broken" style="width: {brokenPercent}%"></div>
    </div>
    
    <div class="results-labels">
      <div class="result-item kept">
        <span class="result-label">Being Kept</span>
        <span class="result-percent">{keptPercent}%</span>
      </div>
      <div class="result-item broken">
        <span class="result-label">Not Being Kept</span>
        <span class="result-percent">{brokenPercent}%</span>
      </div>
    </div>
  </div>
  
  <div class="privacy-note">
    <Shield size={14} />
    <span>Your identity remains anonymous. Only your vote is recorded.</span>
  </div>
</div>

<style>
  .vote-box {
    padding: var(--space-6);
    background: white;
  }
  
  .vote-header {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    margin-bottom: var(--space-5);
    padding-bottom: var(--space-4);
    border-bottom: 1px solid var(--gray-200);
  }
  
  .header-icon {
    width: 48px;
    height: 48px;
    border-radius: var(--radius-xl);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }
  
  .header-icon.active {
    background: var(--success-100);
    color: var(--success-600);
  }
  
  .header-icon.locked {
    background: var(--warning-100);
    color: var(--warning-600);
  }
  
  .header-text h3 {
    font-size: 1.125rem;
    font-weight: 700;
    color: var(--gray-900);
    margin: 0 0 var(--space-1) 0;
  }
  
  .header-text p {
    font-size: 0.875rem;
    color: var(--gray-500);
    margin: 0;
  }
  
  /* Status Banners */
  .status-banner {
    padding: var(--space-4);
    border-radius: var(--radius-lg);
    margin-bottom: var(--space-5);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-3);
  }
  
  .status-banner.warning {
    background: var(--warning-50);
    border: 1px solid var(--warning-200);
  }
  
  .status-banner.info {
    background: var(--primary-50);
    border: 1px solid var(--primary-200);
  }
  
  .status-banner.success {
    background: var(--success-50);
    border: 1px solid var(--success-200);
  }
  
  .banner-content {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    flex: 1;
  }
  
  .banner-content :global(svg) {
    flex-shrink: 0;
  }
  
  .status-banner.warning .banner-content :global(svg) {
    color: var(--warning-600);
  }
  
  .status-banner.info .banner-content :global(svg) {
    color: var(--primary-600);
  }
  
  .status-banner.success .banner-content :global(svg) {
    color: var(--success-600);
  }
  
  .banner-content strong {
    display: block;
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--gray-900);
    margin-bottom: 2px;
  }
  
  .banner-content span {
    font-size: 0.8125rem;
    color: var(--gray-600);
  }
  
  .vote-label {
    font-weight: 600;
  }
  
  .vote-label.kept {
    color: var(--success-700);
  }
  
  .vote-label.broken {
    color: var(--error-700);
  }
  
  .verify-link {
    padding: var(--space-2) var(--space-4);
    background: var(--primary-600);
    color: white;
    border-radius: var(--radius-md);
    font-size: 0.875rem;
    font-weight: 500;
    text-decoration: none;
    white-space: nowrap;
    transition: background 0.2s;
  }
  
  .verify-link:hover {
    background: var(--primary-700);
  }
  
  .error-message {
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
  
  /* Vote Buttons */
  .vote-buttons {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--space-4);
    margin-bottom: var(--space-6);
  }
  
  .vote-btn {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-5);
    border-radius: var(--radius-xl);
    border: 2px solid var(--gray-200);
    background: white;
    cursor: pointer;
    transition: all 0.2s;
  }
  
  .vote-btn:hover:not(.disabled) {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
  }
  
  .vote-btn.kept:hover:not(.disabled) {
    border-color: var(--success-500);
    background: var(--success-50);
  }
  
  .vote-btn.broken:hover:not(.disabled) {
    border-color: var(--error-500);
    background: var(--error-50);
  }
  
  .vote-btn.active.kept {
    border-color: var(--success-600);
    background: var(--success-100);
  }
  
  .vote-btn.active.broken {
    border-color: var(--error-600);
    background: var(--error-100);
  }
  
  .vote-btn.disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  .btn-icon {
    width: 56px;
    height: 56px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--gray-100);
    color: var(--gray-600);
    transition: all 0.2s;
  }
  
  .vote-btn.kept .btn-icon {
    background: var(--success-100);
    color: var(--success-600);
  }
  
  .vote-btn.broken .btn-icon {
    background: var(--error-100);
    color: var(--error-600);
  }
  
  .vote-btn.active.kept .btn-icon {
    background: var(--success-600);
    color: white;
  }
  
  .vote-btn.active.broken .btn-icon {
    background: var(--error-600);
    color: white;
  }
  
  .btn-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--space-1);
  }
  
  .btn-label {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--gray-700);
  }
  
  .btn-count {
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--gray-900);
  }
  
  /* Results */
  .vote-results {
    background: var(--gray-50);
    padding: var(--space-4);
    border-radius: var(--radius-lg);
    margin-bottom: var(--space-4);
  }
  
  .results-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--space-3);
  }
  
  .results-title {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--gray-900);
  }
  
  .results-total {
    font-size: 0.75rem;
    color: var(--gray-500);
  }
  
  .progress-bar {
    height: 10px;
    background: var(--gray-200);
    border-radius: var(--radius-full);
    overflow: hidden;
    display: flex;
    margin-bottom: var(--space-3);
  }
  
  .progress-fill {
    height: 100%;
    transition: width 0.5s ease;
  }
  
  .progress-fill.kept {
    background: linear-gradient(90deg, var(--success-500), var(--success-400));
  }
  
  .progress-fill.broken {
    background: linear-gradient(90deg, var(--error-500), var(--error-400));
  }
  
  .results-labels {
    display: flex;
    justify-content: space-between;
    gap: var(--space-4);
  }
  
  .result-item {
    display: flex;
    align-items: center;
    gap: var(--space-2);
  }
  
  .result-item::before {
    content: '';
    width: 12px;
    height: 12px;
    border-radius: 50%;
    flex-shrink: 0;
  }
  
  .result-item.kept::before {
    background: var(--success-500);
  }
  
  .result-item.broken::before {
    background: var(--error-500);
  }
  
  .result-label {
    font-size: 0.8125rem;
    color: var(--gray-600);
  }
  
  .result-percent {
    font-size: 0.875rem;
    font-weight: 700;
    color: var(--gray-900);
    margin-left: var(--space-1);
  }
  
  .privacy-note {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-3);
    background: var(--gray-50);
    border-radius: var(--radius-md);
    font-size: 0.75rem;
    color: var(--gray-600);
  }
  
  .privacy-note :global(svg) {
    color: var(--success-500);
    flex-shrink: 0;
  }
</style>
