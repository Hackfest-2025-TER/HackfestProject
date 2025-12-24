<script lang="ts">
  import { Shield, User, Lock, Search, CheckCircle, AlertCircle, ChevronRight, Fingerprint, Eye, EyeOff, Info, Loader2 } from 'lucide-svelte';
  import { goto } from '$app/navigation';
  import { authStore } from '$lib/stores';
  import { lookupVoter, verifyZKProof, getMerkleRoot, searchVoters } from '$lib/api';
  import { generateZKProof, generateNullifier, isValidVoterId, isValidSecret, formatNullifier } from '$lib/utils/zkProof';
  
  // UI State
  let currentStep: 'search' | 'verify' | 'success' = 'search';
  let isLoading = false;
  let error = '';
  
  // Form State
  let voterIdInput = '';
  let secretInput = '';
  let showSecret = false;
  let searchQuery = '';
  let searchResults: any[] = [];
  let selectedVoter: any = null;
  
  // ZK State
  let voterLookupData: any = null;
  let generatedProof: any = null;
  let verificationResult: any = null;
  let merkleRoot = '';
  
  // Load merkle root on mount
  async function loadMerkleRoot() {
    try {
      const data = await getMerkleRoot();
      merkleRoot = data.merkle_root;
    } catch (e) {
      console.error('Failed to load merkle root:', e);
    }
  }
  
  // Search for voters by name
  async function handleSearch() {
    if (searchQuery.length < 2) {
      searchResults = [];
      return;
    }
    
    try {
      const data = await searchVoters(searchQuery);
      searchResults = data.results || [];
    } catch (e) {
      console.error('Search failed:', e);
      searchResults = [];
    }
  }
  
  // Select a voter from search results
  function selectVoter(voter: any) {
    selectedVoter = voter;
    voterIdInput = voter.voter_id_full;
    searchResults = [];
    searchQuery = voter.name;
  }
  
  // Manual voter ID entry
  function handleVoterIdInput() {
    selectedVoter = null;
  }
  
  // Step 1: Look up voter and get Merkle proof
  async function lookupAndProceed() {
    error = '';
    
    if (!voterIdInput.trim()) {
      error = 'Please enter your Voter ID (मतदाता नं)';
      return;
    }
    
    isLoading = true;
    
    try {
      const result = await lookupVoter(voterIdInput.trim());
      
      if (!result.found) {
        error = 'Voter ID not found in the registry. Please check your ID and try again.';
        isLoading = false;
        return;
      }
      
      voterLookupData = result;
      currentStep = 'verify';
    } catch (e) {
      error = 'Failed to connect to the registry. Please try again.';
      console.error(e);
    }
    
    isLoading = false;
  }
  
  // Step 2: Generate ZK proof and verify
  async function generateAndVerify() {
    error = '';
    
    if (!isValidSecret(secretInput)) {
      error = 'Your secret must be at least 6 characters. This could be your citizenship number or any secret only you know.';
      return;
    }
    
    isLoading = true;
    authStore.setLoading(true);
    
    try {
      // Generate ZK proof client-side
      const proof = await generateZKProof(
        voterIdInput.trim(),
        secretInput,
        voterLookupData.merkle_proof
      );
      
      generatedProof = proof;
      
      // Send proof to backend for verification (voter ID is NOT sent)
      const result = await verifyZKProof({
        voter_id_hash: proof.voterIdHash,
        nullifier: proof.nullifier,
        merkle_proof: proof.merkleProof,
        commitment: proof.commitment
      });
      
      if (!result.valid) {
        error = result.message || 'Proof verification failed. Please try again.';
        authStore.setError(error);
        isLoading = false;
        return;
      }
      
      verificationResult = result;
      
      // Store credential in auth store
      authStore.setCredential({
        nullifier: result.nullifier!,
        nullifierShort: result.nullifier_short || formatNullifier(result.nullifier!),
        credential: result.credential!,
        createdAt: new Date().toISOString(),
        usedVotes: [],
        verified: true
      });
      
      currentStep = 'success';
    } catch (e) {
      error = 'Verification failed. Please check your connection and try again.';
      console.error(e);
      authStore.setError(error);
    }
    
    isLoading = false;
  }
  
  // Navigate to manifestos after success
  function goToManifestos() {
    goto('/manifestos');
  }
  
  // Go back to search step
  function goBack() {
    currentStep = 'search';
    voterLookupData = null;
    secretInput = '';
    error = '';
  }
  
  // Initialize
  loadMerkleRoot();
</script>

<svelte:head>
  <title>Anonymous Voter Verification - PromiseThread</title>
</svelte:head>

<div class="auth-page">
  <header class="auth-header">
    <a href="/" class="logo">
      <div class="logo-icon">
        <Shield size={20} />
      </div>
      <div class="logo-text">
        <span class="logo-title">PromiseThread</span>
        <span class="logo-subtitle">BLIND AUDITOR SYSTEM</span>
      </div>
    </a>
    
    <div class="header-right">
      <span class="merkle-badge" title="Voter Registry Merkle Root">
        <Fingerprint size={14} />
        Root: {merkleRoot ? merkleRoot.slice(0, 8) + '...' : 'Loading...'}
      </span>
      <span class="status">
        <span class="status-dot online"></span>
        ZK_ACTIVE
      </span>
    </div>
  </header>
  
  <div class="auth-decoration">
    <div class="decoration-text">ZERO-KNOWLEDGE PROOF VERIFICATION</div>
  </div>
  
  <main class="auth-main">
    <div class="auth-card card">
      <!-- Step Indicator -->
      <div class="step-indicator">
        <div class="step" class:active={currentStep === 'search'} class:completed={currentStep !== 'search'}>
          <span class="step-number">1</span>
          <span class="step-label">Find Voter</span>
        </div>
        <div class="step-connector" class:active={currentStep !== 'search'}></div>
        <div class="step" class:active={currentStep === 'verify'} class:completed={currentStep === 'success'}>
          <span class="step-number">2</span>
          <span class="step-label">Verify</span>
        </div>
        <div class="step-connector" class:active={currentStep === 'success'}></div>
        <div class="step" class:active={currentStep === 'success'}>
          <span class="step-number">3</span>
          <span class="step-label">Verified</span>
        </div>
      </div>
      
      <!-- Step 1: Search/Find Voter -->
      {#if currentStep === 'search'}
        <div class="auth-card-header">
          <h1>Anonymous Voter Verification</h1>
          <p>Find your voter record to generate a Zero-Knowledge proof. Your identity remains private.</p>
        </div>
        
        <!-- Search by Name -->
        <div class="form-section">
          <label class="form-label">Search by Name (नाम खोज्नुहोस्)</label>
          <div class="search-wrapper">
            <Search size={18} />
            <input 
              type="text" 
              class="form-input" 
              placeholder="Type voter name..."
              bind:value={searchQuery}
              on:input={handleSearch}
            />
          </div>
          
          {#if searchResults.length > 0}
            <div class="search-results">
              {#each searchResults as voter}
                <button class="search-result-item" on:click={() => selectVoter(voter)}>
                  <div class="voter-info">
                    <span class="voter-name">{voter.name}</span>
                    <span class="voter-meta">Ward {voter.ward} • Age {voter.age} • {voter.gender}</span>
                  </div>
                  <span class="voter-id-partial">{voter.voter_id_partial}</span>
                </button>
              {/each}
            </div>
          {/if}
        </div>
        
        <div class="divider">
          <span>OR ENTER DIRECTLY</span>
        </div>
        
        <!-- Direct Voter ID Entry -->
        <div class="form-section">
          <label class="form-label">Voter ID (मतदाता नं)</label>
          <div class="input-wrapper">
            <User size={18} />
            <input 
              type="text" 
              class="form-input" 
              placeholder="Enter your voter ID number"
              bind:value={voterIdInput}
              on:input={handleVoterIdInput}
            />
          </div>
          {#if selectedVoter}
            <div class="selected-voter-badge">
              <CheckCircle size={14} />
              Selected: {selectedVoter.name} (Ward {selectedVoter.ward})
            </div>
          {/if}
        </div>
        
        {#if error}
          <div class="error-banner">
            <AlertCircle size={18} />
            <p>{error}</p>
          </div>
        {/if}
        
        <div class="info-banner">
          <Info size={18} />
          <p>
            <strong>How it works:</strong> We verify you're on the voter list, then generate a cryptographic proof. 
            Your actual Voter ID is NEVER sent to our servers - only the proof.
          </p>
        </div>
        
        <button class="submit-btn" on:click={lookupAndProceed} disabled={isLoading || !voterIdInput.trim()}>
          {#if isLoading}
            <Loader2 size={18} class="spinner" />
            Looking up...
          {:else}
            Continue
            <ChevronRight size={18} />
          {/if}
        </button>
      {/if}
      
      <!-- Step 2: Enter Secret & Generate Proof -->
      {#if currentStep === 'verify'}
        <div class="auth-card-header">
          <h1>Verify Your Identity</h1>
          <p>Enter your secret to verify and receive your anonymous credential.</p>
        </div>
        
        <!-- Voter Found Confirmation -->
        <div class="voter-found-card">
          <CheckCircle size={24} />
          <div>
            <strong>Voter Found in Registry</strong>
            <span>Name: {voterLookupData.name_masked} • Ward: {voterLookupData.ward}</span>
          </div>
        </div>
        
        <!-- Secret Input -->
        <div class="form-section">
          <label class="form-label">Your Secret (तपाईंको गोप्य)</label>
          <div class="input-wrapper">
            <Lock size={18} />
            {#if showSecret}
              <input 
                type="text"
                class="form-input" 
                placeholder="Demo: Enter 1234567890"
                bind:value={secretInput}
              />
            {:else}
              <input 
                type="password"
                class="form-input" 
                placeholder="Demo: Enter 1234567890"
                bind:value={secretInput}
              />
            {/if}
            <button class="toggle-secret" on:click={() => showSecret = !showSecret}>
              {#if showSecret}
                <EyeOff size={18} />
              {:else}
                <Eye size={18} />
              {/if}
            </button>
          </div>
          <p class="form-hint">
            <strong>Production:</strong> Your citizenship number (नागरिकता नं) securely delivered by Election Commission.
            <br />
            <strong>Demo:</strong> Use <code>1234567890</code> - pre-bound to all voters in demo registry.
          </p>
        </div>
        
        {#if error}
          <div class="error-banner">
            <AlertCircle size={18} />
            <p>{error}</p>
          </div>
        {/if}
        
        <div class="info-banner warning">
          <Shield size={18} />
          <div>
            <strong>Remember Your Secret!</strong>
            <p>Your secret + Voter ID creates your unique nullifier. Use the SAME secret every time to prevent double voting.</p>
          </div>
        </div>
        
        <div class="button-row">
          <button class="back-btn" on:click={goBack}>
            Back
          </button>
          <button class="submit-btn" on:click={generateAndVerify} disabled={isLoading || !secretInput}>
            {#if isLoading}
              <Loader2 size={18} class="spinner" />
              Verifying...
            {:else}
              <Fingerprint size={18} />
              Verify Identity
            {/if}
          </button>
        </div>
      {/if}
      
      <!-- Step 3: Success -->
      {#if currentStep === 'success'}
        <div class="success-content">
          <div class="success-icon">
            <CheckCircle size={48} />
          </div>
          
          <h1>Verification Complete!</h1>
          <p>Your anonymous credential has been issued. You can now vote on manifestos.</p>
          
          <div class="credential-display">
            <div class="credential-row">
              <span class="credential-label">Your Nullifier (Public ID)</span>
              <code class="credential-value">{verificationResult?.nullifier_short || '...'}</code>
            </div>
            <div class="credential-row">
              <span class="credential-label">Credential Token</span>
              <code class="credential-value">{verificationResult?.credential?.slice(0, 16)}...</code>
            </div>
            <div class="credential-row">
              <span class="credential-label">Registry Root</span>
              <code class="credential-value">{verificationResult?.merkle_root || merkleRoot.slice(0, 16)}...</code>
            </div>
          </div>
          
          <div class="info-banner success">
            <Shield size={18} />
            <div>
              <strong>Privacy Guaranteed</strong>
              <p>Your Voter ID was NEVER sent to our servers. Only your nullifier (derived from your secret) is stored to prevent double voting.</p>
            </div>
          </div>
          
          <button class="submit-btn" on:click={goToManifestos}>
            Browse Manifestos
            <ChevronRight size={18} />
          </button>
        </div>
      {/if}
      
      <div class="auth-footer">
        <span class="zk-badge">
          <Fingerprint size={12} />
          Zero-Knowledge Proof System
        </span>
        <div class="footer-links">
          <a href="/help">How it works</a>
          <span>•</span>
          <a href="/privacy">Privacy</a>
        </div>
      </div>
    </div>
  </main>
  
  <footer class="auth-page-footer">
    <p>© 2024 PromiseThread. Anonymous Political Accountability.</p>
  </footer>
</div>

<style>
  .auth-page {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    background: var(--gray-50);
  }
  
  .auth-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-4) var(--space-6);
    background: white;
    border-bottom: 1px solid var(--gray-200);
  }
  
  .logo {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    text-decoration: none;
    color: inherit;
  }
  
  .logo-icon {
    width: 40px;
    height: 40px;
    background: var(--primary-600);
    color: white;
    border-radius: var(--radius-lg);
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .logo-text {
    display: flex;
    flex-direction: column;
  }
  
  .logo-title {
    font-weight: 600;
    font-size: 1rem;
  }
  
  .logo-subtitle {
    font-size: 0.65rem;
    color: var(--gray-500);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  
  .header-right {
    display: flex;
    align-items: center;
    gap: var(--space-4);
  }
  
  .merkle-badge {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    font-family: var(--font-mono);
    font-size: 0.75rem;
    color: var(--gray-600);
    background: var(--gray-100);
    padding: var(--space-2) var(--space-3);
    border-radius: var(--radius-md);
  }
  
  .status {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    font-family: var(--font-mono);
    font-size: 0.75rem;
    color: var(--success-600);
  }
  
  .status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
  }
  
  .status-dot.online {
    background: var(--success-500);
    animation: pulse 2s infinite;
  }
  
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }
  
  .auth-decoration {
    height: 60px;
    background: linear-gradient(135deg, var(--primary-600) 0%, var(--primary-800) 100%);
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .decoration-text {
    font-family: var(--font-mono);
    font-size: 0.75rem;
    color: white;
    opacity: 0.8;
    letter-spacing: 0.2em;
  }
  
  .auth-main {
    flex: 1;
    display: flex;
    justify-content: center;
    padding: var(--space-8) var(--space-4);
  }
  
  .auth-card {
    width: 100%;
    max-width: 540px;
    padding: var(--space-8);
    background: white;
    border-radius: var(--radius-xl);
    box-shadow: var(--shadow-lg);
  }
  
  /* Step Indicator */
  .step-indicator {
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: var(--space-8);
  }
  
  .step {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--space-2);
  }
  
  .step-number {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: var(--gray-200);
    color: var(--gray-500);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 0.875rem;
    transition: all 0.3s;
  }
  
  .step.active .step-number {
    background: var(--primary-600);
    color: white;
  }
  
  .step.completed .step-number {
    background: var(--success-500);
    color: white;
  }
  
  .step-label {
    font-size: 0.75rem;
    color: var(--gray-500);
  }
  
  .step.active .step-label {
    color: var(--primary-600);
    font-weight: 500;
  }
  
  .step-connector {
    width: 60px;
    height: 2px;
    background: var(--gray-200);
    margin: 0 var(--space-2);
    margin-bottom: var(--space-6);
    transition: background 0.3s;
  }
  
  .step-connector.active {
    background: var(--primary-500);
  }
  
  /* Headers */
  .auth-card-header {
    text-align: center;
    margin-bottom: var(--space-6);
  }
  
  .auth-card-header h1 {
    font-size: 1.5rem;
    margin-bottom: var(--space-2);
    color: var(--gray-900);
  }
  
  .auth-card-header p {
    color: var(--gray-500);
    font-size: 0.875rem;
  }
  
  /* Form Elements */
  .form-section {
    margin-bottom: var(--space-5);
  }
  
  .form-label {
    display: block;
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--gray-700);
    margin-bottom: var(--space-2);
  }
  
  .search-wrapper,
  .input-wrapper {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    border: 1px solid var(--gray-300);
    border-radius: var(--radius-lg);
    padding: 0 var(--space-3);
    background: white;
    transition: all 0.2s;
  }
  
  .search-wrapper:focus-within,
  .input-wrapper:focus-within {
    border-color: var(--primary-500);
    box-shadow: 0 0 0 3px var(--primary-100);
  }
  
  .search-wrapper :global(svg),
  .input-wrapper :global(svg) {
    color: var(--gray-400);
    flex-shrink: 0;
  }
  
  .form-input {
    flex: 1;
    padding: var(--space-3) 0;
    border: none;
    background: transparent;
    font-size: 0.875rem;
    outline: none;
  }
  
  .form-hint {
    font-size: 0.75rem;
    color: var(--gray-500);
    margin-top: var(--space-2);
    line-height: 1.5;
  }
  
  .toggle-secret {
    background: none;
    border: none;
    color: var(--gray-400);
    cursor: pointer;
    padding: var(--space-1);
  }
  
  .toggle-secret:hover {
    color: var(--gray-600);
  }
  
  /* Search Results */
  .search-results {
    margin-top: var(--space-2);
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-lg);
    overflow: hidden;
    max-height: 200px;
    overflow-y: auto;
  }
  
  .search-result-item {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-3);
    background: white;
    border: none;
    border-bottom: 1px solid var(--gray-100);
    cursor: pointer;
    text-align: left;
    transition: background 0.2s;
  }
  
  .search-result-item:hover {
    background: var(--primary-50);
  }
  
  .search-result-item:last-child {
    border-bottom: none;
  }
  
  .voter-info {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }
  
  .voter-name {
    font-weight: 500;
    color: var(--gray-900);
  }
  
  .voter-meta {
    font-size: 0.75rem;
    color: var(--gray-500);
  }
  
  .voter-id-partial {
    font-family: var(--font-mono);
    font-size: 0.75rem;
    color: var(--gray-400);
  }
  
  .selected-voter-badge {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    margin-top: var(--space-2);
    padding: var(--space-2) var(--space-3);
    background: var(--success-50);
    color: var(--success-700);
    border-radius: var(--radius-md);
    font-size: 0.875rem;
  }
  
  /* Divider */
  .divider {
    display: flex;
    align-items: center;
    margin: var(--space-6) 0;
    color: var(--gray-400);
    font-size: 0.75rem;
  }
  
  .divider::before,
  .divider::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--gray-200);
  }
  
  .divider span {
    padding: 0 var(--space-4);
  }
  
  /* Banners */
  .info-banner {
    display: flex;
    gap: var(--space-3);
    padding: var(--space-4);
    background: var(--primary-50);
    border-radius: var(--radius-lg);
    margin-bottom: var(--space-6);
  }
  
  .info-banner :global(svg) {
    color: var(--primary-600);
    flex-shrink: 0;
    margin-top: 2px;
  }
  
  .info-banner p {
    font-size: 0.8rem;
    color: var(--gray-600);
    line-height: 1.5;
  }
  
  .info-banner.warning {
    background: var(--warning-50);
  }
  
  .info-banner.warning :global(svg) {
    color: var(--warning-600);
  }
  
  .info-banner.success {
    background: var(--success-50);
  }
  
  .info-banner.success :global(svg) {
    color: var(--success-600);
  }
  
  .info-banner div strong {
    display: block;
    margin-bottom: var(--space-1);
    color: var(--gray-900);
  }
  
  .error-banner {
    display: flex;
    gap: var(--space-3);
    padding: var(--space-4);
    background: var(--error-50);
    border: 1px solid var(--error-200);
    border-radius: var(--radius-lg);
    margin-bottom: var(--space-4);
  }
  
  .error-banner :global(svg) {
    color: var(--error-600);
    flex-shrink: 0;
  }
  
  .error-banner p {
    font-size: 0.875rem;
    color: var(--error-700);
  }
  
  /* Voter Found Card */
  .voter-found-card {
    display: flex;
    align-items: center;
    gap: var(--space-4);
    padding: var(--space-4);
    background: var(--success-50);
    border: 1px solid var(--success-200);
    border-radius: var(--radius-lg);
    margin-bottom: var(--space-6);
  }
  
  .voter-found-card :global(svg) {
    color: var(--success-600);
  }
  
  .voter-found-card strong {
    display: block;
    color: var(--success-800);
  }
  
  .voter-found-card span {
    font-size: 0.875rem;
    color: var(--success-600);
  }
  
  /* Buttons */
  .button-row {
    display: flex;
    gap: var(--space-3);
  }
  
  .back-btn {
    padding: var(--space-4) var(--space-6);
    background: white;
    color: var(--gray-700);
    border: 1px solid var(--gray-300);
    border-radius: var(--radius-lg);
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
  }
  
  .back-btn:hover {
    background: var(--gray-50);
  }
  
  .submit-btn {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--space-2);
    padding: var(--space-4);
    background: var(--primary-600);
    color: white;
    border: none;
    border-radius: var(--radius-lg);
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }
  
  .submit-btn:hover:not(:disabled) {
    background: var(--primary-700);
  }
  
  .submit-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  .submit-btn :global(.spinner) {
    animation: spin 1s linear infinite;
  }
  
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
  
  /* Success State */
  .success-content {
    text-align: center;
  }
  
  .success-icon {
    width: 80px;
    height: 80px;
    margin: 0 auto var(--space-6);
    background: var(--success-100);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .success-icon :global(svg) {
    color: var(--success-600);
  }
  
  .success-content h1 {
    font-size: 1.5rem;
    color: var(--gray-900);
    margin-bottom: var(--space-2);
  }
  
  .success-content > p {
    color: var(--gray-500);
    margin-bottom: var(--space-6);
  }
  
  .credential-display {
    background: var(--gray-900);
    border-radius: var(--radius-lg);
    padding: var(--space-4);
    margin-bottom: var(--space-6);
    text-align: left;
  }
  
  .credential-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--space-2) 0;
    border-bottom: 1px solid var(--gray-700);
  }
  
  .credential-row:last-child {
    border-bottom: none;
  }
  
  .credential-label {
    font-size: 0.75rem;
    color: var(--gray-400);
  }
  
  .credential-value {
    font-family: var(--font-mono);
    font-size: 0.8rem;
    color: var(--success-400);
  }
  
  /* Footer */
  .auth-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: var(--space-6);
    padding-top: var(--space-4);
    border-top: 1px solid var(--gray-200);
    font-size: 0.75rem;
  }
  
  .zk-badge {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    color: var(--primary-600);
    font-weight: 500;
  }
  
  .footer-links {
    display: flex;
    gap: var(--space-2);
    color: var(--gray-400);
  }
  
  .footer-links a {
    color: var(--gray-500);
    text-decoration: none;
  }
  
  .footer-links a:hover {
    color: var(--primary-600);
  }
  
  .auth-page-footer {
    text-align: center;
    padding: var(--space-4);
    font-size: 0.75rem;
    color: var(--gray-500);
  }
</style>
