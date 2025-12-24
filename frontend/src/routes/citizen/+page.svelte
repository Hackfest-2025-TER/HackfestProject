<script lang="ts">
  import Header from '$lib/components/Header.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import ManifestoCard from '$lib/components/ManifestoCard.svelte';
  import HashDisplay from '$lib/components/HashDisplay.svelte';
  import { Shield, FileText, CheckCircle, Clock, Activity, TrendingUp, Eye } from 'lucide-svelte';
  
  // Sample user data
  const user = {
    nullifierId: '0x8a72f92b...c4d1',
    sessionId: 'SES-2024-0827',
    votesSubmitted: 12,
    manifestosViewed: 34,
    commentsMade: 8
  };
  
  // Sample recent activity
  const recentActivity = [
    { type: 'vote', description: 'Voted on "Universal Healthcare Act"', time: '2 hours ago', icon: CheckCircle },
    { type: 'comment', description: 'Commented on "Green Energy Initiative"', time: '5 hours ago', icon: FileText },
    { type: 'view', description: 'Viewed "Education Reform Bill"', time: '1 day ago', icon: Eye }
  ];
  
  // Featured manifestos
  const featuredManifestos = [
    {
      id: '1',
      title: 'Universal Healthcare Act',
      politicianName: 'Jane Doe',
      party: 'Progressive Party',
      category: 'Healthcare',
      status: 'pending',
      integrityScore: 94,
      voteCount: 1450,
      commentCount: 89
    },
    {
      id: '2',
      title: 'North-South Rail Link',
      politicianName: 'Jane Doe',
      party: 'Progressive Party',
      category: 'Infrastructure',
      status: 'pending',
      integrityScore: 87,
      voteCount: 1048,
      commentCount: 56
    }
  ];
</script>

<svelte:head>
  <title>Citizen Dashboard - PromiseThread</title>
</svelte:head>

<Header variant="citizen" />

<main class="citizen-dashboard">
  <div class="container">
    <!-- Welcome Banner -->
    <div class="welcome-banner card">
      <div class="banner-content">
        <div class="banner-icon">
          <Shield size={32} />
        </div>
        <div class="banner-text">
          <h1>Welcome, Citizen</h1>
          <p>Your identity is protected by zero-knowledge proofs. All actions are anonymous.</p>
        </div>
      </div>
      <div class="session-info">
        <span class="status-indicator online"></span>
        <span class="session-label">Session ID:</span>
        <code>{user.sessionId}</code>
      </div>
    </div>
    
    <!-- Stats Grid -->
    <div class="stats-grid">
      <div class="stat-card">
        <CheckCircle size={24} />
        <div class="stat-content">
          <span class="stat-value">{user.votesSubmitted}</span>
          <span class="stat-label">Votes Submitted</span>
        </div>
      </div>
      <div class="stat-card">
        <FileText size={24} />
        <div class="stat-content">
          <span class="stat-value">{user.manifestosViewed}</span>
          <span class="stat-label">Manifestos Viewed</span>
        </div>
      </div>
      <div class="stat-card">
        <Activity size={24} />
        <div class="stat-content">
          <span class="stat-value">{user.commentsMade}</span>
          <span class="stat-label">Comments Made</span>
        </div>
      </div>
    </div>
    
    <div class="content-grid">
      <!-- Featured Manifestos -->
      <section class="featured-section">
        <div class="section-header">
          <h2>
            <TrendingUp size={20} />
            Trending Manifestos
          </h2>
          <a href="/manifestos" class="view-all">View All →</a>
        </div>
        
        <div class="manifestos-list">
          {#each featuredManifestos as manifesto}
            <a href="/manifestos/{manifesto.id}" class="manifesto-item card">
              <div class="manifesto-header">
                <span class="category-badge">{manifesto.category}</span>
                <span class="integrity-badge">
                  {manifesto.integrityScore}% Integrity
                </span>
              </div>
              <h3>{manifesto.title}</h3>
              <p class="politician-info">by {manifesto.politicianName} · {manifesto.party}</p>
              <div class="manifesto-stats">
                <span class="stat">
                  <CheckCircle size={14} />
                  {manifesto.voteCount} votes
                </span>
                <span class="stat">
                  <FileText size={14} />
                  {manifesto.commentCount} comments
                </span>
              </div>
            </a>
          {/each}
        </div>
      </section>
      
      <!-- Recent Activity -->
      <aside class="activity-section">
        <div class="section-header">
          <h2>
            <Clock size={20} />
            Recent Activity
          </h2>
        </div>
        
        <div class="activity-list card">
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
        </div>
        
        <!-- Nullifier Info -->
        <div class="nullifier-card card">
          <h4>
            <Shield size={16} />
            Your Anonymous ID
          </h4>
          <HashDisplay hash={user.nullifierId} />
          <p class="nullifier-note">
            This nullifier proves you're a verified citizen without revealing your identity.
          </p>
        </div>
      </aside>
    </div>
    
    <!-- Quick Actions -->
    <div class="quick-actions">
      <h2>Quick Actions</h2>
      <div class="actions-grid">
        <a href="/manifestos" class="action-card">
          <FileText size={24} />
          <span>Browse Manifestos</span>
        </a>
        <a href="/citizen/attestation" class="action-card">
          <CheckCircle size={24} />
          <span>Submit Attestation</span>
        </a>
        <a href="/audit-trail" class="action-card">
          <Activity size={24} />
          <span>View Audit Trail</span>
        </a>
        <a href="/settings" class="action-card">
          <Shield size={24} />
          <span>Privacy Settings</span>
        </a>
      </div>
    </div>
  </div>
</main>

<Footer />

<style>
  .citizen-dashboard {
    min-height: 100vh;
    background: var(--gray-50);
    padding-bottom: var(--space-12);
  }
  
  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: var(--space-6) var(--space-4);
  }
  
  /* Welcome Banner */
  .welcome-banner {
    padding: var(--space-6);
    margin-bottom: var(--space-6);
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: var(--space-4);
    background: linear-gradient(135deg, var(--primary-50), white);
    border: 1px solid var(--primary-100);
  }
  
  .banner-content {
    display: flex;
    align-items: center;
    gap: var(--space-4);
  }
  
  .banner-icon {
    width: 56px;
    height: 56px;
    background: var(--primary-100);
    color: var(--primary-600);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .banner-text h1 {
    font-size: 1.5rem;
    margin-bottom: var(--space-1);
  }
  
  .banner-text p {
    color: var(--gray-500);
    font-size: 0.9rem;
  }
  
  .session-info {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-2) var(--space-4);
    background: white;
    border-radius: var(--radius-lg);
    border: 1px solid var(--gray-200);
  }
  
  .status-indicator {
    width: 8px;
    height: 8px;
    border-radius: 50%;
  }
  
  .status-indicator.online {
    background: var(--success-500);
  }
  
  .session-label {
    font-size: 0.75rem;
    color: var(--gray-500);
  }
  
  .session-info code {
    font-family: var(--font-mono);
    font-size: 0.75rem;
    color: var(--gray-700);
  }
  
  /* Stats Grid */
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: var(--space-4);
    margin-bottom: var(--space-8);
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
  
  .stat-card :global(svg) {
    color: var(--primary-600);
  }
  
  .stat-content {
    display: flex;
    flex-direction: column;
  }
  
  .stat-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--gray-900);
  }
  
  .stat-label {
    font-size: 0.8rem;
    color: var(--gray-500);
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
  }
  
  .section-header h2 :global(svg) {
    color: var(--primary-600);
  }
  
  .view-all {
    font-size: 0.85rem;
    color: var(--primary-600);
    text-decoration: none;
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
  
  .manifesto-item {
    padding: var(--space-5);
    text-decoration: none;
    color: inherit;
    transition: all 0.2s;
  }
  
  .manifesto-item:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
  }
  
  .manifesto-header {
    display: flex;
    gap: var(--space-2);
    margin-bottom: var(--space-3);
  }
  
  .category-badge {
    padding: var(--space-1) var(--space-2);
    background: var(--gray-100);
    color: var(--gray-600);
    font-size: 0.65rem;
    font-weight: 600;
    border-radius: var(--radius-sm);
    text-transform: uppercase;
  }
  
  .integrity-badge {
    padding: var(--space-1) var(--space-2);
    background: var(--success-100);
    color: var(--success-700);
    font-size: 0.65rem;
    font-weight: 600;
    border-radius: var(--radius-sm);
  }
  
  .manifesto-item h3 {
    font-size: 1rem;
    margin-bottom: var(--space-2);
  }
  
  .politician-info {
    font-size: 0.85rem;
    color: var(--gray-500);
    margin-bottom: var(--space-3);
  }
  
  .manifesto-stats {
    display: flex;
    gap: var(--space-4);
  }
  
  .manifesto-stats .stat {
    display: flex;
    align-items: center;
    gap: var(--space-1);
    font-size: 0.8rem;
    color: var(--gray-500);
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
  }
  
  .activity-time {
    font-size: 0.75rem;
    color: var(--gray-400);
  }
  
  /* Nullifier Card */
  .nullifier-card {
    padding: var(--space-4);
  }
  
  .nullifier-card h4 {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    font-size: 0.85rem;
    margin-bottom: var(--space-3);
    color: var(--primary-600);
  }
  
  .nullifier-note {
    font-size: 0.75rem;
    color: var(--gray-500);
    line-height: 1.5;
    margin-top: var(--space-3);
  }
  
  /* Quick Actions */
  .quick-actions h2 {
    font-size: 1.1rem;
    margin-bottom: var(--space-4);
  }
  
  .actions-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: var(--space-4);
  }
  
  .action-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-6);
    background: white;
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-xl);
    text-decoration: none;
    color: var(--gray-600);
    transition: all 0.2s;
  }
  
  .action-card:hover {
    border-color: var(--primary-500);
    color: var(--primary-600);
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
  }
  
  .action-card span {
    font-size: 0.85rem;
    font-weight: 500;
    text-align: center;
  }
</style>
