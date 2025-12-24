<script lang="ts">
  import Header from '$lib/components/Header.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import HashDisplay from '$lib/components/HashDisplay.svelte';
  import { Building2, Shield, CheckCircle, Lock, ChevronRight, Calendar } from 'lucide-svelte';
  
  // Promise data
  const promise = {
    id: '402',
    title: 'North-South Rail Link',
    category: 'Infrastructure',
    quote: 'We promise to complete the construction of the North-South Rail Link by Q4 2025 to reduce city congestion.',
    targetDate: 'Dec 31, 2025',
    imageUrl: '/images/rail-link.jpg'
  };
  
  // Ledger record
  const ledgerRecord = {
    nullifierHash: '0x8a72f92b45c1e98d3a7b...c4d1',
    blockHeight: 18249002,
    timestamp: '2023-10-27 14:38:22 UTC'
  };
  
  let attestation: 'fulfilled' | 'not_fulfilled' | null = null;
  let isSubmitting = false;
  
  async function submitAttestation() {
    if (!attestation) return;
    isSubmitting = true;
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500));
    isSubmitting = false;
    // Show success
  }
</script>

<svelte:head>
  <title>Citizen Attestation Portal - PromiseThread</title>
</svelte:head>

<Header variant="citizen" />

<main class="attestation-page">
  <div class="container">
    <!-- Page Header -->
    <div class="page-header">
      <span class="header-badge">
        <Building2 size={14} />
        OFFICIAL RECORD SYSTEM
      </span>
      <h1>Citizen Attestation Portal</h1>
      <p>Submit your verification of manifesto items anonymously. All records are cryptographically signed and publicly auditable.</p>
    </div>
    
    <!-- ZK Identity Banner -->
    <div class="zk-banner">
      <div class="zk-left">
        <Shield size={20} />
        <div>
          <strong>Identity: Verified (Zero-Knowledge)</strong>
          <span>Proof generated via zk-SNARK protocol. Your personal data is hidden.</span>
        </div>
      </div>
      <span class="session-badge">
        <span class="status-dot online"></span>
        Secure Session Active
      </span>
    </div>
    
    <div class="content-grid">
      <!-- Promise Card -->
      <div class="promise-section">
        <div class="promise-card card">
          <span class="category-badge">{promise.category.toUpperCase()}</span>
          <div class="promise-image">
            <div class="image-placeholder">
              <Building2 size={48} />
            </div>
          </div>
          <h2>Manifesto Item #{promise.id}: {promise.title}</h2>
          <blockquote>
            "{promise.quote}"
          </blockquote>
          <div class="target-date">
            <Calendar size={16} />
            <span>Target Completion: {promise.targetDate}</span>
          </div>
        </div>
        
        <!-- Attestation Form -->
        <div class="attestation-form card">
          <div class="form-header">
            <CheckCircle size={20} />
            <h3>Your Attestation</h3>
          </div>
          
          <div class="attestation-options">
            <label class="attestation-option" class:selected={attestation === 'fulfilled'}>
              <input type="radio" bind:group={attestation} value="fulfilled" />
              <div class="option-radio"></div>
              <div class="option-content">
                <strong>Being fulfilled</strong>
                <span>I confirm seeing clear evidence of active construction and progress according to the schedule.</span>
              </div>
            </label>
            
            <label class="attestation-option" class:selected={attestation === 'not_fulfilled'}>
              <input type="radio" bind:group={attestation} value="not_fulfilled" />
              <div class="option-radio"></div>
              <div class="option-content">
                <strong>Not being fulfilled</strong>
                <span>I see no evidence of progress, or the project appears abandoned/delayed.</span>
              </div>
            </label>
          </div>
          
          <button 
            class="submit-btn" 
            on:click={submitAttestation}
            disabled={!attestation || isSubmitting}
          >
            {#if isSubmitting}
              <span class="spinner"></span>
              Processing...
            {:else}
              <ChevronRight size={18} />
              Submit Attestation
            {/if}
          </button>
          
          <p class="disclaimer">
            <Lock size={14} />
            Action is irreversible. No personal data will be recorded.
          </p>
        </div>
      </div>
      
      <!-- Sidebar -->
      <aside class="sidebar">
        <!-- Ledger Record -->
        <div class="sidebar-card card">
          <div class="card-header">
            <span class="card-label">OFFICIAL LEDGER RECORD</span>
            <Lock size={14} />
          </div>
          
          <div class="result-badge">
            <CheckCircle size={18} />
            <span>Result: Recorded Anonymously</span>
          </div>
          
          <div class="record-field">
            <span class="field-label">NULLIFIER HASH</span>
            <div class="field-value mono">{ledgerRecord.nullifierHash}</div>
            <span class="field-hint">Unique identifier preventing double-voting</span>
          </div>
          
          <div class="record-field">
            <span class="field-label">BLOCK HEIGHT</span>
            <div class="field-value">#{ledgerRecord.blockHeight.toLocaleString()}</div>
          </div>
          
          <div class="record-field">
            <span class="field-label">TIMESTAMP</span>
            <div class="field-value">{ledgerRecord.timestamp}</div>
          </div>
          
          <p class="immutable-note">
            This record is immutable and permanently stored on the chain.
          </p>
        </div>
        
        <!-- Privacy Guarantee -->
        <div class="sidebar-card card">
          <h4>
            <Shield size={16} />
            Privacy Guarantee
          </h4>
          <ul class="privacy-list">
            <li>Your vote is cryptographically signed using your private key, but only the proof is submitted.</li>
            <li>The <strong>Nullifier Hash</strong> ensures one-person-one-vote without linking back to your ID.</li>
            <li>Results are publicly available for audit by any citizen node.</li>
          </ul>
        </div>
      </aside>
    </div>
  </div>
  
  <!-- Footer -->
  <div class="page-footer">
    <span>Powered by Citizen Protocol v2.1</span>
    <span>•</span>
    <a href="/privacy">Privacy Policy</a>
    <span>•</span>
    <a href="/source">Verify Source Code</a>
    <div class="footer-center">Official Government Transparency Initiative</div>
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
  
  /* Page Header */
  .page-header {
    margin-bottom: var(--space-6);
  }
  
  .header-badge {
    display: inline-flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-1) var(--space-3);
    background: var(--success-100);
    color: var(--success-700);
    font-size: 0.7rem;
    font-weight: 600;
    border-radius: var(--radius-full);
    margin-bottom: var(--space-3);
    letter-spacing: 0.02em;
  }
  
  .page-header h1 {
    font-size: 1.75rem;
    margin-bottom: var(--space-2);
  }
  
  .page-header p {
    color: var(--gray-500);
    max-width: 600px;
  }
  
  /* ZK Banner */
  .zk-banner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: var(--space-4);
    padding: var(--space-4);
    background: white;
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-xl);
    margin-bottom: var(--space-6);
  }
  
  .zk-left {
    display: flex;
    align-items: center;
    gap: var(--space-3);
  }
  
  .zk-left :global(svg) {
    color: var(--primary-600);
  }
  
  .zk-left strong {
    display: block;
    color: var(--gray-900);
    font-size: 0.9rem;
  }
  
  .zk-left span {
    font-size: 0.8rem;
    color: var(--gray-500);
  }
  
  .session-badge {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-2) var(--space-3);
    background: var(--success-50);
    color: var(--success-700);
    border-radius: var(--radius-full);
    font-size: 0.75rem;
    font-weight: 500;
  }
  
  .status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
  }
  
  .status-dot.online {
    background: var(--success-500);
  }
  
  /* Content Grid */
  .content-grid {
    display: grid;
    gap: var(--space-6);
  }
  
  @media (min-width: 768px) {
    .content-grid {
      grid-template-columns: 1fr 340px;
    }
  }
  
  /* Promise Section */
  .promise-card {
    padding: var(--space-6);
    margin-bottom: var(--space-4);
    position: relative;
  }
  
  .category-badge {
    position: absolute;
    top: var(--space-4);
    left: var(--space-4);
    padding: var(--space-1) var(--space-3);
    background: var(--gray-800);
    color: white;
    font-size: 0.65rem;
    font-weight: 600;
    border-radius: var(--radius-sm);
    letter-spacing: 0.02em;
  }
  
  .promise-image {
    margin-bottom: var(--space-4);
    border-radius: var(--radius-lg);
    overflow: hidden;
  }
  
  .image-placeholder {
    height: 200px;
    background: linear-gradient(135deg, var(--success-100), var(--primary-100));
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--gray-400);
  }
  
  .promise-card h2 {
    font-size: 1.25rem;
    margin-bottom: var(--space-3);
  }
  
  .promise-card blockquote {
    padding: var(--space-4);
    background: var(--gray-50);
    border-left: 3px solid var(--primary-500);
    margin-bottom: var(--space-4);
    font-style: italic;
    color: var(--gray-700);
    line-height: 1.6;
  }
  
  .target-date {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    font-size: 0.875rem;
    color: var(--gray-500);
  }
  
  /* Attestation Form */
  .attestation-form {
    padding: var(--space-5);
  }
  
  .form-header {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    margin-bottom: var(--space-4);
    color: var(--success-600);
  }
  
  .form-header h3 {
    color: var(--gray-900);
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
    border-color: var(--gray-300);
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
    position: relative;
  }
  
  .attestation-option.selected .option-radio {
    border-color: var(--primary-500);
  }
  
  .attestation-option.selected .option-radio::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 10px;
    height: 10px;
    background: var(--primary-500);
    border-radius: 50%;
  }
  
  .option-content {
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
  }
  
  .option-content strong {
    color: var(--gray-900);
  }
  
  .option-content span {
    font-size: 0.8rem;
    color: var(--gray-500);
    line-height: 1.4;
  }
  
  .submit-btn {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--space-2);
    padding: var(--space-4);
    background: var(--warning-500);
    color: white;
    border: none;
    border-radius: var(--radius-lg);
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    margin-bottom: var(--space-3);
  }
  
  .submit-btn:hover:not(:disabled) {
    background: var(--warning-600);
  }
  
  .submit-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  .spinner {
    width: 18px;
    height: 18px;
    border: 2px solid white;
    border-top-color: transparent;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }
  
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
  
  .disclaimer {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--space-2);
    font-size: 0.75rem;
    color: var(--gray-400);
    text-align: center;
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
    color: var(--gray-400);
  }
  
  .card-label {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.05em;
  }
  
  .result-badge {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-3);
    background: var(--success-50);
    border-radius: var(--radius-lg);
    margin-bottom: var(--space-4);
  }
  
  .result-badge :global(svg) {
    color: var(--success-600);
  }
  
  .result-badge span {
    color: var(--success-700);
    font-weight: 500;
    font-size: 0.875rem;
  }
  
  .record-field {
    margin-bottom: var(--space-4);
  }
  
  .field-label {
    display: block;
    font-size: 0.65rem;
    font-weight: 600;
    color: var(--gray-400);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: var(--space-1);
  }
  
  .field-value {
    font-size: 0.875rem;
    color: var(--gray-900);
    word-break: break-all;
  }
  
  .field-value.mono {
    font-family: var(--font-mono);
    font-size: 0.75rem;
  }
  
  .field-hint {
    display: block;
    font-size: 0.65rem;
    color: var(--gray-400);
    font-style: italic;
    margin-top: var(--space-1);
  }
  
  .immutable-note {
    padding-top: var(--space-4);
    border-top: 1px solid var(--gray-200);
    font-size: 0.75rem;
    color: var(--gray-500);
    font-style: italic;
  }
  
  .sidebar-card h4 {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    font-size: 0.9rem;
    margin-bottom: var(--space-3);
    color: var(--primary-600);
  }
  
  .privacy-list {
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
  }
  
  .privacy-list li {
    font-size: 0.8rem;
    color: var(--gray-600);
    line-height: 1.5;
    padding-left: var(--space-4);
    position: relative;
  }
  
  .privacy-list li::before {
    content: '•';
    position: absolute;
    left: 0;
    color: var(--primary-500);
  }
  
  .privacy-list li strong {
    color: var(--primary-600);
  }
  
  /* Page Footer */
  .page-footer {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-wrap: wrap;
    gap: var(--space-3);
    padding: var(--space-6) var(--space-4);
    font-size: 0.75rem;
    color: var(--gray-400);
    text-align: center;
  }
  
  .page-footer a {
    color: var(--primary-600);
    text-decoration: none;
  }
  
  .footer-center {
    width: 100%;
    margin-top: var(--space-2);
    font-style: italic;
  }
</style>
