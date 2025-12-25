<script lang="ts">
  import { Shield, User, Lock, CheckCircle, AlertCircle, ChevronRight, Eye, EyeOff, Loader2, KeyRound } from 'lucide-svelte';
  import { goto } from '$app/navigation';
  import { authStore } from '$lib/stores';
  import { lookupVoter, getMerkleRoot, searchVoters } from '$lib/api';
  import { isValidSecret } from '$lib/utils/zkProof';
  import { authenticateCitizen } from '$lib/zk/auth';
  
  // UI State
  let currentStep: 'search' | 'verify' | 'success' = 'search';
  let isLoading = false;
  let error = '';
  let statusMessage = ''; // New status message for ZK steps
  
  // Form State
  let voterIdInput = '';
  let secretInput = '';
  let showSecret = false;
  
  // Data State
  let voterLookupData: any = null;
  let verificationResult: any = null;
  let merkleRoot = '';
  
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

  // Browser-compatible SHA256
  async function sha256(message: string): Promise<string> {
    const msgBuffer = new TextEncoder().encode(message);
    const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  }

  // Compute commitment: hash(secret + voterID) - must match EC's computation
  async function computeCommitment(secret: string, voterId: string): Promise<string> {
    return await sha256(secret + voterId);
  }
  
  // Step 1: Basic voter ID validation (no server call needed)
  // With commitment scheme, we can't verify voter ID alone - need both ID + secret
  async function lookupAndProceed() {
    error = '';
    
    if (!voterIdInput.trim()) {
      error = 'Please enter your Voter ID';
      return;
    }

    // Basic format validation (voter IDs are numeric)
    if (!/^\d+$/.test(voterIdInput.trim())) {
      error = 'Voter ID should contain only numbers';
      return;
    }
    
    // With commitment scheme, we proceed to secret entry
    // The actual verification happens when both ID + secret are provided
    voterLookupData = {
      voter_id: voterIdInput.trim()
    };
    
    currentStep = 'verify';
  }
  
  // Step 2: Verify commitment and generate credentials (Purist Approach)
  // With commitment scheme: leaf = hash(secret + voterID)
  // Only the correct combination works!
  async function generateAndVerify() {
    error = '';
    statusMessage = '';
    
    if (!isValidSecret(secretInput)) {
      error = 'Please enter a valid secret (Citizenship Number)';
      return;
    }
    
    isLoading = true;
    
    try {
      // Use the Purist ZK Auth flow with commitment scheme
      // Voter ID and secret NEVER sent to server - only nullifier
      const result = await authenticateCitizen(
        voterIdInput.trim(), 
        secretInput.trim(),
        (status) => { statusMessage = status; }
        // No pre-fetched data - the new scheme needs to download fresh
      );
      
      verificationResult = result;
      
      if (result.success) {
        // Update auth store
        authStore.login(result.credential!, result.nullifier!);
        currentStep = 'success';
        
        // Redirect after delay
        setTimeout(() => {
          goto('/manifestos');
        }, 2000);
      } else {
        error = result.message || 'Verification failed';
      }
      
    } catch (e: any) {
      console.error('ZK Verification failed:', e);
      error = e.message || 'Failed to verify credentials. Please check your Voter ID and Citizenship Number.';
    }
    
    isLoading = false;
  }
  
  function goToManifestos() {
    goto('/manifestos');
  }
  
  function goBack() {
    currentStep = 'search';
    voterLookupData = null;
    secretInput = '';
    error = '';
  }
  
  loadMerkleRoot();
</script>

<svelte:head>
  <title>Verify Your Identity - PromiseThread</title>
</svelte:head>


<div class="auth-page">
  <main class="auth-main">
    <div class="auth-card">
      <!-- Step Indicator -->
      <div class="step-indicator">
        <div class="step" class:active={currentStep === 'search'} class:completed={currentStep !== 'search'}>
          <span class="step-number">1</span>
          <span class="step-label">Find Record</span>
        </div>
        <div class="step-connector" class:active={currentStep !== 'search'}></div>
        <div class="step" class:active={currentStep === 'verify'} class:completed={currentStep === 'success'}>
          <span class="step-number">2</span>
          <span class="step-label">Verify</span>
        </div>
        <div class="step-connector" class:active={currentStep === 'success'}></div>
        <div class="step" class:active={currentStep === 'success'}>
          <span class="step-number">3</span>
          <span class="step-label">Done</span>
        </div>
      </div>
      
      <!-- Step 1: Voter ID -->
      {#if currentStep === 'search'}
        <div class="auth-card-header">
          <div class="header-icon">
            <KeyRound size={32} />
          </div>
          <h1>Verify Your Identity</h1>
          <p>Enter your voter ID to get started. Your identity remains private.</p>
        </div>
        
        <div class="form-section">
          <label class="form-label">
            <User size={16} />
            Voter ID Number
          </label>
          <div class="input-wrapper">
            <input 
              type="text" 
              class="form-input" 
              placeholder="Enter your voter ID number"
              bind:value={voterIdInput}
            />
          </div>
          <p class="form-hint">
            Your voter ID can be found on your voter registration card.
          </p>
        </div>
        
        {#if error}
          <div class="error-banner">
            <AlertCircle size={18} />
            <p>{error}</p>
          </div>
        {/if}
        
        <div class="info-banner">
          <Shield size={20} />
          <div>
            <strong>Your Privacy is Protected</strong>
            <p>We verify you're a registered voter without storing any personal information. Your identity remains anonymous.</p>
          </div>
        </div>
        
        <button class="submit-btn" on:click={lookupAndProceed} disabled={isLoading || !voterIdInput.trim()}>
          {#if isLoading}
            <Loader2 size={18} class="spinner" />
            {statusMessage || 'Looking up...'}
          {:else}
            Continue
            <ChevronRight size={18} />
          {/if}
        </button>
      {/if}
      
      <!-- Step 2: Verify -->
      {#if currentStep === 'verify'}
        <div class="auth-card-header">
          <div class="header-icon">
            <Lock size={32} />
          </div>
          <h1>Enter Your Secret</h1>
          <p>Create a secret to verify your identity anonymously.</p>
        </div>
        
        <div class="voter-found-card">
          <CheckCircle size={24} />
          <div>
            <strong>Voter ID Verified Locally</strong>
            <span class="privacy-note">🔒 Your ID stays on your device - never sent to server</span>
          </div>
        </div>
        
        <div class="form-section">
          <label class="form-label">Your Citizenship Number (नागरिकता नं)</label>
          <div class="input-wrapper">
            {#if showSecret}
              <input 
                type="text"
                class="form-input" 
                placeholder="Enter your citizenship number"
                bind:value={secretInput}
              />
            {:else}
              <input 
                type="password"
                class="form-input" 
                placeholder="Enter your citizenship number"
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
            <strong>Production:</strong> Your citizenship number (नागरिकता नं) - only you know this.
            <br />
            <strong>Demo:</strong> Use <code>CITIZENSHIP_{voterIdInput}</code> (e.g., CITIZENSHIP_25327456)
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
            <strong>Commitment Scheme: hash(secret + voterID)</strong>
            <p>Your citizenship number + Voter ID together create your unique commitment. Only the correct combination will be found in the registry.</p>
          </div>
        </div>
        
        <div class="button-row">
          <button class="back-btn" on:click={goBack}>
            Back
          </button>
          <button class="submit-btn" on:click={generateAndVerify} disabled={isLoading || !secretInput}>
            {#if isLoading}
              <Loader2 size={18} class="spinner" />
              {statusMessage || 'Verifying...'}
            {:else}
              Verify
            {/if}
          </button>
        </div>
      {/if}
      
      <!-- Step 3: Success -->
      {#if currentStep === 'success'}
        <div class="success-content">
          <div class="success-icon">
            <CheckCircle size={56} />
          </div>
          
          <h1>You're Verified!</h1>
          <p>You can now share feedback on election promises anonymously.</p>
          
          <div class="info-banner success">
            <Shield size={18} />
            <div>
              <strong>Privacy Protected</strong>
              <p>Your identity is never revealed. Only you can prove you're a verified citizen.</p>
            </div>
          </div>
          
          <button class="submit-btn" on:click={goToManifestos}>
            Browse Promises
            <ChevronRight size={18} />
          </button>
        </div>
      {/if}
      
      <div class="auth-footer">
        <a href="/">Back to Home</a>
        <a href="/privacy">Privacy Policy</a>
      </div>
    </div>
  </main>
</div>

<style>
  .auth-page {
    min-height: 100vh;
    background-color: #0f172a;
    display: flex;
    flex-direction: column;
    color: white;
  }
  
  .auth-main {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem;
  }
  
  .auth-card {
    width: 100%;
    max-width: 500px;
    background: rgba(30, 41, 59, 0.6);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 24px;
    padding: 2.5rem;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  }
  
  /* Step Indicator */
  .step-indicator {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 2.5rem;
    padding: 0 1rem;
  }
  
  .step {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    position: relative;
    z-index: 1;
  }
  
  .step-number {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.1);
    color: var(--gray-400);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 0.875rem;
    transition: all 0.3s;
    border: 1px solid rgba(255, 255, 255, 0.1);
  }
  
  .step.active .step-number {
    background: var(--primary-500);
    color: white;
    border-color: var(--primary-500);
    box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.2);
  }
  
  .step.completed .step-number {
    background: var(--success-500);
    color: white;
    border-color: var(--success-500);
  }
  
  .step-label {
    font-size: 0.75rem;
    font-weight: 500;
    color: var(--gray-500);
  }
  
  .step.active .step-label {
    color: white;
  }
  
  .step-connector {
    flex: 1;
    height: 2px;
    background: rgba(255, 255, 255, 0.1);
    margin: 0 1rem;
    margin-bottom: 1.25rem; /* Align with circle center */
  }
  
  .step-connector.active {
    background: var(--success-500);
  }
  
  /* Headers */
  .auth-card-header {
    text-align: center;
    margin-bottom: 2.5rem;
  }
  
  .header-icon {
    width: 64px;
    height: 64px;
    margin: 0 auto 1.5rem;
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(59, 130, 246, 0.1));
    border: 2px solid rgba(59, 130, 246, 0.3);
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--primary-400);
  }
  
  .auth-card-header h1 {
    font-size: 1.75rem;
    font-weight: 700;
    color: white;
    margin-bottom: 0.5rem;
  }
  
  .auth-card-header p {
    color: var(--gray-400);
    font-size: 0.95rem;
    line-height: 1.5;
  }
  
  /* Forms */
  .form-section {
    margin-bottom: 1.5rem;
  }
  
  .form-label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--gray-300);
    margin-bottom: 0.75rem;
  }
  
  .form-label :global(svg) {
    color: var(--gray-500);
  }
  
  .form-hint {
    margin-top: 0.5rem;
    font-size: 0.8125rem;
    color: var(--gray-500);
    line-height: 1.5;
  }
  
  .input-wrapper {
    position: relative;
  }
  
  .form-input,
  input[type="text"],
  input[type="password"] {
    width: 100%;
    padding: 0.875rem 1rem;
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    color: white;
    font-size: 1rem;
    transition: all 0.2s;
  }
  
  input[type="text"]:focus,
  input[type="password"]:focus {
    outline: none;
    border-color: var(--primary-500);
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
    background: rgba(15, 23, 42, 0.8);
  }
  
  .toggle-secret {
    position: absolute;
    right: 1rem;
    top: 50%;
    transform: translateY(-50%);
    background: none;
    border: none;
    color: var(--gray-500);
    cursor: pointer;
    padding: 0.25rem;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 6px;
    transition: all 0.2s;
  }
  
  .toggle-secret:hover {
    color: white;
    background: rgba(255, 255, 255, 0.05);
  }
  
  /* Auth Footer */
  .auth-footer {
    display: flex;
    justify-content: center;
    gap: 2rem;
    margin-top: 2rem;
    padding-top: 1.5rem;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
  }
  
  .auth-footer a {
    color: var(--gray-400);
    font-size: 0.875rem;
    text-decoration: none;
    transition: color 0.2s;
  }
  
  .auth-footer a:hover {
    color: white;
  }
  
  /* Banners */
  .info-banner {
    display: flex;
    gap: 0.75rem;
    padding: 1rem;
    background: rgba(59, 130, 246, 0.1);
    border: 1px solid rgba(59, 130, 246, 0.2);
    border-radius: 12px;
    margin-bottom: 1.5rem;
  }
  
  .info-banner :global(svg) {
    color: var(--primary-400);
    flex-shrink: 0;
    margin-top: 2px;
  }
  
  .info-banner p {
    font-size: 0.85rem;
    color: var(--gray-300);
    line-height: 1.5;
  }
  
  .info-banner.warning {
    background: rgba(245, 158, 11, 0.1);
    border-color: rgba(245, 158, 11, 0.2);
  }
  
  .info-banner.warning :global(svg) {
    color: var(--warning-400);
  }
  
  .info-banner.success {
    background: rgba(16, 185, 129, 0.1);
    border-color: rgba(16, 185, 129, 0.2);
  }
  
  .info-banner.success :global(svg) {
    color: var(--success-400);
  }
  
  .info-banner div strong {
    display: block;
    margin-bottom: 0.25rem;
    color: white;
    font-size: 0.9rem;
  }
  
  .error-banner {
    display: flex;
    gap: 0.75rem;
    padding: 1rem;
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.2);
    border-radius: 12px;
    margin-bottom: 1rem;
  }
  
  .error-banner :global(svg) {
    color: var(--error-500);
    flex-shrink: 0;
  }
  
  .error-banner p {
    font-size: 0.875rem;
    color: var(--error-400);
  }
  
  /* Voter Found Card */
  .voter-found-card {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.2);
    border-radius: 12px;
    margin-bottom: 1.5rem;
  }
  
  .voter-found-card :global(svg) {
    color: var(--success-400);
  }
  
  .voter-found-card strong {
    display: block;
    color: var(--success-300);
    font-size: 0.95rem;
  }
  
  .voter-found-card span {
    font-size: 0.85rem;
    color: var(--success-400);
  }
  
  /* Buttons */
  .button-row {
    display: flex;
    gap: 1rem;
  }
  
  .back-btn {
    padding: 0.75rem 1.25rem;
    background: transparent;
    color: var(--gray-300);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    font-size: 0.95rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
  }
  
  .back-btn:hover {
    background: rgba(255, 255, 255, 0.05);
    color: white;
  }
  
  .submit-btn {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 0.75rem 1.25rem;
    background: var(--primary-600);
    color: white;
    border: none;
    border-radius: 12px;
    font-size: 0.95rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
  }
  
  .submit-btn:hover:not(:disabled) {
    background: var(--primary-500);
  }
  
  .submit-btn:disabled {
    opacity: 0.5;
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
    margin: 0 auto 1.5rem;
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.2);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .success-icon :global(svg) {
    color: var(--success-400);
  }
  
  .success-content h1 {
    font-size: 1.5rem;
    color: white;
    margin-bottom: 0.5rem;
  }
  
  .success-content > p {
    color: var(--gray-400);
    margin-bottom: 2rem;
  }
</style>