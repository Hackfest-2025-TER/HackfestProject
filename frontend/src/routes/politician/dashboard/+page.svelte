<script lang="ts">
  import { Shield, FileText, Users, Settings, BarChart3, LogOut, CheckCircle, TrendingUp, Vote, Eye } from 'lucide-svelte';
  import HashDisplay from '$lib/components/HashDisplay.svelte';
  import ManifestoCard from '$lib/components/ManifestoCard.svelte';
  
  // Politician data
  const politician = {
    name: 'Senator Doe',
    id: '0x4a...9f2',
    avatarUrl: null,
    integrityScore: 98,
    manifestosAudited: 12,
    voteParticipation: 95
  };
  
  // Sample manifesto data
  const manifesto = {
    id: 'MAN-2024-0042',
    title: 'Economic Reform 2024',
    description: 'A comprehensive framework for revitalizing the national economy through tax incentives for small businesses, digital currency integration, and sustainable energy subsidies.',
    status: 'active',
    publicationDate: 'Oct 12, 2024',
    blockHeight: 19402112,
    manifestoHash: '0x7f8a93a2b1c9d8e7f6a5b4c3d2e1'
  };
  
  const comments = [
    {
      id: '1',
      author: 'Verified Citizen',
      zkCredential: '0x8a...99',
      date: 'Oct 14, 2024 • 14:32 UTC',
      content: 'This proposal fails to address the rural transport deficit sufficiently. While the tax incentives are a good start for urban centers, Section 4 needs a dedicated clause for agricultural supply chain logistics. Without it, the economic reform remains unbalanced.',
      evidenceProof: 'tx_0x92f8...4a2b'
    },
    {
      id: '2',
      author: 'Verified Citizen',
      zkCredential: '0x3b...11',
      date: 'Oct 14, 2024 • 12:15 UTC',
      content: 'Strongly agree with the digital currency integration points. It\'s about time we modernized the treasury systems. Transparency is key here.',
      evidenceProof: 'tx_0x11a7...88e3'
    }
  ];
  
  let activeNav = 'manifestos';
</script>

<svelte:head>
  <title>Politician Audit Portal - PromiseThread</title>
</svelte:head>

<div class="dashboard-layout">
  <!-- Sidebar -->
  <aside class="sidebar">
    <div class="sidebar-header">
      <div class="user-info">
        <div class="avatar">
          {politician.name[0]}
        </div>
        <div class="user-details">
          <span class="user-name">{politician.name}</span>
          <span class="user-id">ID: {politician.id}</span>
        </div>
      </div>
    </div>
    
    <nav class="sidebar-nav">
      <a href="/politician/dashboard" class="nav-item" class:active={activeNav === 'dashboard'}>
        <BarChart3 size={18} />
        Dashboard
      </a>
      <a href="/politician/manifestos" class="nav-item" class:active={activeNav === 'manifestos'}>
        <FileText size={18} />
        Manifestos
      </a>
      <a href="/politician/voters" class="nav-item" class:active={activeNav === 'voters'}>
        <Users size={18} />
        Voters
      </a>
      <a href="/politician/audit-logs" class="nav-item" class:active={activeNav === 'audit-logs'}>
        <Eye size={18} />
        Audit Logs
      </a>
      <a href="/politician/settings" class="nav-item" class:active={activeNav === 'settings'}>
        <Settings size={18} />
        Settings
      </a>
    </nav>
    
    <div class="sidebar-footer">
      <button class="logout-btn">
        <LogOut size={18} />
        Secure Logout
      </button>
    </div>
  </aside>
  
  <!-- Main Content -->
  <main class="main-content">
    <!-- Header -->
    <header class="content-header">
      <div class="header-left">
        <Shield size={24} />
        <h1>Politician Audit Portal</h1>
      </div>
      <div class="header-right">
        <span class="node-status">
          <span class="status-dot online"></span>
          Node: Active
        </span>
        <button class="icon-btn">🔔</button>
      </div>
    </header>
    
    <!-- Breadcrumb -->
    <div class="breadcrumb">
      <a href="/politician/dashboard">Dashboard</a>
      <span>/</span>
      <a href="/politician/manifestos">Manifestos</a>
      <span>/</span>
      <span class="current">Economic Reform 2024</span>
    </div>
    
    <!-- Manifesto Detail -->
    <div class="manifesto-detail">
      <div class="detail-header">
        <div class="status-row">
          <span class="status-badge active">ACTIVE</span>
          <span class="manifesto-id">ID: {manifesto.id}</span>
        </div>
        <a href="#" class="view-doc">↗ View Original Document</a>
      </div>
      
      <h2>{manifesto.title}</h2>
      <p class="description">{manifesto.description}</p>
      
      <div class="meta-grid">
        <div class="meta-item">
          <span class="meta-label">PUBLICATION DATE</span>
          <span class="meta-value">{manifesto.publicationDate}</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">BLOCK HEIGHT</span>
          <span class="meta-value">#{manifesto.blockHeight.toLocaleString()}</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">MANIFESTO HASH</span>
          <HashDisplay hash={manifesto.manifestoHash} />
        </div>
      </div>
    </div>
    
    <!-- Comments Section -->
    <div class="comments-section">
      <div class="comments-header">
        <div class="comments-title">
          <h3>Citizen Comments</h3>
          <span class="comment-count">142</span>
        </div>
        <div class="comments-controls">
          <div class="search-box">
            <input type="text" placeholder="Search comments..." />
          </div>
          <button class="sort-btn">
            ≡ Newest First
          </button>
        </div>
      </div>
      
      <div class="comments-list">
        {#each comments as comment}
          <div class="comment-item">
            <div class="comment-avatar">
              <Users size={20} />
            </div>
            <div class="comment-content">
              <div class="comment-header">
                <span class="author">{comment.author}</span>
                <HashDisplay hash={comment.zkCredential} copyable={false} />
                <span class="date">{comment.date}</span>
              </div>
              <p class="comment-text">{comment.content}</p>
              <div class="evidence">
                <span class="evidence-label">EVIDENCE PROOF:</span>
                <a href="#" class="evidence-link">{comment.evidenceProof}</a>
              </div>
            </div>
            <button class="copy-btn" title="Copy">📋</button>
          </div>
        {/each}
      </div>
    </div>
  </main>
</div>

<style>
  .dashboard-layout {
    display: flex;
    min-height: 100vh;
    background: var(--gray-50);
  }
  
  /* Sidebar */
  .sidebar {
    width: 260px;
    background: white;
    border-right: 1px solid var(--gray-200);
    display: flex;
    flex-direction: column;
    position: sticky;
    top: 0;
    height: 100vh;
  }
  
  .sidebar-header {
    padding: var(--space-6);
    border-bottom: 1px solid var(--gray-200);
  }
  
  .user-info {
    display: flex;
    align-items: center;
    gap: var(--space-3);
  }
  
  .avatar {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: var(--primary-100);
    color: var(--primary-700);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 1.25rem;
  }
  
  .user-details {
    display: flex;
    flex-direction: column;
  }
  
  .user-name {
    font-weight: 600;
    color: var(--gray-900);
  }
  
  .user-id {
    font-size: 0.75rem;
    font-family: var(--font-mono);
    color: var(--gray-500);
  }
  
  .sidebar-nav {
    flex: 1;
    padding: var(--space-4);
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
  }
  
  .nav-item {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-3) var(--space-4);
    color: var(--gray-600);
    text-decoration: none;
    border-radius: var(--radius-lg);
    font-size: 0.875rem;
    font-weight: 500;
    transition: all 0.2s;
  }
  
  .nav-item:hover {
    background: var(--gray-100);
    color: var(--gray-900);
  }
  
  .nav-item.active {
    background: var(--primary-50);
    color: var(--primary-700);
  }
  
  .sidebar-footer {
    padding: var(--space-4);
    border-top: 1px solid var(--gray-200);
  }
  
  .logout-btn {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    width: 100%;
    padding: var(--space-3);
    border: none;
    background: transparent;
    color: var(--gray-500);
    font-size: 0.875rem;
    cursor: pointer;
    border-radius: var(--radius-lg);
  }
  
  .logout-btn:hover {
    background: var(--gray-100);
    color: var(--gray-700);
  }
  
  /* Main Content */
  .main-content {
    flex: 1;
    padding: var(--space-6);
    overflow-y: auto;
  }
  
  .content-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--space-4);
  }
  
  .header-left {
    display: flex;
    align-items: center;
    gap: var(--space-3);
  }
  
  .header-left h1 {
    font-size: 1.25rem;
  }
  
  .header-right {
    display: flex;
    align-items: center;
    gap: var(--space-4);
  }
  
  .node-status {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-2) var(--space-3);
    background: var(--gray-100);
    border-radius: var(--radius-full);
    font-size: 0.8rem;
    color: var(--gray-600);
  }
  
  .status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
  }
  
  .status-dot.online {
    background: var(--success-500);
  }
  
  .icon-btn {
    width: 40px;
    height: 40px;
    border: 1px solid var(--gray-200);
    background: white;
    border-radius: var(--radius-lg);
    cursor: pointer;
  }
  
  /* Breadcrumb */
  .breadcrumb {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    font-size: 0.875rem;
    margin-bottom: var(--space-6);
  }
  
  .breadcrumb a {
    color: var(--gray-500);
    text-decoration: none;
  }
  
  .breadcrumb a:hover {
    color: var(--primary-600);
  }
  
  .breadcrumb span {
    color: var(--gray-400);
  }
  
  .breadcrumb .current {
    color: var(--gray-900);
    font-weight: 500;
  }
  
  /* Manifesto Detail */
  .manifesto-detail {
    background: white;
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-xl);
    padding: var(--space-6);
    margin-bottom: var(--space-6);
  }
  
  .detail-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--space-4);
  }
  
  .status-row {
    display: flex;
    align-items: center;
    gap: var(--space-3);
  }
  
  .status-badge {
    padding: var(--space-1) var(--space-2);
    font-size: 0.7rem;
    font-weight: 600;
    border-radius: var(--radius-sm);
  }
  
  .status-badge.active {
    background: var(--success-100);
    color: var(--success-700);
  }
  
  .manifesto-id {
    font-size: 0.8rem;
    color: var(--gray-500);
    font-family: var(--font-mono);
  }
  
  .view-doc {
    font-size: 0.875rem;
    color: var(--primary-600);
    text-decoration: none;
  }
  
  .manifesto-detail h2 {
    font-size: 1.5rem;
    margin-bottom: var(--space-3);
  }
  
  .description {
    color: var(--gray-600);
    line-height: 1.6;
    margin-bottom: var(--space-6);
  }
  
  .meta-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: var(--space-4);
    padding-top: var(--space-4);
    border-top: 1px solid var(--gray-200);
  }
  
  .meta-item {
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
  }
  
  .meta-label {
    font-size: 0.65rem;
    font-weight: 600;
    color: var(--gray-400);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  
  .meta-value {
    font-size: 0.875rem;
    color: var(--gray-900);
    font-weight: 500;
  }
  
  /* Comments Section */
  .comments-section {
    background: white;
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-xl);
    overflow: hidden;
  }
  
  .comments-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-4) var(--space-6);
    border-bottom: 1px solid var(--gray-200);
    flex-wrap: wrap;
    gap: var(--space-3);
  }
  
  .comments-title {
    display: flex;
    align-items: center;
    gap: var(--space-2);
  }
  
  .comments-title h3 {
    font-size: 1rem;
  }
  
  .comment-count {
    padding: var(--space-1) var(--space-2);
    background: var(--gray-100);
    border-radius: var(--radius-full);
    font-size: 0.75rem;
    color: var(--gray-600);
  }
  
  .comments-controls {
    display: flex;
    gap: var(--space-3);
  }
  
  .search-box input {
    padding: var(--space-2) var(--space-3);
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-lg);
    font-size: 0.8rem;
    width: 200px;
  }
  
  .sort-btn {
    padding: var(--space-2) var(--space-3);
    border: 1px solid var(--gray-200);
    background: white;
    border-radius: var(--radius-lg);
    font-size: 0.8rem;
    color: var(--gray-600);
    cursor: pointer;
  }
  
  .comments-list {
    max-height: 500px;
    overflow-y: auto;
  }
  
  .comment-item {
    display: flex;
    gap: var(--space-4);
    padding: var(--space-5) var(--space-6);
    border-bottom: 1px solid var(--gray-100);
  }
  
  .comment-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: var(--gray-100);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--gray-500);
    flex-shrink: 0;
  }
  
  .comment-content {
    flex: 1;
  }
  
  .comment-header {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    margin-bottom: var(--space-2);
    flex-wrap: wrap;
  }
  
  .author {
    font-weight: 600;
    color: var(--gray-900);
  }
  
  .date {
    font-size: 0.75rem;
    color: var(--gray-400);
  }
  
  .comment-text {
    font-size: 0.875rem;
    color: var(--gray-700);
    line-height: 1.6;
    margin-bottom: var(--space-3);
  }
  
  .evidence {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    font-size: 0.75rem;
  }
  
  .evidence-label {
    color: var(--gray-400);
  }
  
  .evidence-link {
    color: var(--success-600);
    font-family: var(--font-mono);
  }
  
  .copy-btn {
    width: 36px;
    height: 36px;
    border: none;
    background: transparent;
    cursor: pointer;
    border-radius: var(--radius-md);
    opacity: 0.5;
  }
  
  .copy-btn:hover {
    background: var(--gray-100);
    opacity: 1;
  }
</style>
