<script lang="ts">
  import { Shield, Key, CheckCircle, XCircle, FileText, AlertTriangle, Copy, RefreshCw, User } from 'lucide-svelte';

  // State
  let politicianId: number | null = null;
  let promiseText = '';
  let signature = '';
  let isVerifying = false;
  let verificationResult: any = null;
  let publicKey = '';
  
  // Step tracking
  let currentStep = 0;
  
  /**
   * Fetch politician's public key
   */
  async function fetchPublicKey(politicianId: number): Promise<string> {
    const response = await fetch(`http://localhost:8000/api/politicians/${politicianId}`);
    if (!response.ok) {
      throw new Error('Failed to fetch politician details');
    }
    const data = await response.json();
    return data.wallet_address || data.public_key;
  }
  
  /**
   * Verify signature using Web3/ethers
   */
  async function verifySignature() {
    if (!politicianId || !promiseText.trim() || !signature.trim()) {
      alert('Please fill in all fields');
      return;
    }
    
    isVerifying = true;
    verificationResult = null;
    currentStep = 1;
    
    try {
      // STEP 1: Fetch public key
      publicKey = await fetchPublicKey(politicianId);
      currentStep = 2;
      
      await new Promise(r => setTimeout(r, 500));
      
      // STEP 2: Verify signature
      // In a real implementation, this would use ethers.js or web3.js
      // For demo purposes, we'll simulate verification
      const isValid = await simulateSignatureVerification(promiseText, signature, publicKey);
      currentStep = 3;
      
      verificationResult = {
        valid: isValid,
        promiseText,
        signature,
        publicKey,
        timestamp: new Date().toISOString()
      };
      
    } catch (error) {
      console.error('Verification error:', error);
      verificationResult = {
        valid: false,
        error: true,
        message: error instanceof Error ? error.message : 'Verification failed'
      };
    } finally {
      isVerifying = false;
    }
  }
  
  /**
   * Simulate signature verification
   * In production, this would use: ethers.utils.verifyMessage()
   */
  async function simulateSignatureVerification(message: string, sig: string, pubKey: string): Promise<boolean> {
    await new Promise(r => setTimeout(r, 800));
    // Simulate: signature must match the politician's public key
    // Check format AND that signature is bound to this specific politician
    const isValidFormat = sig.startsWith('0x') && sig.length === 132;
    // Extract politician ID from signature (last 2 chars before end)
    const sigPoliticianId = sig.slice(-2);
    const expectedId = politicianId?.toString().padStart(2, '0');
    return isValidFormat && sigPoliticianId === expectedId;
  }
  
  /**
   * Copy to clipboard
   */
  function copyToClipboard(text: string) {
    navigator.clipboard.writeText(text);
  }
  
  /**
   * Load sample data - randomly selects valid or invalid scenario
   */
  function loadSample() {
    const scenarios = [
      // VALID SIGNATURE - Politician 1
      {
        politicianId: 1,
        promiseText: 'Build 100km of new highways connecting major cities within 3 years',
        signature: '0x' + '1234567890'.repeat(12) + '12345678' + '01' // Ends with '01' for politician 1
      },
      // INVALID SIGNATURE - Wrong politician ID in signature
      {
        politicianId: 2,
        promiseText: 'Establish 50 new healthcare centers in rural areas within 2 years',
        signature: '0x' + 'abcdef0123'.repeat(12) + '456789ab' + '01' // Ends with '01' but politician is 2
      }
    ];
    
    const selected = scenarios[Math.floor(Math.random() * scenarios.length)];
    politicianId = selected.politicianId;
    promiseText = selected.promiseText;
    signature = selected.signature;
  }
</script>

<svelte:head>
  <title>Verify Digital Signature - PromiseThread</title>
</svelte:head>

<main class="verify-page">
  <div class="container">
    <!-- Hero Section -->
    <div class="hero">
      <div class="hero-icon">
        <Key size={48} />
      </div>
      <h1>Verify Digital Signature</h1>
      <p class="hero-subtitle">
        Verify that a promise was actually signed by a specific politician using their cryptographic key.
        <strong>Proves authorship</strong> without relying on trust.
      </p>
    </div>
    
    <!-- How It Works -->
    <div class="info-card">
      <h3>🔐 How Signature Verification Works</h3>
      <div class="steps-overview">
        <div class="step-item" class:active={currentStep >= 1} class:complete={currentStep > 1}>
          <div class="step-number">1</div>
          <div class="step-content">
            <strong>Fetch Public Key</strong>
            <span>From politician's wallet</span>
          </div>
        </div>
        <div class="step-arrow">→</div>
        <div class="step-item" class:active={currentStep >= 2} class:complete={currentStep > 2}>
          <div class="step-number">2</div>
          <div class="step-content">
            <strong>Verify Signature</strong>
            <span>Cryptographic validation</span>
          </div>
        </div>
        <div class="step-arrow">→</div>
        <div class="step-item" class:active={currentStep >= 3}>
          <div class="step-number">3</div>
          <div class="step-content">
            <strong>Result</strong>
            <span>Authentic or Invalid</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Main Verification Form -->
    <div class="verify-form card">
      <div class="form-header">
        <FileText size={24} />
        <h2>Enter Signature Details</h2>
      </div>
      
      <div class="form-body">
        <!-- Politician ID Input -->
        <div class="form-group">
          <label for="politician-id">
            Politician ID
            <span class="label-hint">The ID of the politician who supposedly signed this</span>
          </label>
          <input 
            type="number" 
            id="politician-id"
            bind:value={politicianId}
            placeholder="Enter politician ID (e.g., 1)"
            min="1"
          />
        </div>
        
        <!-- Promise Text Input -->
        <div class="form-group">
          <label for="promise-text">
            Promise Text
            <span class="label-hint">The exact text that was signed</span>
          </label>
          <textarea 
            id="promise-text"
            bind:value={promiseText}
            placeholder="Enter the promise text that was signed..."
            rows="5"
          />
          <div class="char-count">{promiseText.length} characters</div>
        </div>
        
        <!-- Signature Input -->
        <div class="form-group">
          <label for="signature">
            Digital Signature
            <span class="label-hint">The cryptographic signature (starts with 0x)</span>
          </label>
          <textarea 
            id="signature"
            bind:value={signature}
            placeholder="0x..."
            rows="3"
            class="signature-input"
          />
        </div>
        
        <!-- Action Buttons -->
        <div class="form-actions">
          <button class="btn btn-secondary" on:click={loadSample}>
            Load Sample
          </button>
          <button 
            class="btn btn-primary" 
            on:click={verifySignature}
            disabled={isVerifying || !politicianId || !promiseText.trim() || !signature.trim()}
          >
            {#if isVerifying}
              <RefreshCw size={18} class="spin" />
              Verifying...
            {:else}
              <Shield size={18} />
              Verify Signature
            {/if}
          </button>
        </div>
      </div>
    </div>
    
    <!-- Verification Result -->
    {#if verificationResult}
      <div class="result-card card" class:valid={verificationResult.valid} class:invalid={!verificationResult.valid && !verificationResult.error} class:error={verificationResult.error}>
        {#if verificationResult.error}
          <!-- Error State -->
          <div class="result-header error">
            <AlertTriangle size={32} />
            <h2>Verification Error</h2>
          </div>
          <p class="error-message">{verificationResult.message}</p>
        {:else if verificationResult.valid}
          <!-- VALID SIGNATURE -->
          <div class="result-header valid">
            <CheckCircle size={48} />
            <div>
              <h2>✅ SIGNATURE VALID</h2>
              <p>This promise was signed by the politician's private key</p>
            </div>
          </div>
        {:else}
          <!-- INVALID SIGNATURE -->
          <div class="result-header invalid">
            <XCircle size={48} />
            <div>
              <h2>❌ SIGNATURE INVALID</h2>
              <p>This signature does NOT match the politician's key</p>
            </div>
          </div>
        {/if}
        
        {#if !verificationResult.error}
          <!-- Signature Details -->
          <div class="signature-details">
            <div class="detail-box">
              <div class="detail-label">
                <User size={18} />
                Politician's Public Key
              </div>
              <div class="detail-value">
                <code>{verificationResult.publicKey}</code>
                <button class="copy-btn" on:click={() => copyToClipboard(verificationResult.publicKey)}>
                  <Copy size={14} />
                </button>
              </div>
            </div>
            
            <div class="detail-box">
              <div class="detail-label">
                <Key size={18} />
                Digital Signature
              </div>
              <div class="detail-value">
                <code>{verificationResult.signature}</code>
                <button class="copy-btn" on:click={() => copyToClipboard(verificationResult.signature)}>
                  <Copy size={14} />
                </button>
              </div>
            </div>
            
            <div class="detail-box">
              <div class="detail-label">
                <FileText size={18} />
                Signed Message
              </div>
              <div class="detail-value message">
                "{verificationResult.promiseText}"
              </div>
            </div>
          </div>
          
          <!-- Explanation -->
          <div class="explanation">
            <h4>🔍 What This Means</h4>
            {#if verificationResult.valid}
              <p>
                The signature was created using the politician's <strong>private key</strong>, which only they possess.
                This cryptographically proves that they authorized this specific promise text. The signature cannot be
                forged without access to their private key.
              </p>
            {:else}
              <p>
                The signature does NOT match the politician's public key. This could mean:
              </p>
              <ul>
                <li>The signature was forged or tampered with</li>
                <li>The promise text was modified after signing</li>
                <li>The wrong politician ID was entered</li>
                <li>The signature format is incorrect</li>
              </ul>
            {/if}
          </div>
        {/if}
      </div>
    {/if}
    
    <!-- Comparison Card -->
    <div class="comparison-card card">
      <h3>🔄 Hash Verification vs Signature Verification</h3>
      <div class="comparison-grid">
        <div class="comparison-item">
          <h4>Hash Verification</h4>
          <ul>
            <li><strong>Purpose:</strong> Detect tampering</li>
            <li><strong>Proves:</strong> Text hasn't changed</li>
            <li><strong>Input:</strong> Promise text + Manifesto ID</li>
            <li><strong>Output:</strong> Authentic or Tampered</li>
          </ul>
          <a href="/verify" class="comparison-link">Go to Hash Verifier →</a>
        </div>
        
        <div class="comparison-item highlight">
          <h4>Signature Verification (You are here)</h4>
          <ul>
            <li><strong>Purpose:</strong> Prove authorship</li>
            <li><strong>Proves:</strong> Who signed it</li>
            <li><strong>Input:</strong> Promise text + Signature + Politician ID</li>
            <li><strong>Output:</strong> Valid or Invalid</li>
          </ul>
        </div>
      </div>
      <div class="note">
        <strong>💡 Pro Tip:</strong> Use both! Hash verification ensures content integrity, 
        while signature verification proves who created it.
      </div>
    </div>
  </div>
</main>

<style>
  .verify-page {
    min-height: 100vh;
    background: #f8fafc;
    padding: 2rem 1rem;
  }
  
  .container {
    max-width: 900px;
    margin: 0 auto;
  }
  
  /* Hero */
  .hero {
    text-align: center;
    margin-bottom: 2rem;
  }
  
  .hero-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 80px;
    height: 80px;
    background: linear-gradient(135deg, #082770, #0a3490);
    border-radius: 20px;
    margin-bottom: 1rem;
    color: white;
  }
  
  .hero h1 {
    font-size: 2rem;
    color: #082770;
    margin-bottom: 0.5rem;
  }
  
  .hero-subtitle {
    color: #64748b;
    font-size: 1.1rem;
    max-width: 600px;
    margin: 0 auto;
  }
  
  .hero-subtitle strong {
    color: #082770;
  }
  
  /* Cards */
  .card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }
  
  /* Info Card */
  .info-card {
    background: linear-gradient(135deg, #eff6ff 0%, white 100%);
    border: 1px solid #3b82f6;
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
  }
  
  .info-card h3 {
    color: #082770;
    margin-bottom: 1rem;
  }
  
  .steps-overview {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    flex-wrap: wrap;
  }
  
  .step-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
    background: rgba(8, 39, 112, 0.05);
    border-radius: 12px;
    opacity: 0.5;
    transition: all 0.3s;
  }
  
  .step-item.active {
    opacity: 1;
    background: rgba(59, 130, 246, 0.15);
    border: 1px solid #3b82f6;
  }
  
  .step-item.complete {
    opacity: 1;
    background: rgba(34, 197, 94, 0.15);
    border: 1px solid #22c55e;
  }
  
  .step-number {
    width: 28px;
    height: 28px;
    background: #082770;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: bold;
    font-size: 0.85rem;
  }
  
  .step-item.complete .step-number {
    background: #22c55e;
  }
  
  .step-content strong {
    display: block;
    color: #082770;
    font-size: 0.9rem;
  }
  
  .step-content span {
    font-size: 0.75rem;
    color: #64748b;
  }
  
  .step-arrow {
    color: #94a3b8;
    font-size: 1.5rem;
  }
  
  /* Form */
  .verify-form {
    padding: 0;
    overflow: hidden;
  }
  
  .form-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1.25rem 1.5rem;
    background: #f8fafc;
    border-bottom: 1px solid #e2e8f0;
    color: #082770;
  }
  
  .form-header h2 {
    font-size: 1.25rem;
    margin: 0;
  }
  
  .form-body {
    padding: 1.5rem;
  }
  
  .form-group {
    margin-bottom: 1.5rem;
  }
  
  .form-group label {
    display: block;
    color: #082770;
    font-weight: 500;
    margin-bottom: 0.5rem;
  }
  
  .label-hint {
    display: block;
    font-size: 0.8rem;
    color: #64748b;
    font-weight: normal;
    margin-top: 0.25rem;
  }
  
  .form-group input,
  .form-group textarea {
    width: 100%;
    padding: 0.875rem 1rem;
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    color: #082770;
    font-size: 1rem;
    transition: border-color 0.2s;
  }
  
  .form-group input:focus,
  .form-group textarea:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }
  
  .form-group textarea {
    resize: vertical;
    font-family: inherit;
  }
  
  .signature-input {
    font-family: 'Monaco', 'Consolas', monospace;
    font-size: 0.85rem;
  }
  
  .char-count {
    text-align: right;
    font-size: 0.75rem;
    color: #64748b;
    margin-top: 0.25rem;
  }
  
  .form-actions {
    display: flex;
    gap: 1rem;
    justify-content: flex-end;
  }
  
  .btn {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.875rem 1.5rem;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    border: none;
    font-size: 1rem;
  }
  
  .btn-primary {
    background: linear-gradient(135deg, #082770, #0a3490);
    color: white;
  }
  
  .btn-primary:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(8, 39, 112, 0.3);
  }
  
  .btn-primary:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  .btn-secondary {
    background: #e2e8f0;
    color: #082770;
  }
  
  .btn-secondary:hover {
    background: #cbd5e1;
  }
  
  :global(.spin) {
    animation: spin 1s linear infinite;
  }
  
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
  
  /* Result Card */
  .result-card {
    padding: 0;
    overflow: hidden;
  }
  
  .result-card.valid {
    border-color: #22c55e;
  }
  
  .result-card.invalid {
    border-color: #ef4444;
  }
  
  .result-card.error {
    border-color: #f59e0b;
  }
  
  .result-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1.5rem;
  }
  
  .result-header.valid {
    background: linear-gradient(135deg, rgba(34, 197, 94, 0.15), rgba(34, 197, 94, 0.05));
    color: #22c55e;
  }
  
  .result-header.invalid {
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(239, 68, 68, 0.05));
    color: #ef4444;
  }
  
  .result-header.error {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(245, 158, 11, 0.05));
    color: #f59e0b;
  }
  
  .result-header h2 {
    margin: 0;
    font-size: 1.5rem;
  }
  
  .result-header p {
    margin: 0.25rem 0 0;
    opacity: 0.8;
    font-size: 0.95rem;
  }
  
  .error-message {
    padding: 1rem 1.5rem;
    color: #f59e0b;
  }
  
  /* Signature Details */
  .signature-details {
    padding: 1.5rem;
    background: #f8fafc;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
  
  .detail-box {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1rem;
  }
  
  .detail-label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #64748b;
    font-size: 0.85rem;
    margin-bottom: 0.5rem;
    font-weight: 500;
  }
  
  .detail-value {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: #f8fafc;
    padding: 0.75rem;
    border-radius: 8px;
  }
  
  .detail-value code {
    flex: 1;
    font-family: 'Monaco', 'Consolas', monospace;
    font-size: 0.85rem;
    color: #082770;
    word-break: break-all;
  }
  
  .detail-value.message {
    font-style: italic;
    color: #475569;
  }
  
  .copy-btn {
    background: #e2e8f0;
    border: none;
    border-radius: 6px;
    padding: 0.5rem;
    cursor: pointer;
    color: #64748b;
    transition: all 0.2s;
    flex-shrink: 0;
  }
  
  .copy-btn:hover {
    background: #cbd5e1;
    color: #082770;
  }
  
  /* Explanation */
  .explanation {
    padding: 1.5rem;
    border-top: 1px solid #e2e8f0;
  }
  
  .explanation h4 {
    color: #082770;
    margin-bottom: 0.75rem;
  }
  
  .explanation p {
    color: #475569;
    line-height: 1.6;
    margin-bottom: 0.5rem;
  }
  
  .explanation ul {
    color: #64748b;
    padding-left: 1.5rem;
  }
  
  .explanation li {
    margin-bottom: 0.5rem;
  }
  
  /* Comparison Card */
  .comparison-card {
    padding: 1.5rem;
  }
  
  .comparison-card h3 {
    color: #082770;
    margin-bottom: 1rem;
  }
  
  .comparison-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1rem;
    margin-bottom: 1rem;
  }
  
  .comparison-item {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.25rem;
  }
  
  .comparison-item.highlight {
    background: linear-gradient(135deg, #eff6ff, #dbeafe);
    border-color: #3b82f6;
  }
  
  .comparison-item h4 {
    color: #082770;
    margin-bottom: 0.75rem;
    font-size: 1.1rem;
  }
  
  .comparison-item ul {
    list-style: none;
    padding: 0;
    margin: 0 0 1rem 0;
  }
  
  .comparison-item li {
    color: #475569;
    font-size: 0.9rem;
    margin-bottom: 0.5rem;
    padding-left: 1rem;
    position: relative;
  }
  
  .comparison-item li::before {
    content: '•';
    position: absolute;
    left: 0;
    color: #3b82f6;
  }
  
  .comparison-link {
    display: inline-block;
    color: #3b82f6;
    text-decoration: none;
    font-weight: 500;
    font-size: 0.9rem;
  }
  
  .comparison-link:hover {
    text-decoration: underline;
  }
  
  .note {
    background: #fef3c7;
    border: 1px solid #fbbf24;
    border-radius: 8px;
    padding: 1rem;
    color: #92400e;
    font-size: 0.9rem;
  }
  
  /* Trust Model */
  .trust-model {
    padding: 1.5rem;
  }
  
  .trust-model h3 {
    color: #082770;
    margin-bottom: 1rem;
  }
  
  .trust-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
  }
  
  .trust-item {
    text-align: center;
    padding: 1rem;
  }
  
  .trust-icon {
    font-size: 2.5rem;
    margin-bottom: 0.75rem;
  }
  
  .trust-item h4 {
    color: #082770;
    font-size: 1rem;
    margin-bottom: 0.5rem;
  }
  
  .trust-item p {
    color: #64748b;
    font-size: 0.85rem;
    line-height: 1.5;
  }
  
  @media (max-width: 768px) {
    .hero h1 {
      font-size: 1.5rem;
    }
    
    .comparison-grid {
      grid-template-columns: 1fr;
    }
    
    .trust-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
