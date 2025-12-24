<script lang="ts">
  import Header from '$lib/components/Header.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import CommentThread from '$lib/components/CommentThread.svelte';
  import VoteBox from '$lib/components/VoteBox.svelte';
  import HashDisplay from '$lib/components/HashDisplay.svelte';
  import { Shield, ThumbsUp, MessageSquare, Share2, ExternalLink, Clock, CheckCircle, Info, Search, Send } from 'lucide-svelte';
  
  // Sample manifesto data
  const manifesto = {
    id: '4992',
    title: 'Universal Basic Income Pilot',
    status: 'verified',
    hash: '0x7a82...9f2',
    merkleRoot: '0x3b...1c',
    description: 'This manifesto proposes a 2-year pilot program to introduce a universal basic income for all citizens, funded by a restructuring of existing tax brackets. The primary goal is to assess the impact on economic stability and entrepreneurship rates within the designated pilot zones.',
    details: 'All funding allocations will be transparently tracked via the attached smart contract addresses, ensuring real-time auditability of public funds.',
    voteCount: 12500,
    commentCount: 84,
    timeline: 'Discussion Phase (Ends in 4d)',
    quorum: 78,
    postedAgo: '2 days ago'
  };
  
  const comments = [
    {
      id: '1',
      content: 'While the funding model appears sound in the short term, has there been any modeling done on the impact of tax bracket restructuring on middle-income households specifically in the pilot zones? The whitepaper seems vague on this.',
      zkCredential: '0x4f...82',
      upvotes: 142,
      downvotes: 5,
      createdAt: '2024-10-14T14:32:00Z',
      isVerifiedCitizen: true,
      evidenceProof: 'tx_0x92f8...4a2b',
      replies: [
        {
          id: '1-1',
          content: 'Page 42 of the technical addendum addresses this. The bracket shift only affects the top 5% of earners in the zone. Middle income remains neutral.',
          zkCredential: '0xb2...9c',
          upvotes: 56,
          downvotes: 2,
          createdAt: '2024-10-14T12:15:00Z',
          isVerifiedCitizen: true,
          userRole: 'Verified Economist'
        }
      ]
    },
    {
      id: '2',
      content: 'I support this fully. It\'s time we test UBI in a controlled environment. The current welfare systems are bloated and inefficient.',
      zkCredential: '0x88...1f',
      upvotes: 89,
      downvotes: 12,
      createdAt: '2024-10-14T10:00:00Z',
      isVerifiedCitizen: true
    }
  ];
  
  let newComment = '';
  let commentSortBy = 'top';
</script>

<svelte:head>
  <title>{manifesto.title} - PromiseThread</title>
</svelte:head>

<Header variant="citizen" />

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
              <HashDisplay hash={manifesto.merkleRoot} />
            </div>
            <a href="#" class="view-proof">View On-Chain Proof ↗</a>
          </div>
          
          <p class="description">{manifesto.description}</p>
          <p class="details">{manifesto.details}</p>
          
          <div class="manifesto-stats">
            <div class="stat">
              <ThumbsUp size={18} />
              <span>{(manifesto.voteCount / 1000).toFixed(1)}k Votes</span>
            </div>
            <div class="stat">
              <MessageSquare size={18} />
              <span>{manifesto.commentCount} Comments</span>
            </div>
            <button class="share-btn">
              <Share2 size={18} />
              Share
            </button>
          </div>
        </div>
        
        <!-- Comment Input -->
        <div class="comment-input card">
          <div class="input-header">
            <div class="avatar-placeholder"></div>
            <div class="input-wrapper">
              <input 
                type="text" 
                placeholder="Enter your argument..."
                bind:value={newComment}
              />
            </div>
          </div>
          <div class="input-footer">
            <div class="posting-as">
              <Shield size={14} />
              <span>Posting anonymously as</span>
              <HashDisplay hash="0x8a...3f" copyable={false} />
              <span class="nullifier-label">(Nullifier ID)</span>
            </div>
            <button class="btn btn-primary">
              <Send size={16} />
              Sign & Post
            </button>
          </div>
        </div>
        
        <!-- Discussion -->
        <div class="discussion card">
          <div class="discussion-header">
            <h3>Discussion</h3>
            <div class="sort-tabs">
              <button 
                class="sort-btn" 
                class:active={commentSortBy === 'top'}
                on:click={() => commentSortBy = 'top'}
              >Top</button>
              <button 
                class="sort-btn" 
                class:active={commentSortBy === 'newest'}
                on:click={() => commentSortBy = 'newest'}
              >Newest</button>
              <button 
                class="sort-btn" 
                class:active={commentSortBy === 'controversial'}
                on:click={() => commentSortBy = 'controversial'}
              >Controversial</button>
            </div>
          </div>
          
          <div class="comments-list">
            {#each comments as comment}
              <CommentThread {comment} />
            {/each}
          </div>
        </div>
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
              {manifesto.timeline}
            </div>
          </div>
          
          <div class="sidebar-section">
            <span class="section-label">QUORUM REACHED</span>
            <div class="quorum-bar">
              <div class="quorum-fill" style="width: {manifesto.quorum}%"></div>
            </div>
            <span class="quorum-text">{manifesto.quorum}% Verified</span>
          </div>
          
          <div class="sidebar-section">
            <span class="section-label">IMMUTABLE ID</span>
            <HashDisplay hash={manifesto.hash} />
          </div>
        </div>
        
        <!-- Discussion Rules -->
        <div class="sidebar-card card">
          <h4>Discussion Rules</h4>
          <ul class="rules-list">
            <li>
              <Shield size={14} />
              All comments are cryptographically signed. You cannot edit or delete after 5 minutes.
            </li>
            <li>
              <Shield size={14} />
              Identities are hidden, but your reputation is persistent via Nullifier Hash.
            </li>
            <li>
              <Shield size={14} />
              Civil discourse is enforced by community consensus voting.
            </li>
          </ul>
        </div>
        
        <!-- Related Proposals -->
        <div class="sidebar-card card">
          <h4>Related Proposals</h4>
          <div class="related-list">
            <a href="#" class="related-item">
              <span class="related-id">#4011</span>
              <span class="related-title">Digital ID Implementation</span>
              <span class="related-status closed">Closed</span>
            </a>
            <a href="#" class="related-item">
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

<Footer />

<style>
  .manifesto-detail {
    min-height: 100vh;
    background: var(--gray-50);
    padding: var(--space-6) 0;
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
