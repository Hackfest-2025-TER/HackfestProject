<script lang="ts">
  import { browser } from '$app/environment';
  import ManifestoCard from '$lib/components/ManifestoCard.svelte';
  import HashDisplay from '$lib/components/HashDisplay.svelte';
  import { Shield, FileText, CheckCircle, Clock, Activity, TrendingUp, Eye, AlertCircle, Fingerprint, MessageCircle, Users, Info, ChevronRight } from 'lucide-svelte';
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { authStore, isAuthenticated, credential } from '$lib/stores';
  import { getManifestos } from '$lib/api';
  
  // Reactive auth state
  $: isAuth = $isAuthenticated;
  $: userCredential = $credential;
  
  // Data
  let manifestos: any[] = [];
  let isLoading = true;
  
  // Load data without auth requirement
  onMount(async () => {
    if (!browser) return;
    
    try {
      const data = await getManifestos();
      manifestos = data.manifestos?.slice(0, 4) || [];
    } catch (e) {
      console.error('Failed to load manifestos:', e);
    }
    isLoading = false;
  });
  
  // Activity based on voted manifestos (or show demo data if not authenticated)
  $: recentActivity = isAuth 
    ? (userCredential?.usedVotes || []).slice(-3).map(id => ({
        type: 'vote',
        description: `Shared opinion on promise ${id}`,
        time: 'Recently',
        icon: CheckCircle
      }))
    : [];
</script>

<svelte:head>
  <title>Citizen Portal - PromiseThread</title>
</svelte:head>

<main class="citizen-page">
  <div class="container">
    <!-- Page Header -->
    <div class="page-header">
      <h1>Citizen Portal</h1>
      <p>Track election promises, share your opinions anonymously, and hold leaders accountable.</p>
    </div>
    
    <!-- Auth Status Banner -->
    {#if isAuth}
      <div class="auth-banner verified">
        <div class="auth-info">
          <Shield size={20} />
          <div>
            <strong>You're verified</strong>
            <span>You can share feedback anonymously</span>
          </div>
        </div>
        <span class="opinions-shared">
          <MessageCircle size={14} />
          {userCredential?.usedVotes?.length || 0} feedback given
        </span>
      </div>
    {:else}
      <div class="auth-banner info">
        <div class="auth-info">
          <Info size={20} />
          <div>
            <strong>Want to share feedback?</strong>
            <span>Verify once to participate anonymously</span>
          </div>
        </div>
        <a href="/auth" class="verify-btn">
          Get Started
        </a>
      </div>
    {/if}
    
    <!-- Stats Grid -->
    <div class="stats-grid">
      <div class="stat-card card">
        <div class="stat-header">
          <span class="stat-label">Feedback Given</span>
          <MessageCircle size={20} />
        </div>
        <div class="stat-value">{isAuth ? (userCredential?.usedVotes?.length || 0) : '-'}</div>
        <div class="stat-trend">Your opinions shared</div>
      </div>
      <div class="stat-card card">
        <div class="stat-header">
          <span class="stat-label">Active Promises</span>
          <FileText size={20} />
        </div>
        <div class="stat-value">{manifestos.length}</div>
        <div class="stat-trend">Currently tracking</div>
      </div>
      <div class="stat-card card">
        <div class="stat-header">
          <span class="stat-label">Citizen Status</span>
          <Shield size={20} />
        </div>
        <div class="stat-value status-{isAuth ? 'verified' : 'pending'}">{isAuth ? 'Verified' : 'Not Yet'}</div>
        <div class="stat-trend">{isAuth ? 'Anonymous participation enabled' : 'Verify to participate'}</div>
      </div>
    </div>
    
    <!-- Verification Trust Banner -->
    <div class="verification-banner card">
      <div class="verification-content">
        <div class="verification-icon">
          <Shield size={28} />
        </div>
        <div class="verification-text">
          <h3>Verify Promise Hashes</h3>
          <p>Don't trust—verify! Check that any promise text matches its blockchain hash. Our system is designed so you never have to trust us.</p>
        </div>
      </div>
      <a href="/verify" class="verification-btn">
        <Shield size={18} />
        Verify Now
      </a>
    </div>
    
    <div class="content-grid">
      <!-- Featured Manifestos -->
      <section class="featured-section">
        <div class="section-header">
          <h2>
            <TrendingUp size={20} />
            Trending Promises
          </h2>
          <a href="/manifestos" class="view-all">View All →</a>
        </div>
        
        <div class="manifestos-list">
          {#if isLoading}
            <p class="loading">Loading promises...</p>
          {:else if manifestos.length === 0}
            <p class="empty">No promises found.</p>
          {:else}
            {#each manifestos as manifesto}
              <ManifestoCard {manifesto} />
            {/each}
          {/if}
        </div>
      </section>
      
      <!-- Recent Activity -->
      <aside class="activity-section">
        <div class="section-header">
          <h2>
            <Clock size={20} />
            Your Activity
          </h2>
        </div>
        
        {#if !isAuth}
          <!-- Not verified info card -->
          <div class="info-card card">
            <div class="info-icon">
              <Info size={24} />
            </div>
            <div class="info-content">
              <h4>Get Started</h4>
              <p>Verify as a citizen to share your opinions on promises anonymously.</p>
              <a href="/auth" class="info-btn">
                <Shield size={16} />
                Verify Now
              </a>
            </div>
          </div>
          
          <!-- How it works -->
          <div class="how-it-works card">
            <h4>How It Works</h4>
            <ul>
              <li>
                <CheckCircle size={16} />
                <span>Verify once anonymously</span>
              </li>
              <li>
                <MessageCircle size={16} />
                <span>Share opinions on promises</span>
              </li>
              <li>
                <Eye size={16} />
                <span>Track promise progress</span>
              </li>
            </ul>
            <p class="privacy-note">
              <Shield size={14} />
              Your identity stays private. Always.
            </p>
          </div>
        {:else}
          <div class="activity-list card">
            {#if recentActivity.length === 0}
              <p class="empty-activity">No recent activity yet. Start sharing your opinions on promises!</p>
            {:else}
              {#each recentActivity as activity}
                <div class="activity-item">
                  <div class="activity-icon">
                    <svelte:component this={activity.icon} size={18} />
                  </div>
                  <div class="activity-content">
                    <p>{activity.description}</p>
                    <span class="activity-time">{activity.time}</span>
                  </div>
                </div>
              {/each}
            {/if}
          </div>
          
          <!-- Nullifier Info -->
          <div class="nullifier-card card">
            <h4>
              <Shield size={16} />
              Your Anonymous ID
            </h4>
            <HashDisplay hash={userCredential?.nullifier || ''} />
            <p class="nullifier-note">
              This ID proves you're a verified citizen without revealing who you are.
            </p>
          </div>
        {/if}
      </aside>
    </div>
    
    <!-- Quick Actions -->
    <div class="quick-actions">
      <h2>Quick Actions</h2>
      <div class="actions-grid">
        <a href="/manifestos" class="action-card card">
          <FileText size={24} />
          <span>Browse Promises</span>
          <ChevronRight size={16} class="action-arrow" />
        </a>
        <a href={isAuth ? "/citizen/attestation" : "/auth"} class="action-card card">
          <MessageCircle size={24} />
          <span>Share Opinion</span>
          <ChevronRight size={16} class="action-arrow" />
        </a>
        <a href={isAuth ? "/citizen/votes" : "/auth"} class="action-card card">
          <CheckCircle size={24} />
          <span>My Votes</span>
          <ChevronRight size={16} class="action-arrow" />
        </a>
        <a href="/verify" class="action-card card verify-card">
          <Shield size={24} />
          <span>Verify Hash</span>
          <ChevronRight size={16} class="action-arrow" />
        </a>
        <a href="/audit-trail" class="action-card card">
          <Activity size={24} />
          <span>View Audit Trail</span>
          <ChevronRight size={16} class="action-arrow" />
        </a>
        <a href="/politicians" class="action-card card">
          <Users size={24} />
          <span>View Representatives</span>
          <ChevronRight size={16} class="action-arrow" />
        </a>
      </div>
    </div>
  </div>
</main>

<style>
  .citizen-page {
    min-height: 100vh;
    background: var(--gray-50);
    padding: var(--space-8) 0;
  }
  
  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 var(--space-4);
  }
  
  /* Page Header - Matches manifestos/politicians */
  .page-header {
    margin-bottom: var(--space-6);
  }
  
  .page-header h1 {
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--gray-900);
    margin-bottom: var(--space-2);
  }
  
  .page-header p {
    color: var(--gray-600);
    font-size: 1rem;
    max-width: 600px;
  }
  
  /* Auth Banner - Matches manifestos page */
  .auth-banner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-4);
    border-radius: var(--radius-lg);
    margin-bottom: var(--space-6);
    flex-wrap: wrap;
    gap: var(--space-3);
  }
  
  .auth-banner.verified {
    background: var(--success-50);
    border: 1px solid var(--success-200);
  }
  
  .auth-banner.info {
    background: var(--primary-50);
    border: 1px solid var(--primary-200);
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
    color: var(--primary-600);
  }
  
  .auth-info div {
    display: flex;
    flex-direction: column;
  }
  
  .auth-info strong {
    font-size: 0.9rem;
    color: var(--gray-900);
  }
  
  .auth-info span {
    font-size: 0.8rem;
    color: var(--gray-600);
  }
  
  .opinions-shared {
    display: flex;
    align-items: center;
    gap: var(--space-1);
    font-size: 0.85rem;
    color: var(--success-700);
    font-weight: 500;
  }
  
  .verify-btn {
    padding: var(--space-2) var(--space-4);
    background: var(--primary-600);
    color: white;
    border-radius: var(--radius-md);
    text-decoration: none;
    font-size: 0.875rem;
    font-weight: 500;
    transition: all 0.2s;
  }
  
  .verify-btn:hover {
    background: var(--primary-700);
  }
  
  /* Stats Grid - Matches manifestos page */
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: var(--space-4);
    margin-bottom: var(--space-8);
  }
  
  .stat-card {
    padding: var(--space-5);
  }
  
  .stat-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--space-2);
  }
  
  .stat-header .stat-label {
    font-size: 0.85rem;
    color: var(--gray-500);
    font-weight: 500;
  }
  
  .stat-header :global(svg) {
    color: var(--primary-500);
  }
  
  .stat-card .stat-value {
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--gray-900);
    margin-bottom: var(--space-1);
  }
  
  .stat-card .stat-value.status-verified {
    color: var(--success-600);
  }
  
  .stat-card .stat-value.status-pending {
    color: var(--gray-500);
  }
  
  .stat-trend {
    font-size: 0.75rem;
    color: var(--gray-500);
  }

  .loading, .empty {
    padding: var(--space-8);
    text-align: center;
    color: var(--gray-500);
  }
  
  .empty-activity {
    padding: var(--space-4);
    text-align: center;
    color: var(--gray-400);
    font-size: 0.875rem;
  }
  
  /* Content Grid */
  .content-grid {
    display: grid;
    gap: var(--space-6);
    margin-bottom: var(--space-8);
  }
  
  @media (min-width: 768px) {
    .content-grid {
      grid-template-columns: 1fr 320px;
    }
  }
  
  /* Section Headers */
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
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--gray-900);
  }
  
  .section-header h2 :global(svg) {
    color: var(--primary-600);
  }
  
  .view-all {
    font-size: 0.85rem;
    color: var(--primary-600);
    text-decoration: none;
    font-weight: 500;
  }
  
  .view-all:hover {
    text-decoration: underline;
  }
  
  /* Manifestos List */
  .manifestos-list {
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
  }
  
  /* Activity Section */
  .activity-list {
    padding: 0;
    margin-bottom: var(--space-4);
  }
  
  .activity-item {
    display: flex;
    gap: var(--space-3);
    padding: var(--space-4);
    border-bottom: 1px solid var(--gray-100);
  }
  
  .activity-item:last-child {
    border-bottom: none;
  }
  
  .activity-icon {
    width: 36px;
    height: 36px;
    background: var(--primary-50);
    color: var(--primary-600);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }
  
  .activity-content p {
    font-size: 0.875rem;
    margin-bottom: var(--space-1);
    color: var(--gray-700);
  }
  
  .activity-time {
    font-size: 0.75rem;
    color: var(--gray-400);
  }
  
  /* Info Card */
  .info-card {
    padding: var(--space-5);
    margin-bottom: var(--space-4);
  }
  
  .info-icon {
    width: 48px;
    height: 48px;
    background: var(--primary-50);
    color: var(--primary-600);
    border-radius: var(--radius-lg);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: var(--space-4);
  }
  
  .info-content h4 {
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: var(--space-2);
    color: var(--gray-900);
  }
  
  .info-content p {
    font-size: 0.875rem;
    color: var(--gray-600);
    margin-bottom: var(--space-4);
    line-height: 1.5;
  }
  
  .info-btn {
    display: inline-flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-2) var(--space-4);
    background: var(--primary-600);
    color: white;
    border-radius: var(--radius-md);
    text-decoration: none;
    font-size: 0.875rem;
    font-weight: 500;
    transition: all 0.2s;
  }
  
  .info-btn:hover {
    background: var(--primary-700);
  }
  
  /* How it works */
  .how-it-works {
    padding: var(--space-5);
    margin-bottom: var(--space-4);
  }
  
  .how-it-works h4 {
    font-size: 0.95rem;
    font-weight: 600;
    margin-bottom: var(--space-4);
    color: var(--gray-900);
  }
  
  .how-it-works ul {
    list-style: none;
    padding: 0;
    margin: 0 0 var(--space-4) 0;
  }
  
  .how-it-works li {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-2) 0;
    font-size: 0.875rem;
    color: var(--gray-700);
  }
  
  .how-it-works li :global(svg) {
    color: var(--success-500);
    flex-shrink: 0;
  }
  
  .privacy-note {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-3);
    background: var(--primary-50);
    color: var(--primary-700);
    border-radius: var(--radius-md);
    font-size: 0.8rem;
    font-weight: 500;
  }
  
  .privacy-note :global(svg) {
    color: var(--primary-600);
    flex-shrink: 0;
  }
  
  /* Nullifier Card */
  .nullifier-card {
    padding: var(--space-5);
  }
  
  .nullifier-card h4 {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    font-size: 0.9rem;
    font-weight: 600;
    margin-bottom: var(--space-3);
    color: var(--primary-700);
  }
  
  .nullifier-note {
    font-size: 0.75rem;
    color: var(--gray-500);
    line-height: 1.5;
    margin-top: var(--space-3);
  }
  
  /* Quick Actions */
  .quick-actions {
    margin-top: var(--space-8);
  }
  
  .quick-actions h2 {
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: var(--space-4);
    color: var(--gray-900);
  }
  
  .actions-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: var(--space-4);
  }
  
  .action-card {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-4) var(--space-5);
    text-decoration: none;
    color: var(--gray-700);
    transition: all 0.2s;
  }
  
  .action-card :global(svg:first-child) {
    color: var(--primary-500);
    flex-shrink: 0;
  }
  
  .action-card span {
    flex: 1;
    font-size: 0.9rem;
    font-weight: 500;
  }
  
  .action-card :global(.action-arrow) {
    color: var(--gray-400);
    transition: transform 0.2s;
  }
  
  .action-card:hover {
    border-color: var(--primary-300);
    background: var(--primary-50);
  }
  
  .action-card:hover :global(.action-arrow) {
    transform: translateX(4px);
    color: var(--primary-500);
  }
  
  /* Verification Banner */
  .verification-banner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-4);
    padding: var(--space-6);
    margin: var(--space-8) 0;
    background: linear-gradient(135deg, #082770 0%, #0a3490 100%);
    border: none;
    position: relative;
    overflow: hidden;
  }
  
  .verification-banner::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 200px;
    height: 200px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 50%;
  }
  
  .verification-content {
    display: flex;
    align-items: center;
    gap: var(--space-4);
    flex: 1;
    z-index: 1;
  }
  
  .verification-icon {
    width: 56px;
    height: 56px;
    background: rgba(255, 255, 255, 0.15);
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: var(--radius-xl);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }
  
  .verification-icon :global(svg) {
    color: white;
  }
  
  .verification-text h3 {
    font-size: 1.25rem;
    font-weight: 600;
    color: white;
    margin-bottom: var(--space-2);
  }
  
  .verification-text p {
    font-size: 0.875rem;
    color: rgba(255, 255, 255, 0.85);
    line-height: 1.5;
    max-width: 600px;
  }
  
  .verification-btn {
    display: inline-flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-3) var(--space-6);
    background: white;
    color: #082770;
    border-radius: var(--radius-lg);
    text-decoration: none;
    font-weight: 600;
    font-size: 0.95rem;
    transition: all 0.2s;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    z-index: 1;
    flex-shrink: 0;
  }
  
  .verification-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    background: #f8fafc;
  }
  
  .verification-btn :global(svg) {
    color: #082770;
  }
  
  /* Verify Action Card Highlight */
  .action-card.verify-card {
    background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
    border-color: #0ea5e9;
  }
  
  .action-card.verify-card :global(svg:first-child) {
    color: #0284c7;
  }
  
  .action-card.verify-card:hover {
    background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
    border-color: #0284c7;
    transform: translateY(-2px);
  }
  
  @media (max-width: 768px) {
    .verification-banner {
      flex-direction: column;
      text-align: center;
    }
    
    .verification-content {
      flex-direction: column;
      text-align: center;
    }
    
    .verification-text p {
      margin: 0 auto;
    }
  }
</style>
