<script lang="ts">
  import Header from '$lib/components/Header.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import { Shield, Database, FileText, Link2, CheckCircle, Users, Vote, Search, ChevronRight } from 'lucide-svelte';
</script>

<svelte:head>
  <title>PromiseThread - Transparency by Design</title>
</svelte:head>

<Header variant="default" />

<main>
  <!-- Hero Section -->
  <section class="hero">
    <div class="container">
      <div class="hero-content">
        <h1>Transparency by Design.</h1>
        <p class="hero-subtitle">
          PromiseThread isn't just a website; it's a verifiable ledger of political accountability. 
          We use advanced cryptography to ensure every promise is tracked and every vote is counted 
          without compromising your privacy.
        </p>
        <a href="/manifestos" class="btn btn-primary btn-lg">View Manifestos</a>
      </div>
      <div class="hero-image">
        <div class="blockchain-graphic">
          <div class="chain-link"></div>
          <div class="chain-link"></div>
          <div class="chain-link"></div>
        </div>
      </div>
    </div>
  </section>

  <!-- Core Technologies -->
  <section class="section tech-section">
    <div class="container">
      <h2>Core Technologies</h2>
      <p class="section-subtitle">The pillars of our trustless architecture.</p>
      
      <div class="tech-grid">
        <div class="tech-card card">
          <div class="tech-icon">
            <Shield size={24} />
          </div>
          <h3>Zero-Knowledge Proofs</h3>
          <p>
            Our "ZK" authentication allows you to mathematically prove you are a registered 
            citizen without ever revealing your name or ID to our servers.
          </p>
        </div>
        
        <div class="tech-card card">
          <div class="tech-icon">
            <Database size={24} />
          </div>
          <h3>Hybrid Storage</h3>
          <p>
            We balance speed and security. Critical data like votes are stored on an immutable 
            ledger, while discussions happen off-chain for real-time speed.
          </p>
        </div>
        
        <div class="tech-card card">
          <div class="tech-icon">
            <FileText size={24} />
          </div>
          <h3>Audit Trail</h3>
          <p>
            Every promise update and vote tally is cryptographically signed. Anyone can download 
            the chain data to verify the integrity of the platform.
          </p>
        </div>
      </div>
    </div>
  </section>

  <!-- Where Data Lives -->
  <section class="section data-section">
    <div class="container">
      <h2>Where Data Lives</h2>
      <p class="section-subtitle">
        Understanding the distinction between On-Chain (The Truth) and Off-Chain 
        (The Conversation) is key to how we maintain trust.
      </p>
      
      <div class="data-grid">
        <div class="data-card on-chain">
          <div class="data-icon">
            <Link2 size={24} />
          </div>
          <h3>On-Chain (The Ledger)</h3>
          <span class="data-badge">IMMUTABLE & PUBLIC</span>
          <ul class="data-list">
            <li><CheckCircle size={16} /> Manifesto Promises</li>
            <li><CheckCircle size={16} /> Final Vote Tallies</li>
            <li><CheckCircle size={16} /> Politician Verifications</li>
          </ul>
        </div>
        
        <div class="data-card off-chain">
          <div class="data-icon">
            <Database size={24} />
          </div>
          <h3>Off-Chain (The Town Hall)</h3>
          <span class="data-badge gray">FAST & SCALABLE</span>
          <ul class="data-list gray">
            <li><CheckCircle size={16} /> User Comments & Debates</li>
            <li><CheckCircle size={16} /> Profile Images & Bio Text</li>
            <li><CheckCircle size={16} /> Notification Systems</li>
          </ul>
        </div>
      </div>
    </div>
  </section>

  <!-- Promise Lifecycle -->
  <section class="section lifecycle-section">
    <div class="container">
      <h2>The Life of a Promise</h2>
      
      <div class="timeline">
        <div class="timeline-item">
          <div class="timeline-number">1</div>
          <div class="timeline-content">
            <h4>Proposal & Draft</h4>
            <p>A politician drafts a manifesto. At this stage, it is off-chain and open for feedback from the community.</p>
          </div>
        </div>
        
        <div class="timeline-item">
          <div class="timeline-number">2</div>
          <div class="timeline-content">
            <h4>Immutable Commitment</h4>
            <p>The finalized promise is hashed and stored on the blockchain. It can no longer be edited or deleted without leaving a trace.</p>
          </div>
        </div>
        
        <div class="timeline-item">
          <div class="timeline-number">3</div>
          <div class="timeline-content">
            <h4>Citizen Voting</h4>
            <p>Verified citizens cast votes on the priority and feasibility of the promise.</p>
          </div>
        </div>
        
        <div class="timeline-item">
          <div class="timeline-number">4</div>
          <div class="timeline-content">
            <h4>Execution & Audit</h4>
            <p>Over the term, journalists and auditors submit evidence linked to the promise. The status is updated based on verifiable proof.</p>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Vote Integrity Flow -->
  <section class="section integrity-section">
    <div class="container">
      <h2>Vote Integrity Flow</h2>
      
      <div class="flow-grid">
        <div class="flow-card">
          <div class="flow-icon">
            <Users size={24} />
          </div>
          <h4>1. Authenticate</h4>
          <p>User logs in via Government ID or BankID. ZK Proof is generated locally.</p>
        </div>
        
        <div class="flow-connector">→</div>
        
        <div class="flow-card">
          <div class="flow-icon">
            <Shield size={24} />
          </div>
          <h4>2. Tokenize</h4>
          <p>System issues a one-time voting token. The link to your ID is destroyed.</p>
        </div>
        
        <div class="flow-connector">→</div>
        
        <div class="flow-card">
          <div class="flow-icon">
            <Vote size={24} />
          </div>
          <h4>3. Cast Vote</h4>
          <p>The token is used to sign the vote on the ledger. Your vote is public; your name is not.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- CTA Section -->
  <section class="section cta-section">
    <div class="container">
      <div class="cta-content">
        <Shield size={48} />
        <h2>Ready to verify democracy?</h2>
        <p>
          Join thousands of citizens who are taking control of the narrative. 
          No hidden agendas, just verifiable truth.
        </p>
        <div class="cta-buttons">
          <a href="/manifestos" class="btn btn-primary btn-lg">Explore Manifestos</a>
          <a href="/whitepaper" class="btn btn-secondary btn-lg">Read Whitepaper</a>
        </div>
      </div>
    </div>
  </section>
</main>

<Footer />

<style>
  main {
    min-height: 100vh;
  }
  
  .section {
    padding: var(--space-16) 0;
  }
  
  .section h2 {
    text-align: center;
    margin-bottom: var(--space-2);
  }
  
  .section-subtitle {
    text-align: center;
    color: var(--gray-500);
    max-width: 600px;
    margin: 0 auto var(--space-10);
  }
  
  /* Hero */
  .hero {
    padding: var(--space-12) 0;
    background: white;
  }
  
  .hero .container {
    display: grid;
    gap: var(--space-8);
    align-items: center;
  }
  
  @media (min-width: 768px) {
    .hero .container {
      grid-template-columns: 1fr 1fr;
    }
  }
  
  .hero h1 {
    font-size: 2.5rem;
    line-height: 1.1;
    margin-bottom: var(--space-4);
  }
  
  @media (min-width: 768px) {
    .hero h1 {
      font-size: 3.5rem;
    }
  }
  
  .hero-subtitle {
    color: var(--gray-600);
    margin-bottom: var(--space-6);
    font-size: 1.125rem;
    line-height: 1.7;
  }
  
  .hero-image {
    display: flex;
    justify-content: center;
  }
  
  .blockchain-graphic {
    display: flex;
    gap: var(--space-4);
    padding: var(--space-8);
    background: linear-gradient(135deg, var(--primary-50), var(--gray-100));
    border-radius: var(--radius-2xl);
  }
  
  .chain-link {
    width: 60px;
    height: 60px;
    background: var(--primary-500);
    border-radius: var(--radius-lg);
    opacity: 0.8;
  }
  
  .chain-link:nth-child(2) {
    opacity: 0.6;
  }
  
  .chain-link:nth-child(3) {
    opacity: 0.4;
  }
  
  /* Tech Section */
  .tech-section {
    background: var(--gray-50);
  }
  
  .tech-grid {
    display: grid;
    gap: var(--space-6);
  }
  
  @media (min-width: 768px) {
    .tech-grid {
      grid-template-columns: repeat(3, 1fr);
    }
  }
  
  .tech-card {
    padding: var(--space-6);
    text-align: center;
  }
  
  .tech-icon {
    width: 56px;
    height: 56px;
    background: var(--primary-100);
    color: var(--primary-600);
    border-radius: var(--radius-xl);
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto var(--space-4);
  }
  
  .tech-card h3 {
    font-size: 1.125rem;
    margin-bottom: var(--space-2);
  }
  
  .tech-card p {
    font-size: 0.875rem;
    color: var(--gray-600);
    line-height: 1.6;
  }
  
  /* Data Section */
  .data-section {
    background: var(--gray-800);
    color: white;
  }
  
  .data-section h2,
  .data-section .section-subtitle {
    color: white;
  }
  
  .data-section .section-subtitle {
    opacity: 0.7;
  }
  
  .data-grid {
    display: grid;
    gap: var(--space-6);
  }
  
  @media (min-width: 768px) {
    .data-grid {
      grid-template-columns: repeat(2, 1fr);
    }
  }
  
  .data-card {
    padding: var(--space-6);
    border-radius: var(--radius-xl);
    background: var(--gray-700);
    border-top: 4px solid var(--primary-500);
  }
  
  .data-card.off-chain {
    border-top-color: var(--gray-500);
  }
  
  .data-icon {
    margin-bottom: var(--space-4);
    color: var(--primary-400);
  }
  
  .data-card.off-chain .data-icon {
    color: var(--gray-400);
  }
  
  .data-card h3 {
    color: white;
    margin-bottom: var(--space-2);
  }
  
  .data-badge {
    display: inline-block;
    padding: var(--space-1) var(--space-2);
    background: var(--primary-500);
    color: white;
    font-size: 0.65rem;
    font-weight: 600;
    border-radius: var(--radius-sm);
    letter-spacing: 0.05em;
    margin-bottom: var(--space-4);
  }
  
  .data-badge.gray {
    background: var(--gray-600);
  }
  
  .data-list {
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
  }
  
  .data-list li {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    color: var(--primary-300);
    font-size: 0.875rem;
  }
  
  .data-list.gray li {
    color: var(--gray-400);
  }
  
  /* Timeline */
  .timeline {
    max-width: 600px;
    margin: 0 auto;
  }
  
  .timeline-item {
    display: flex;
    gap: var(--space-4);
    padding-bottom: var(--space-6);
    position: relative;
  }
  
  .timeline-item:not(:last-child)::before {
    content: '';
    position: absolute;
    left: 18px;
    top: 40px;
    bottom: 0;
    width: 2px;
    background: var(--gray-200);
  }
  
  .timeline-number {
    width: 40px;
    height: 40px;
    background: var(--primary-600);
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    flex-shrink: 0;
  }
  
  .timeline-content h4 {
    margin-bottom: var(--space-2);
  }
  
  .timeline-content p {
    color: var(--gray-600);
    font-size: 0.875rem;
    line-height: 1.6;
  }
  
  /* Flow */
  .flow-grid {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--space-4);
  }
  
  @media (min-width: 768px) {
    .flow-grid {
      flex-direction: row;
      justify-content: center;
    }
  }
  
  .flow-card {
    background: var(--primary-50);
    padding: var(--space-6);
    border-radius: var(--radius-xl);
    text-align: center;
    max-width: 250px;
  }
  
  .flow-icon {
    width: 48px;
    height: 48px;
    background: white;
    color: var(--primary-600);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto var(--space-3);
    box-shadow: var(--shadow-sm);
  }
  
  .flow-card h4 {
    margin-bottom: var(--space-2);
    font-size: 1rem;
  }
  
  .flow-card p {
    font-size: 0.8rem;
    color: var(--gray-600);
    line-height: 1.5;
  }
  
  .flow-connector {
    color: var(--gray-400);
    font-size: 1.5rem;
    transform: rotate(90deg);
  }
  
  @media (min-width: 768px) {
    .flow-connector {
      transform: none;
    }
  }
  
  /* CTA */
  .cta-section {
    background: var(--gray-50);
  }
  
  .cta-content {
    text-align: center;
    max-width: 600px;
    margin: 0 auto;
  }
  
  .cta-content :global(svg) {
    color: var(--primary-600);
    margin-bottom: var(--space-4);
  }
  
  .cta-content h2 {
    margin-bottom: var(--space-4);
  }
  
  .cta-content p {
    color: var(--gray-600);
    margin-bottom: var(--space-6);
  }
  
  .cta-buttons {
    display: flex;
    gap: var(--space-3);
    justify-content: center;
    flex-wrap: wrap;
  }
</style>
