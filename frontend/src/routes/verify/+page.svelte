<script lang="ts">
  import HashDisplay from '$lib/components/HashDisplay.svelte';
  import { Shield, Search, CheckCircle, XCircle, FileText, Link, Clock, AlertTriangle, Copy, ExternalLink, RefreshCw } from 'lucide-svelte';

  // State
  let manifestoId: number | null = null;
  let manifestoText = '';
  let isVerifying = false;
  let verificationResult: any = null;
  let localHash = '';
  let blockchainHash = '';
  let showAdvanced = false;
  
  // Step tracking for UX
  let currentStep = 0;
  
  /**
   * STEP 1: Local Hash Computation (CRITICAL - happens in browser)
   * This is the most important part - the backend NEVER touches this value.
   * Even if the backend is malicious, this verification still works.
   */
  async function computeLocalHash(text: string): Promise<string> {
    const encoder = new TextEncoder();
    const data = encoder.encode(text);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    return '0x' + hashHex; // Full 64-char SHA256 hash (no truncation!)
  }
  
  /**
   * STEP 2: Fetch Blockchain Hash
   * Backend acts only as RPC proxy - not as authority.
   */
  async function fetchBlockchainHash(manifestoId: number): Promise<any> {
    const response = await fetch(`http://localhost:8000/api/manifestos/${manifestoId}`);
    if (!response.ok) {
      throw new Error('Failed to fetch blockchain hash');
    }
    const data = await response.json();
    return { hash: data.hash, manifesto: data };
  }
  
  /**
   * MAIN VERIFICATION FLOW
   */
  async function verifyManifesto() {
    if (!manifestoId || !manifestoText.trim()) {
      alert('Please enter manifesto ID and manifesto text');
      return;
    }
    
    isVerifying = true;
    verificationResult = null;
    currentStep = 1;
    
    try {
      // STEP 1: Compute local hash (in browser - trustless)
      localHash = await computeLocalHash(manifestoText);
      currentStep = 2;
      
      // Small delay for UX
      await new Promise(r => setTimeout(r, 500));
      
      // STEP 2: Fetch blockchain hash
      const blockchainData = await fetchBlockchainHash(manifestoId);
      blockchainHash = blockchainData.hash;
      currentStep = 3;
      
      await new Promise(r => setTimeout(r, 500));
      
      // STEP 3: Compare hashes
      const isValid = localHash === blockchainHash;
      currentStep = 4;
      
      verificationResult = {
        valid: isValid,
        localHash,
        blockchainHash,
        blockchainData,
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
   * Copy hash to clipboard
   */
  function copyHash(hash: string) {
    navigator.clipboard.writeText(hash);
  }
  
  /**
   * Load sample data - randomly selects valid or tampered scenario
   */
  function loadSample() {
    const scenarios = [
      // VALID - Exact match with blockchain (Manifesto ID 1)
      // Backend generates hash as: title:description:politician_id
      {
        manifestoId: 1,
        manifestoText: `धुलिखेल-काभ्रे सडक विस्तार:धुलिखेलदेखि काभ्रेसम्मको सडकलाई चार लेन बनाउने। यो परियोजनाले यातायात सुधार गर्नेछ र आर्थिक विकासमा योगदान पुर्याउनेछ।:1`
      },
      // TAMPERED - Text has been modified (Manifesto ID 2 with extra word "अति")
      {
        manifestoId: 2,
        manifestoText: `प्रत्येक गाउँमा स्वास्थ्य चौकी:हरेक गाउँमा कम्तीमा एक अति स्वास्थ्य चौकी स्थापना गर्ने र आधारभूत स्वास्थ्य सेवा सुनिश्चित गर्ने।:2`
        // Note: The word "अति" was added after "एक" - original doesn't have it
      }
    ];
    
    const selected = scenarios[Math.floor(Math.random() * scenarios.length)];
    manifestoId = selected.manifestoId;
    manifestoText = selected.manifestoText;
  }
</script>

<svelte:head>
  <title>Verify Manifesto - PromiseThread</title>
</svelte:head>

<main class="verify-page">
  <div class="container">
    <!-- Hero Section -->
    <div class="hero">
      <div class="hero-icon">
        <Shield size={48} />
      </div>
      <h1>Verify Promise Hash</h1>
      <p class="hero-subtitle">
        Independently verify that a promise's text matches its blockchain hash.
        <strong>Your verification happens in your browser</strong> — we never see your data.
      </p>
    </div>
    
    <!-- How It Works -->
    <div class="info-card">
      <h3>🔐 How Trustless Verification Works</h3>
      <div class="steps-overview">
        <div class="step-item" class:active={currentStep >= 1} class:complete={currentStep > 1}>
          <div class="step-number">1</div>
          <div class="step-content">
            <strong>Local Hash</strong>
            <span>SHA-256 computed in YOUR browser</span>
          </div>
        </div>
        <div class="step-arrow">→</div>
        <div class="step-item" class:active={currentStep >= 2} class:complete={currentStep > 2}>
          <div class="step-number">2</div>
          <div class="step-content">
            <strong>Blockchain Hash</strong>
            <span>Fetched from immutable ledger</span>
          </div>
        </div>
        <div class="step-arrow">→</div>
        <div class="step-item" class:active={currentStep >= 3} class:complete={currentStep > 3}>
          <div class="step-number">3</div>
          <div class="step-content">
            <strong>Compare</strong>
            <span>Match = Authentic</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Main Verification Form -->
    <div class="verify-form card">
      <div class="form-header">
        <FileText size={24} />
        <h2>Enter Manifesto Details</h2>
      </div>
      
      <div class="form-body">
        <!-- Manifesto ID Input -->
        <div class="form-group">
          <label for="manifesto-id">
            Manifesto/Promise ID
            <span class="label-hint">The unique ID of the promise you want to verify</span>
          </label>
          <input 
            type="number" 
            id="manifesto-id"
            bind:value={manifestoId}
            placeholder="Enter manifesto ID (e.g., 1)"
            min="1"
          />
        </div>
        
        <!-- Manifesto Text Input -->
        <div class="form-group">
          <label for="manifesto-text">
            Manifesto Text
            <span class="label-hint">Paste the exact manifesto text you want to verify</span>
          </label>
          <textarea 
            id="manifesto-text"
            bind:value={manifestoText}
            placeholder="Paste the complete manifesto text here...

The text must match EXACTLY what was originally submitted. Even a single character difference will cause verification to fail (this is a feature, not a bug!)."
            rows="8"
          />
          <div class="char-count">{manifestoText.length} characters</div>
        </div>
        
        <!-- Action Buttons -->
        <div class="form-actions">
          <button class="btn btn-secondary" on:click={loadSample}>
            Load Sample
          </button>
          <button 
            class="btn btn-primary" 
            on:click={verifyManifesto}
            disabled={isVerifying || !manifestoId || !manifestoText.trim()}
          >
            {#if isVerifying}
              <RefreshCw size={18} class="spin" />
              Verifying...
            {:else}
              <Search size={18} />
              Verify Authenticity
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
          <!-- AUTHENTIC -->
          <div class="result-header valid">
            <CheckCircle size={48} />
            <div>
              <h2>✅ AUTHENTIC</h2>
              <p>This manifesto has NOT been tampered with</p>
            </div>
          </div>
        {:else}
          <!-- TAMPERED -->
          <div class="result-header invalid">
            <XCircle size={48} />
            <div>
              <h2>❌ TAMPERED OR DIFFERENT</h2>
              <p>The hashes do not match — text has been modified</p>
            </div>
          </div>
        {/if}
        
        {#if !verificationResult.error}
          <!-- Hash Comparison -->
          <div class="hash-comparison">
            <div class="hash-box">
              <div class="hash-label">
                <span class="label-icon local">🖥️</span>
                Your Local Hash
                <span class="hash-note">(computed in browser)</span>
              </div>
              <div class="hash-value">
                <code>{verificationResult.localHash}</code>
                <button class="copy-btn" on:click={() => copyHash(verificationResult.localHash)}>
                  <Copy size={14} />
                </button>
              </div>
            </div>
            
            <div class="comparison-symbol">
              {verificationResult.valid ? '=' : '≠'}
            </div>
            
            <div class="hash-box">
              <div class="hash-label">
                <span class="label-icon blockchain">⛓️</span>
                Blockchain Hash
                <span class="hash-note">(immutable)</span>
              </div>
              <div class="hash-value">
                <code>{verificationResult.blockchainHash}</code>
                <button class="copy-btn" on:click={() => copyHash(verificationResult.blockchainHash)}>
                  <Copy size={14} />
                </button>
              </div>
            </div>
          </div>
          
          <!-- Blockchain Details -->
          {#if verificationResult.blockchainData}
            <div class="blockchain-details">
              <h4>📦 Blockchain Record</h4>
              <div class="details-grid">
                <div class="detail-item">
                  <span class="detail-label">Contract</span>
                  <code class="detail-value">{verificationResult.blockchainData.contract_address}</code>
                </div>
                <div class="detail-item">
                  <span class="detail-label">Chain</span>
                  <span class="detail-value">{verificationResult.blockchainData.chain_name} (ID: {verificationResult.blockchainData.chain_id})</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">Block #</span>
                  <span class="detail-value">{verificationResult.blockchainData.block_number}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">Recorded</span>
                  <span class="detail-value">{new Date(verificationResult.blockchainData.timestamp).toLocaleString()}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">Politician</span>
                  <span class="detail-value">{verificationResult.blockchainData.politician_name}</span>
                </div>
              </div>
            </div>
          {/if}
          
          <!-- Advanced: Show how to verify independently -->
          <button class="toggle-advanced" on:click={() => showAdvanced = !showAdvanced}>
            {showAdvanced ? '▼ Hide' : '▶ Show'} Independent Verification Instructions
          </button>
          
          {#if showAdvanced}
            <div class="advanced-section">
              <h4>🔍 Verify Without This Website</h4>
              <p>You don't need to trust us. Here's how to verify independently:</p>
              
              <div class="code-block">
                <strong>Option 1: JavaScript (Browser Console)</strong>
                <pre>{`// Paste manifesto text
const text = \`${manifestoText.substring(0, 100)}...\`;

// Compute hash
const encoder = new TextEncoder();
const data = encoder.encode(text);
const hashBuffer = await crypto.subtle.digest('SHA-256', data);
const hashArray = Array.from(new Uint8Array(hashBuffer));
const hash = '0x' + hashArray.map(b => b.toString(16).padStart(2, '0')).join('');

console.log('Your hash:', hash);
// Compare with: ${verificationResult.blockchainHash}`}</pre>
              </div>
              
              <div class="code-block">
                <strong>Option 2: Python</strong>
                <pre>{`import hashlib
text = """${manifestoText.substring(0, 100)}..."""
hash = '0x' + hashlib.sha256(text.encode()).hexdigest()
print(f'Your hash: {hash}')
# Compare with: ${verificationResult.blockchainHash}`}</pre>
              </div>
              
              <div class="code-block">
                <strong>Option 3: Query Blockchain Directly</strong>
                <pre>{`curl -X POST ${verificationResult.blockchainData?.rpc_url || 'http://localhost:8545'} \\
  -H "Content-Type: application/json" \\
  --data '{
    "jsonrpc":"2.0",
    "method":"eth_call",
    "params":[{
      "to":"${verificationResult.blockchainData?.contract_address}",
      "data":"0x87e0150f..." // verifyManifesto(politicianId, hash)
    }, "latest"],
    "id":1
  }'`}</pre>
              </div>
            </div>
          {/if}
        {/if}
      </div>
    {/if}
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
    background: linear-gradient(135deg, #3b82f6, #8b5cf6);
    border-radius: 20px;
    margin-bottom: 1rem;
    color: #082770;
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
    color: #22c55e;
  }
  
  /* Cards */
  .card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    margin-bottom: 1.5rem;
  }
  
  /* Info Card */
  .info-card {
    background: linear-gradient(135deg, #1e3a5f 0%, #1e293b 100%);
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
    background: rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    opacity: 0.5;
    transition: all 0.3s;
  }
  
  .step-item.active {
    opacity: 1;
    background: rgba(59, 130, 246, 0.2);
    border: 1px solid #3b82f6;
  }
  
  .step-item.complete {
    opacity: 1;
    background: rgba(34, 197, 94, 0.2);
    border: 1px solid #22c55e;
  }
  
  .step-number {
    width: 28px;
    height: 28px;
    background: #3b82f6;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #082770;
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
    color: #64748b;
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
    border-bottom: 1px solid #334155;
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
    background: #f8fafc;
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
  }
  
  .form-group textarea {
    resize: vertical;
    min-height: 150px;
    font-family: inherit;
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
    background: linear-gradient(135deg, #3b82f6, #8b5cf6);
    color: #082770;
  }
  
  .btn-primary:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
  }
  
  .btn-primary:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  .btn-secondary {
    background: #334155;
    color: #082770;
  }
  
  .btn-secondary:hover {
    background: #475569;
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
    background: linear-gradient(135deg, rgba(34, 197, 94, 0.2), rgba(34, 197, 94, 0.05));
    color: #22c55e;
  }
  
  .result-header.invalid {
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(239, 68, 68, 0.05));
    color: #ef4444;
  }
  
  .result-header.error {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(245, 158, 11, 0.05));
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
    color: #fbbf24;
  }
  
  /* Hash Comparison */
  .hash-comparison {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1.5rem;
    background: #f8fafc;
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .hash-box {
    flex: 1;
    min-width: 280px;
    background: white;
    border-radius: 12px;
    padding: 1rem;
  }
  
  .hash-label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #64748b;
    font-size: 0.85rem;
    margin-bottom: 0.5rem;
  }
  
  .label-icon {
    font-size: 1.1rem;
  }
  
  .hash-note {
    font-size: 0.75rem;
    opacity: 0.7;
  }
  
  .hash-value {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: #f8fafc;
    padding: 0.75rem;
    border-radius: 8px;
  }
  
  .hash-value code {
    flex: 1;
    font-family: 'Monaco', 'Consolas', monospace;
    font-size: 0.85rem;
    color: #22d3ee;
    word-break: break-all;
  }
  
  .copy-btn {
    background: #334155;
    border: none;
    border-radius: 6px;
    padding: 0.5rem;
    cursor: pointer;
    color: #64748b;
    transition: all 0.2s;
  }
  
  .copy-btn:hover {
    background: #475569;
    color: #082770;
  }
  
  .comparison-symbol {
    font-size: 2rem;
    font-weight: bold;
    color: #64748b;
    padding: 0 0.5rem;
  }
  
  .result-card.valid .comparison-symbol {
    color: #22c55e;
  }
  
  .result-card.invalid .comparison-symbol {
    color: #ef4444;
  }
  
  /* Blockchain Details */
  .blockchain-details {
    padding: 1.5rem;
    border-top: 1px solid #334155;
  }
  
  .blockchain-details h4 {
    color: #082770;
    margin-bottom: 1rem;
  }
  
  .details-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
  }
  
  .detail-item {
    background: #f8fafc;
    padding: 0.75rem 1rem;
    border-radius: 8px;
  }
  
  .detail-label {
    display: block;
    font-size: 0.75rem;
    color: #64748b;
    margin-bottom: 0.25rem;
  }
  
  .detail-value {
    color: #082770;
    font-size: 0.9rem;
  }
  
  code.detail-value {
    font-family: 'Monaco', 'Consolas', monospace;
    font-size: 0.8rem;
    color: #22d3ee;
    word-break: break-all;
  }
  
  /* Advanced Section */
  .toggle-advanced {
    display: block;
    width: 100%;
    padding: 1rem;
    background: transparent;
    border: none;
    border-top: 1px solid #334155;
    color: #3b82f6;
    font-size: 0.9rem;
    cursor: pointer;
    text-align: left;
    transition: background 0.2s;
  }
  
  .toggle-advanced:hover {
    background: rgba(59, 130, 246, 0.1);
  }
  
  .advanced-section {
    padding: 1.5rem;
    background: #f8fafc;
    border-top: 1px solid #334155;
  }
  
  .advanced-section h4 {
    color: #082770;
    margin-bottom: 0.5rem;
  }
  
  .advanced-section > p {
    color: #64748b;
    margin-bottom: 1rem;
  }
  
  .code-block {
    margin-bottom: 1rem;
    background: white;
    border-radius: 8px;
    padding: 1rem;
  }
  
  .code-block strong {
    display: block;
    color: #f59e0b;
    margin-bottom: 0.5rem;
    font-size: 0.85rem;
  }
  
  .code-block pre {
    margin: 0;
    padding: 0.75rem;
    background: #f8fafc;
    border-radius: 6px;
    overflow-x: auto;
    font-family: 'Monaco', 'Consolas', monospace;
    font-size: 0.8rem;
    color: #22d3ee;
    white-space: pre-wrap;
    word-break: break-word;
  }
  
  /* Trust Model */
  .trust-model {
    padding: 1.5rem;
  }
  
  .trust-model h3 {
    color: #082770;
    margin-bottom: 1.5rem;
    text-align: center;
  }
  
  .trust-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
  }
  
  .trust-item {
    text-align: center;
  }
  
  .trust-icon {
    font-size: 2rem;
    margin-bottom: 0.5rem;
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
  
  .trust-item strong {
    color: #22c55e;
  }
  
  /* Responsive */
  @media (max-width: 768px) {
    .hero h1 {
      font-size: 1.5rem;
    }
    
    .steps-overview {
      flex-direction: column;
    }
    
    .step-arrow {
      transform: rotate(90deg);
    }
    
    .hash-comparison {
      flex-direction: column;
    }
    
    .comparison-symbol {
      transform: rotate(90deg);
    }
  }
</style>
