<script lang="ts">
  import { FileText, Lock, Users, Shield, ArrowRight, CheckCircle, Activity, Globe, Database, Zap } from 'lucide-svelte';
  import { onMount } from 'svelte';

  let mounted = false;
  onMount(() => {
    mounted = true;
  });
</script>

<svelte:head>
  <title>PromiseThread - The Future of Political Accountability</title>
</svelte:head>

<main class="landing-page">
  <!-- Hero Section -->
  <section class="hero">
    <div class="hero-bg">
      <div class="glow glow-1"></div>
      <div class="glow glow-2"></div>
      <div class="grid-pattern"></div>
    </div>
    
    <div class="container hero-container">
      <div class="hero-content">
        <div class="badge-pill">
          <span class="badge-dot"></span>
          <span>Live Election Cycle 2025</span>
        </div>
        <h1 class="hero-title">
          Democracy, <br />
          <span class="text-gradient">Upgraded.</span>
        </h1>
        <p class="hero-subtitle">
          The first decentralized platform that turns political promises into trackable, immutable records. Hold leaders accountable without compromising your privacy.
        </p>
        <div class="hero-buttons">
          <a href="/manifestos" class="btn btn-primary btn-xl">
            Explore Promises
            <ArrowRight size={20} />
          </a>
          <a href="/auth" class="btn btn-glass btn-xl">
            Verify Identity
          </a>
        </div>
        
        <div class="trust-badges">
          <div class="trust-item">
            <Shield size={16} />
            <span>Privacy Preserved</span>
          </div>
          <div class="trust-item">
            <Database size={16} />
            <span>Immutable Record</span>
          </div>
          <div class="trust-item">
            <Users size={16} />
            <span>Community Verified</span>
          </div>
        </div>
      </div>
      
      <!-- CSS Illustration: The Ledger -->
      <div class="hero-visual">
        <div class="ledger-illustration" class:animate={mounted}>
          <!-- Central Node -->
          <div class="ledger-card main-card">
            <div class="card-header">
              <div class="card-icon"><FileText size={20} /></div>
              <div class="card-lines">
                <div class="line long"></div>
                <div class="line short"></div>
              </div>
            </div>
            <div class="card-body">
              <div class="stat-row">
                <div class="stat-pill success">
                  <CheckCircle size={12} />
                  <span>Verified</span>
                </div>
                <div class="stat-pill">ID: #8821</div>
              </div>
              <div class="progress-container">
                <div class="progress-bar" style="width: 72%"></div>
              </div>
            </div>
          </div>
          
          <!-- Floating Nodes -->
          <div class="node node-1">
            <Users size={16} />
          </div>
          <div class="node node-2">
            <Lock size={16} />
          </div>
          <div class="node node-3">
            <Activity size={16} />
          </div>
          
          <!-- Connecting Lines (CSS Borders/Pseudo) -->
          <div class="connection conn-1"></div>
          <div class="connection conn-2"></div>
          <div class="connection conn-3"></div>
          
          <!-- Background Elements -->
          <div class="floating-card card-1">
            <div class="mini-stat">
              <span class="label">Trust Score</span>
              <span class="value">98%</span>
            </div>
          </div>
          <div class="floating-card card-2">
            <div class="mini-stat">
              <span class="label">Votes</span>
              <span class="value">12.5k</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Stats Strip -->
  <section class="stats-strip">
    <div class="container">
      <div class="stats-grid">
        <div class="stat-item">
          <span class="stat-number">2,400+</span>
          <span class="stat-label">Verified Citizens</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-item">
          <span class="stat-number">156</span>
          <span class="stat-label">Promises Tracked</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-item">
          <span class="stat-number">100%</span>
          <span class="stat-label">Transparent</span>
        </div>
      </div>
    </div>
  </section>

  <!-- Features Grid (Bento) -->
  <section class="section features-section">
    <div class="container">
      <div class="section-header">
        <h2>Powerful Accountability Tools</h2>
        <p>Built for the modern voter. Simple enough for anyone, powerful enough for truth.</p>
      </div>
      
      <div class="bento-grid">
        <!-- Large Feature -->
        <div class="bento-card large">
          <div class="card-content">
            <div class="icon-box primary">
              <Database size={28} />
            </div>
            <h3>Immutable Promise Ledger</h3>
            <p>Every promise is recorded permanently. Politicians cannot delete or silently edit their commitments once they are live. History is preserved forever.</p>
            <div class="feature-visual-lines">
              <div class="code-line">hash: 0x7f8...9a2</div>
              <div class="code-line">prev: 0x3c1...b4e</div>
              <div class="code-line">status: <span class="text-emerald-400">verified</span></div>
            </div>
          </div>
        </div>
        
        <!-- Medium Feature -->
        <div class="bento-card medium">
          <div class="card-content">
            <div class="icon-box success">
              <Shield size={28} />
            </div>
            <h3>Zero-Knowledge Privacy</h3>
            <p>Prove you are a citizen without revealing who you are. Your vote is counted, but your identity remains yours alone.</p>
          </div>
          <div class="shield-visual">
            <div class="shield-ring"></div>
            <Shield size={40} class="shield-icon" />
          </div>
        </div>
        
        <!-- Small Features -->
        <div class="bento-card small">
          <div class="icon-box warning">
            <Activity size={24} />
          </div>
          <h3>Real-time Tracking</h3>
          <p>Watch promise status updates live as they happen.</p>
        </div>
        
        <div class="bento-card small">
          <div class="icon-box info">
            <Globe size={24} />
          </div>
          <h3>Open Data</h3>
          <p>All data is accessible via API for independent audit.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- Process Section -->
  <section class="section process-section">
    <div class="container">
      <div class="process-wrapper">
        <div class="process-line"></div>
        
        <div class="process-step">
          <div class="step-number">01</div>
          <div class="step-content">
            <h3>Politicians Post</h3>
            <p>Candidates publish their manifestos. Each promise is locked into the system.</p>
          </div>
        </div>
        
        <div class="process-step">
          <div class="step-number">02</div>
          <div class="step-content">
            <h3>Citizens Verify</h3>
            <p>Voters join anonymously using secure identity verification.</p>
          </div>
        </div>
        
        <div class="process-step">
          <div class="step-number">03</div>
          <div class="step-content">
            <h3>Community Tracks</h3>
            <p>Vote on progress. Is the promise kept? The community decides.</p>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- CTA Section -->
  <section class="cta-section">
    <div class="container">
      <div class="cta-card">
        <div class="cta-content">
          <h2>Ready to shape the future?</h2>
          <p>Join thousands of citizens ensuring promises are more than just words.</p>
          <div class="cta-buttons">
            <a href="/auth" class="btn btn-white btn-lg">
              Get Started Now
            </a>
          </div>
        </div>
        <div class="cta-pattern">
          <Zap size={120} strokeWidth={1} />
        </div>
      </div>
    </div>
  </section>
</main>

<style>
  /* Global Layout */
  .landing-page {
    overflow-x: hidden;
    background-color: #0f172a; /* Dark slate background */
    color: white;
  }
  
  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 var(--space-6);
  }
  
  /* Hero Section */
  .hero {
    position: relative;
    min-height: 100vh;
    display: flex;
    align-items: center;
    padding-top: 8rem; /* Increased to account for fixed header */
    padding-bottom: 4rem;
    overflow: hidden;
  }
  
  .hero-bg {
    position: absolute;
    inset: 0;
    z-index: 0;
  }
  
  .grid-pattern {
    position: absolute;
    inset: 0;
    background-image: linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    mask-image: radial-gradient(circle at center, black 40%, transparent 80%);
  }
  
  .glow {
    position: absolute;
    border-radius: 50%;
    filter: blur(100px);
    opacity: 0.4;
  }
  
  .glow-1 {
    top: -10%;
    left: -10%;
    width: 500px;
    height: 500px;
    background: var(--primary-600);
  }
  
  .glow-2 {
    bottom: 10%;
    right: -5%;
    width: 600px;
    height: 600px;
    background: var(--primary-800);
  }
  
  .hero-container {
    position: relative;
    z-index: 1;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 4rem;
    align-items: center;
  }
  
  .hero-content {
    max-width: 600px;
  }
  
  .badge-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background: rgba(59, 130, 246, 0.1);
    border: 1px solid rgba(59, 130, 246, 0.2);
    border-radius: 9999px;
    color: var(--primary-300);
    font-size: 0.875rem;
    font-weight: 500;
    margin-bottom: 1.5rem;
  }
  
  .badge-dot {
    width: 8px;
    height: 8px;
    background: var(--success-500);
    border-radius: 50%;
    box-shadow: 0 0 8px var(--success-500);
  }
  
  .hero-title {
    font-size: 4rem;
    line-height: 1.1;
    font-weight: 800;
    margin-bottom: 1.5rem;
    letter-spacing: -0.02em;
    color: white;
  }
  
  .text-gradient {
    background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  
  .hero-subtitle {
    font-size: 1.25rem;
    color: var(--gray-300);
    margin-bottom: 2.5rem;
    line-height: 1.6;
  }
  
  .hero-buttons {
    display: flex;
    gap: 1rem;
    margin-bottom: 3rem;
  }
  
  .btn-xl {
    padding: 1rem 2rem;
    font-size: 1.125rem;
  }
  
  .btn-glass {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: white;
    backdrop-filter: blur(10px);
  }
  
  .btn-glass:hover {
    background: rgba(255, 255, 255, 0.1);
  }
  
  .trust-badges {
    display: flex;
    gap: 2rem;
    padding-top: 2rem;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
  }
  
  .trust-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: var(--gray-300);
    font-size: 0.875rem;
  }
  
  /* Hero Visual / Illustration */
  .hero-visual {
    position: relative;
    height: 500px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .ledger-illustration {
    position: relative;
    width: 100%;
    height: 100%;
  }
  
  .ledger-card {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 280px;
    background: rgba(30, 41, 59, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 1.5rem;
    backdrop-filter: blur(12px);
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
    z-index: 10;
  }
  
  .card-header {
    display: flex;
    gap: 1rem;
    margin-bottom: 1.5rem;
  }
  
  .card-icon {
    width: 40px;
    height: 40px;
    background: rgba(59, 130, 246, 0.2);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--primary-400);
  }
  
  .card-lines {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 0.5rem;
  }
  
  .line {
    height: 6px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 3px;
  }
  
  .line.long { width: 100%; }
  .line.short { width: 60%; }
  
  .stat-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 1rem;
  }
  
  .stat-pill {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    font-size: 0.75rem;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    background: rgba(255, 255, 255, 0.05);
    color: var(--gray-300);
  }
  
  .stat-pill.success {
    background: rgba(16, 185, 129, 0.1);
    color: var(--success-400);
  }
  
  .progress-container {
    height: 6px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 3px;
    overflow: hidden;
  }
  
  .progress-bar {
    height: 100%;
    background: var(--primary-500);
    border-radius: 3px;
  }
  
  .node {
    position: absolute;
    width: 48px;
    height: 48px;
    background: rgba(15, 23, 42, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--gray-300);
    z-index: 5;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
  }
  
  .node-1 { top: 20%; left: 20%; animation: float 6s ease-in-out infinite; }
  .node-2 { top: 30%; right: 15%; animation: float 7s ease-in-out infinite 1s; }
  .node-3 { bottom: 20%; left: 30%; animation: float 8s ease-in-out infinite 2s; }
  
  .floating-card {
    position: absolute;
    padding: 0.75rem 1.25rem;
    background: rgba(30, 41, 59, 0.9);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    z-index: 8;
    backdrop-filter: blur(8px);
  }
  
  .card-1 { top: 15%; right: 30%; animation: float 5s ease-in-out infinite 0.5s; }
  .card-2 { bottom: 25%; right: 20%; animation: float 6s ease-in-out infinite 1.5s; }
  
  .mini-stat {
    display: flex;
    flex-direction: column;
  }
  
  .mini-stat .label { font-size: 0.75rem; color: var(--gray-300); }
  .mini-stat .value { font-size: 1.125rem; font-weight: 700; color: white; }
  
  @keyframes float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-20px); }
  }
  
  /* Stats Strip */
  .stats-strip {
    background: rgba(255, 255, 255, 0.02);
    border-top: 1px solid rgba(255, 255, 255, 0.05);
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    padding: 2rem 0;
  }
  
  .stats-grid {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 4rem;
  }
  
  .stat-item {
    text-align: center;
  }
  
  .stat-number {
    display: block;
    font-size: 2.5rem;
    font-weight: 700;
    color: white;
    line-height: 1;
    margin-bottom: 0.5rem;
  }
  
  .stat-label {
    color: var(--gray-300);
    font-size: 0.875rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  
  .stat-divider {
    width: 1px;
    height: 40px;
    background: rgba(255, 255, 255, 0.1);
  }
  
  /* Features Section */
  .section {
    padding: 8rem 0;
  }
  
  .section-header {
    text-align: center;
    max-width: 700px;
    margin: 0 auto 5rem;
  }
  
  .section-header h2 {
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 1rem;
  }
  
  .section-header p {
    font-size: 1.125rem;
    color: var(--gray-300);
  }
  
  .bento-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    grid-template-rows: repeat(2, 320px);
    gap: 2rem;
  }
  
  .bento-card {
    background: rgba(30, 41, 59, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 24px;
    padding: 2rem;
    position: relative;
    overflow: hidden;
    transition: transform 0.3s ease, border-color 0.3s ease;
  }
  
  .bento-card:hover {
    transform: translateY(-5px);
    border-color: rgba(255, 255, 255, 0.1);
    background: rgba(30, 41, 59, 0.6);
  }
  
  .bento-card.large {
    grid-column: span 2;
    grid-row: span 1;
  }
  
  .bento-card.medium {
    grid-column: span 1;
    grid-row: span 2;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }
  
  .bento-card.small {
    grid-column: span 1;
    grid-row: span 1;
  }
  
  .icon-box {
    width: 56px;
    height: 56px;
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 1.5rem;
  }
  
  .icon-box.primary { background: rgba(59, 130, 246, 0.1); color: var(--primary-400); }
  .icon-box.success { background: rgba(16, 185, 129, 0.1); color: var(--success-400); }
  .icon-box.warning { background: rgba(245, 158, 11, 0.1); color: var(--warning-400); }
  .icon-box.info { background: rgba(6, 182, 212, 0.1); color: #22d3ee; }
  
  .bento-card h3 {
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 0.75rem;
    color: white;
  }
  
  .bento-card p {
    color: var(--gray-300);
    line-height: 1.6;
  }
  
  .feature-visual-lines {
    margin-top: 2rem;
    background: rgba(0, 0, 0, 0.5);
    border-radius: 12px;
    padding: 1rem;
    font-family: monospace;
    font-size: 0.875rem;
    color: var(--gray-200);
  }
  
  .code-line {
    margin-bottom: 0.5rem;
  }
  
  .shield-visual {
    position: relative;
    height: 150px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-top: 2rem;
  }
  
  .shield-ring {
    position: absolute;
    width: 120px;
    height: 120px;
    border: 2px dashed rgba(16, 185, 129, 0.2);
    border-radius: 50%;
    animation: spin 10s linear infinite;
  }
  
  .shield-icon {
    color: var(--success-500);
    filter: drop-shadow(0 0 10px rgba(16, 185, 129, 0.3));
  }
  
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
  
  /* Process Section */
  .process-section {
    background: rgba(255, 255, 255, 0.02);
  }
  
  .process-wrapper {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 2rem;
    position: relative;
    padding-top: 2rem;
  }
  
  .process-line {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--primary-500), transparent);
  }
  
  .process-step {
    position: relative;
  }
  
  .step-number {
    font-size: 4rem;
    font-weight: 800;
    color: rgba(255, 255, 255, 0.05);
    position: absolute;
    top: -2rem;
    left: 0;
    z-index: 0;
  }
  
  .step-content {
    position: relative;
    z-index: 1;
    padding-top: 1rem;
  }
  
  .step-content h3 {
    font-size: 1.25rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    color: var(--primary-300);
  }
  
  .step-content p {
    color: var(--gray-300);
    font-size: 0.95rem;
  }
  
  /* CTA Section */
  .cta-section {
    padding: 6rem 0;
  }
  
  .cta-card {
    background: linear-gradient(135deg, var(--primary-600), var(--primary-800));
    border-radius: 32px;
    padding: 4rem;
    position: relative;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  
  .cta-content {
    position: relative;
    z-index: 2;
    max-width: 500px;
  }
  
  .cta-content h2 {
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 1rem;
  }
  
  .cta-content p {
    font-size: 1.125rem;
    color: rgba(255, 255, 255, 0.9);
    margin-bottom: 2rem;
  }
  
  .btn-white {
    background: white;
    color: var(--primary-700);
    padding: 1rem 2rem;
    font-weight: 600;
    border-radius: 12px;
    transition: transform 0.2s;
  }
  
  .btn-white:hover {
    transform: scale(1.05);
  }
  
  .cta-pattern {
    position: absolute;
    right: -20px;
    bottom: -20px;
    color: rgba(255, 255, 255, 0.1);
    transform: rotate(-15deg);
  }
  
  /* Responsive */
  @media (max-width: 1024px) {
    .hero-container {
      grid-template-columns: 1fr;
      text-align: center;
    }
    
    .hero-content {
      margin: 0 auto;
    }
    
    .hero-buttons {
      justify-content: center;
    }
    
    .trust-badges {
      justify-content: center;
    }
    
    .bento-grid {
      grid-template-columns: 1fr;
      grid-template-rows: auto;
    }
    
    .bento-card.large, .bento-card.medium, .bento-card.small {
      grid-column: span 1;
      grid-row: span 1;
    }
    
    .process-wrapper {
      grid-template-columns: 1fr;
      gap: 4rem;
    }
    
    .process-line {
      display: none;
    }
  }
</style>