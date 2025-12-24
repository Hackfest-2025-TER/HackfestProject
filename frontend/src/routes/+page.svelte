<script lang="ts">
  import Header from '$lib/components/Header.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import { FileText, Lock, Users, Shield, Eye, EyeOff, CheckCircle, ChevronRight, BookOpen } from 'lucide-svelte';
</script>

<svelte:head>
  <title>PromiseThread - Track Election Promises</title>
</svelte:head>

<Header variant="default" />

<main>
  <!-- Hero Section -->
  <section class="hero">
    <div class="container">
      <div class="hero-content">
        <h1>Know What Was Promised.<br/>See What Was Delivered.</h1>
        <p class="hero-subtitle">
          This platform keeps election promises public and unchanged, so citizens can 
          track progress without giving up their privacy.
        </p>
        <div class="hero-buttons">
          <a href="/manifestos" class="btn btn-primary btn-lg">
            <FileText size={20} />
            View Election Promises
          </a>
          <a href="/guide" class="btn btn-secondary btn-lg">
            How This Works
          </a>
        </div>
      </div>
      <div class="hero-image">
        <div class="hero-illustration">
          <div class="promise-card">
            <div class="promise-status kept">✓ Kept</div>
            <div class="promise-title">Build 100 new schools</div>
            <div class="promise-progress">
              <div class="progress-bar" style="width: 85%"></div>
            </div>
          </div>
          <div class="promise-card">
            <div class="promise-status pending">⏳ In Progress</div>
            <div class="promise-title">Reduce unemployment by 20%</div>
            <div class="promise-progress">
              <div class="progress-bar" style="width: 45%"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- What Can You Do Section -->
  <section class="section features-section">
    <div class="container">
      <h2>What Can You Do on This Platform?</h2>
      <p class="section-subtitle">Simple tools to help you stay informed about political promises.</p>
      
      <div class="features-grid">
        <div class="feature-card card">
          <div class="feature-icon">
            <FileText size={28} />
          </div>
          <h3>View Promises</h3>
          <p>See official promises made by political parties during elections. All in one place.</p>
        </div>
        
        <div class="feature-card card">
          <div class="feature-icon locked">
            <Lock size={28} />
          </div>
          <h3>Promises Cannot Be Changed</h3>
          <p>Once published, promises are locked and cannot be edited or deleted later.</p>
        </div>
        
        <div class="feature-card card">
          <div class="feature-icon feedback">
            <Users size={28} />
          </div>
          <h3>Share Your Feedback</h3>
          <p>Citizens can say whether promises are being fulfilled based on what they see.</p>
        </div>
        
        <div class="feature-card card">
          <div class="feature-icon privacy">
            <Shield size={28} />
          </div>
          <h3>Stay Anonymous</h3>
          <p>You can participate without revealing your name or identity. Your privacy comes first.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- What Is Public / Private Section -->
  <section class="section transparency-section">
    <div class="container">
      <h2>What Is Public and What Is Private?</h2>
      <p class="section-subtitle">We believe in transparency for promises, but privacy for people.</p>
      
      <div class="transparency-grid">
        <div class="transparency-card public">
          <div class="transparency-header">
            <Eye size={24} />
            <h3>Public</h3>
            <span class="badge">Anyone Can See</span>
          </div>
          <ul class="transparency-list">
            <li><CheckCircle size={18} /> Election promises from all parties</li>
            <li><CheckCircle size={18} /> Progress updates and results</li>
            <li><CheckCircle size={18} /> Overall citizen feedback scores</li>
            <li><CheckCircle size={18} /> When promises were made</li>
          </ul>
        </div>
        
        <div class="transparency-card private">
          <div class="transparency-header">
            <EyeOff size={24} />
            <h3>Private</h3>
            <span class="badge gray">Never Revealed</span>
          </div>
          <ul class="transparency-list">
            <li><Shield size={18} /> Your name</li>
            <li><Shield size={18} /> Your voter ID</li>
            <li><Shield size={18} /> How you voted</li>
            <li><Shield size={18} /> Your personal information</li>
          </ul>
        </div>
      </div>
    </div>
  </section>

  <!-- Promise Lifecycle -->
  <section class="section lifecycle-section">
    <div class="container">
      <h2>How an Election Promise Is Tracked</h2>
      <p class="section-subtitle">A simple process to keep politicians accountable.</p>
      
      <div class="timeline">
        <div class="timeline-item">
          <div class="timeline-number">1</div>
          <div class="timeline-content">
            <h4>Promises Are Published</h4>
            <p>Political parties publish their official promises during election time.</p>
          </div>
        </div>
        
        <div class="timeline-item">
          <div class="timeline-number">2</div>
          <div class="timeline-content">
            <h4>Promises Are Locked</h4>
            <p>Once published, promises cannot be changed or deleted. They remain as a permanent record.</p>
          </div>
        </div>
        
        <div class="timeline-item">
          <div class="timeline-number">3</div>
          <div class="timeline-content">
            <h4>Citizens Track Progress</h4>
            <p>Over time, citizens can share their feedback on whether promises are being kept.</p>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Privacy Assurance -->
  <section class="section privacy-section">
    <div class="container">
      <div class="privacy-content">
        <div class="privacy-icon">
          <Shield size={48} />
        </div>
        <h2>Your Privacy Comes First</h2>
        <p>
          You can take part without logging in with your name. The system only checks 
          that you are a real citizen — nothing more. We never see who you are.
        </p>
        <a href="/privacy" class="btn btn-outline">
          Learn How Your Privacy Is Protected
          <ChevronRight size={18} />
        </a>
      </div>
    </div>
  </section>

  <!-- Final CTA -->
  <section class="section cta-section">
    <div class="container">
      <div class="cta-content">
        <h2>Democracy Works Better When Promises Are Remembered</h2>
        <p>
          Join thousands of citizens who are keeping track of what was promised 
          and what was delivered.
        </p>
        <div class="cta-buttons">
          <a href="/manifestos" class="btn btn-primary btn-lg">
            <FileText size={20} />
            Explore Promises
          </a>
          <a href="/guide" class="btn btn-secondary btn-lg">
            <BookOpen size={20} />
            Citizen Guide
          </a>
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
    font-size: 2rem;
    color: var(--gray-900);
  }
  
  .section-subtitle {
    text-align: center;
    color: var(--gray-500);
    max-width: 600px;
    margin: 0 auto var(--space-10);
    font-size: 1.1rem;
  }
  
  /* Hero */
  .hero {
    padding: var(--space-16) 0;
    background: linear-gradient(180deg, #f8fafc 0%, white 100%);
  }
  
  .hero .container {
    display: grid;
    gap: var(--space-12);
    align-items: center;
  }
  
  @media (min-width: 768px) {
    .hero .container {
      grid-template-columns: 1fr 1fr;
    }
  }
  
  .hero h1 {
    font-size: 2.5rem;
    line-height: 1.15;
    margin-bottom: var(--space-6);
    color: #082770;
  }
  
  @media (min-width: 768px) {
    .hero h1 {
      font-size: 3rem;
    }
  }
  
  .hero-subtitle {
    color: var(--gray-600);
    margin-bottom: var(--space-8);
    font-size: 1.25rem;
    line-height: 1.7;
  }
  
  .hero-buttons {
    display: flex;
    gap: var(--space-4);
    flex-wrap: wrap;
  }
  
  .hero-buttons .btn {
    display: flex;
    align-items: center;
    gap: var(--space-2);
  }
  
  .btn-primary {
    background: #082770;
    color: white;
    padding: var(--space-4) var(--space-6);
    border-radius: var(--radius-lg);
    font-weight: 600;
    text-decoration: none;
    transition: all 0.2s;
  }
  
  .btn-primary:hover {
    background: #0a3490;
    transform: translateY(-1px);
  }
  
  .btn-secondary {
    background: white;
    color: #082770;
    padding: var(--space-4) var(--space-6);
    border-radius: var(--radius-lg);
    font-weight: 600;
    text-decoration: none;
    border: 2px solid #082770;
    transition: all 0.2s;
  }
  
  .btn-secondary:hover {
    background: #082770;
    color: white;
  }
  
  .btn-outline {
    display: inline-flex;
    align-items: center;
    gap: var(--space-2);
    color: #082770;
    font-weight: 600;
    text-decoration: none;
    padding: var(--space-3) var(--space-4);
    border: 2px solid #082770;
    border-radius: var(--radius-lg);
    transition: all 0.2s;
  }
  
  .btn-outline:hover {
    background: #082770;
    color: white;
  }
  
  /* Hero Illustration */
  .hero-image {
    display: flex;
    justify-content: center;
  }
  
  .hero-illustration {
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
    padding: var(--space-6);
    background: white;
    border-radius: var(--radius-2xl);
    box-shadow: var(--shadow-xl);
    border: 1px solid var(--gray-100);
  }
  
  .promise-card {
    padding: var(--space-4);
    background: var(--gray-50);
    border-radius: var(--radius-lg);
    min-width: 280px;
  }
  
  .promise-status {
    font-size: 0.75rem;
    font-weight: 600;
    margin-bottom: var(--space-2);
  }
  
  .promise-status.kept {
    color: var(--success-600);
  }
  
  .promise-status.pending {
    color: var(--warning-600);
  }
  
  .promise-title {
    font-weight: 600;
    color: var(--gray-900);
    margin-bottom: var(--space-3);
  }
  
  .promise-progress {
    height: 6px;
    background: var(--gray-200);
    border-radius: 3px;
    overflow: hidden;
  }
  
  .progress-bar {
    height: 100%;
    background: linear-gradient(90deg, #082770, #10b981);
    border-radius: 3px;
  }
  
  /* Features Section */
  .features-section {
    background: white;
  }
  
  .features-grid {
    display: grid;
    gap: var(--space-6);
  }
  
  @media (min-width: 768px) {
    .features-grid {
      grid-template-columns: repeat(2, 1fr);
    }
  }
  
  @media (min-width: 1024px) {
    .features-grid {
      grid-template-columns: repeat(4, 1fr);
    }
  }
  
  .feature-card {
    padding: var(--space-6);
    text-align: center;
    border: 1px solid var(--gray-100);
    transition: all 0.2s;
  }
  
  .feature-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-lg);
  }
  
  .feature-icon {
    width: 64px;
    height: 64px;
    background: #e8f4fc;
    color: #082770;
    border-radius: var(--radius-xl);
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto var(--space-4);
  }
  
  .feature-icon.locked {
    background: #fef3c7;
    color: #d97706;
  }
  
  .feature-icon.feedback {
    background: #dbeafe;
    color: #2563eb;
  }
  
  .feature-icon.privacy {
    background: #d1fae5;
    color: #059669;
  }
  
  .feature-card h3 {
    font-size: 1.125rem;
    margin-bottom: var(--space-2);
    color: var(--gray-900);
  }
  
  .feature-card p {
    font-size: 0.9rem;
    color: var(--gray-600);
    line-height: 1.6;
  }
  
  /* Transparency Section */
  .transparency-section {
    background: var(--gray-50);
  }
  
  .transparency-grid {
    display: grid;
    gap: var(--space-6);
  }
  
  @media (min-width: 768px) {
    .transparency-grid {
      grid-template-columns: repeat(2, 1fr);
    }
  }
  
  .transparency-card {
    padding: var(--space-8);
    border-radius: var(--radius-xl);
    background: white;
    box-shadow: var(--shadow-md);
  }
  
  .transparency-card.public {
    border-top: 4px solid #082770;
  }
  
  .transparency-card.private {
    border-top: 4px solid #059669;
  }
  
  .transparency-header {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: var(--space-3);
    margin-bottom: var(--space-6);
  }
  
  .transparency-header h3 {
    font-size: 1.25rem;
    margin: 0;
  }
  
  .transparency-card.public .transparency-header {
    color: #082770;
  }
  
  .transparency-card.private .transparency-header {
    color: #059669;
  }
  
  .badge {
    font-size: 0.7rem;
    font-weight: 600;
    padding: var(--space-1) var(--space-2);
    border-radius: var(--radius-sm);
    background: #082770;
    color: white;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  
  .badge.gray {
    background: #059669;
  }
  
  .transparency-list {
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
  }
  
  .transparency-list li {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    color: var(--gray-700);
    font-size: 0.95rem;
  }
  
  .transparency-card.public .transparency-list li :global(svg) {
    color: #082770;
  }
  
  .transparency-card.private .transparency-list li :global(svg) {
    color: #059669;
  }
  
  /* Timeline */
  .lifecycle-section {
    background: white;
  }
  
  .timeline {
    max-width: 600px;
    margin: 0 auto;
  }
  
  .timeline-item {
    display: flex;
    gap: var(--space-5);
    padding-bottom: var(--space-8);
    position: relative;
  }
  
  .timeline-item:not(:last-child)::before {
    content: '';
    position: absolute;
    left: 22px;
    top: 50px;
    bottom: 0;
    width: 3px;
    background: linear-gradient(180deg, #082770, #e5e7eb);
  }
  
  .timeline-number {
    width: 48px;
    height: 48px;
    background: #082770;
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 1.25rem;
    flex-shrink: 0;
  }
  
  .timeline-content h4 {
    margin-bottom: var(--space-2);
    font-size: 1.125rem;
    color: var(--gray-900);
  }
  
  .timeline-content p {
    color: var(--gray-600);
    font-size: 0.95rem;
    line-height: 1.6;
  }
  
  /* Privacy Section */
  .privacy-section {
    background: linear-gradient(135deg, #d1fae5 0%, #e8f4fc 100%);
  }
  
  .privacy-content {
    text-align: center;
    max-width: 600px;
    margin: 0 auto;
  }
  
  .privacy-icon {
    width: 80px;
    height: 80px;
    background: white;
    color: #059669;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto var(--space-6);
    box-shadow: var(--shadow-lg);
  }
  
  .privacy-content h2 {
    color: #082770;
    margin-bottom: var(--space-4);
  }
  
  .privacy-content p {
    color: var(--gray-700);
    margin-bottom: var(--space-6);
    font-size: 1.1rem;
    line-height: 1.7;
  }
  
  /* CTA */
  .cta-section {
    background: #082770;
    color: white;
  }
  
  .cta-content {
    text-align: center;
    max-width: 700px;
    margin: 0 auto;
  }
  
  .cta-content h2 {
    color: white;
    margin-bottom: var(--space-4);
    font-size: 2rem;
  }
  
  .cta-content p {
    color: rgba(255, 255, 255, 0.8);
    margin-bottom: var(--space-8);
    font-size: 1.1rem;
    line-height: 1.7;
  }
  
  .cta-buttons {
    display: flex;
    gap: var(--space-4);
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .cta-buttons .btn-primary {
    background: white;
    color: #082770;
  }
  
  .cta-buttons .btn-primary:hover {
    background: #f1f5f9;
  }
  
  .cta-buttons .btn-secondary {
    background: transparent;
    color: white;
    border-color: white;
  }
  
  .cta-buttons .btn-secondary:hover {
    background: white;
    color: #082770;
  }
  
  .cta-buttons .btn {
    display: flex;
    align-items: center;
    gap: var(--space-2);
  }
</style>
