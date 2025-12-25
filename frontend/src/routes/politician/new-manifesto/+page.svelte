<script lang="ts">
  import Header from '$lib/components/Header.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import { Shield, Upload, Plus, Trash2, FileText, Info, Trees, Lightbulb, Key, Lock, AlertTriangle, CheckCircle, Loader } from 'lucide-svelte';
  import HashDisplay from '$lib/components/HashDisplay.svelte';
  import { onMount } from 'svelte';
  import { getPoliticianWalletStatus, submitSignedManifesto } from '$lib/api';
  import { computeSHA256, parseKeystore, signMessage, decryptKeystore, formatAddress } from '$lib/utils/crypto';
  
  // Form state
  let manifestoTitle = '';
  let executiveSummary = '';
  let promises: { id: number; title: string; category: string; description: string }[] = [];
  
  let newPromiseTitle = '';
  let newPromiseCategory = 'economy';
  let newPromiseDescription = '';
  
  // Signing state
  let walletStatus: { has_wallet: boolean; wallet_address?: string; key_version?: number } | null = null;
  let keystoreFile: File | null = null;
  let keystoreData: any = null;
  let passphrase = '';
  let signingStep: 'check-wallet' | 'upload-keystore' | 'enter-passphrase' | 'signing' | 'complete' = 'check-wallet';
  let isSubmitting = false;
  let submitError = '';
  let submitSuccess = false;
  let manifestoHash = '';
  let signature = '';
  
  // Politician ID (in production, get from auth context)
  const politicianId = 1;
  
  const categories = [
    { value: 'economy', label: 'Economy' },
    { value: 'healthcare', label: 'Healthcare' },
    { value: 'education', label: 'Education' },
    { value: 'environment', label: 'Environment' },
    { value: 'infrastructure', label: 'Infrastructure' },
    { value: 'technology', label: 'Technology & Governance' }
  ];
  
  onMount(async () => {
    await checkWalletStatus();
  });
  
  async function checkWalletStatus() {
    try {
      walletStatus = await getPoliticianWalletStatus(politicianId);
      if (walletStatus?.has_wallet) {
        signingStep = 'upload-keystore';
      }
    } catch (e) {
      console.error('Failed to check wallet status:', e);
    }
  }
  
  function addPromise() {
    if (newPromiseTitle && newPromiseDescription) {
      promises = [...promises, {
        id: Date.now(),
        title: newPromiseTitle,
        category: newPromiseCategory,
        description: newPromiseDescription
      }];
      newPromiseTitle = '';
      newPromiseDescription = '';
    }
  }
  
  function removePromise(id: number) {
    promises = promises.filter(p => p.id !== id);
  }
  
  async function handleKeystoreUpload(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      keystoreFile = input.files[0];
      try {
        const text = await keystoreFile.text();
        keystoreData = parseKeystore(text);
        if (keystoreData) {
          signingStep = 'enter-passphrase';
        } else {
          submitError = 'Invalid keystore file format';
        }
      } catch (e) {
        submitError = 'Failed to read keystore file';
      }
    }
  }
  
  function buildManifestoContent(): string {
    // The backend computes hash from description only
    // So we just return the description for consistency
    return executiveSummary;
  }
  
  async function handleSubmit(event: Event) {
    event.preventDefault();
    
    if (!manifestoTitle || !executiveSummary) {
      submitError = 'Please fill in the title and summary';
      return;
    }
    
    if (!keystoreData || !passphrase) {
      submitError = 'Please upload your keystore and enter passphrase';
      return;
    }
    
    submitError = '';
    isSubmitting = true;
    signingStep = 'signing';
    
    try {
      // Build content and compute hash
      const content = buildManifestoContent();
      const hash = await computeSHA256(content);
      // Keep full hash with 0x prefix for backend compatibility
      manifestoHash = hash.startsWith('0x') ? hash : '0x' + hash;
      
      // Decrypt keystore and sign
      const privateKey = await decryptKeystore(keystoreData, passphrase);
      if (!privateKey) {
        throw new Error('Failed to decrypt keystore. Check your passphrase.');
      }
      
      // Sign the hash (pass wallet address for simplified verification)
      const hashForSigning = manifestoHash.startsWith('0x') ? manifestoHash.slice(2) : manifestoHash;
      signature = await signMessage(hashForSigning, privateKey, walletStatus?.wallet_address);
      
      // Submit to backend
      const result = await submitSignedManifesto({
        politician_id: politicianId,
        title: manifestoTitle,
        description: executiveSummary,  // Backend expects 'description'
        category: promises[0]?.category || 'general',
        grace_period_days: 7,
        manifesto_hash: manifestoHash,  // Send full hash with 0x prefix
        signature: signature
      });
      
      if (result.id) {
        submitSuccess = true;
        signingStep = 'complete';
      } else {
        throw new Error(result.error || 'Submission failed');
      }
    } catch (e: any) {
      submitError = e.message || 'Failed to sign and submit manifesto';
      signingStep = 'enter-passphrase';
    } finally {
      isSubmitting = false;
    }
  }
  
  $: previewHash = manifestoHash 
    ? (manifestoHash.startsWith('0x') 
        ? `${manifestoHash.slice(0, 10)}...${manifestoHash.slice(-4)}`
        : `0x${manifestoHash.slice(0, 8)}...${manifestoHash.slice(-4)}`)
    : '0x7f839a2b...c9d1';
</script>

<svelte:head>
  <title>Draft New Manifesto - Politician Portal</title>
</svelte:head>

<Header variant="politician" />

<main class="draft-page">
  <div class="container">
    <!-- Breadcrumb -->
    <div class="breadcrumb">
      <a href="/politician/dashboard">Dashboard</a>
      <span>/</span>
      <span class="current">New Manifesto</span>
    </div>
    
    <div class="page-header">
      <div class="header-content">
        <h1>Draft New Manifesto</h1>
        <p>Define your commitments for the 2024 Election Cycle. All data is cryptographically signed and publicly verifiable.</p>
      </div>
      <div class="secure-badge">
        <span class="status-dot online"></span>
        SECURE NODE CONNECTED
      </div>
    </div>
    
    <!-- Main Form -->
    <form class="manifesto-form" on:submit={handleSubmit}>
      <!-- Title -->
      <div class="form-section">
        <label class="form-label">Manifesto Title / Campaign Slogan</label>
        <input 
          type="text" 
          class="form-input large" 
          placeholder="e.g., A Vision for a Better Tomorrow"
          bind:value={manifestoTitle}
        />
      </div>
      
      <!-- Executive Summary -->
      <div class="form-section">
        <label class="form-label">Executive Summary / Vision</label>
        <textarea 
          class="form-textarea"
          placeholder="Outline your core vision statement here..."
          rows="6"
          bind:value={executiveSummary}
        ></textarea>
      </div>
      
      <!-- PDF Upload -->
      <div class="form-section">
        <label class="form-label">Full Manifesto Document (PDF)</label>
        <div class="upload-zone">
          <Upload size={24} />
          <p><span class="upload-link">Click to upload</span> or drag and drop</p>
          <span class="upload-hint">PDF (MAX. 10MB)</span>
        </div>
      </div>
      
      <!-- Campaign Promises -->
      <div class="form-section promises-section">
        <h2>Campaign Promises</h2>
        <p class="section-desc">Add specific, trackable commitments. These will be converted to smart contracts upon publishing.</p>
        
        <!-- Add Promise Form -->
        <div class="add-promise-form card">
          <div class="form-row">
            <div class="form-group flex-2">
              <label class="form-label small">PROMISE TITLE</label>
              <input 
                type="text" 
                class="form-input"
                placeholder="e.g., Reduce Carbon Emissions"
                bind:value={newPromiseTitle}
              />
            </div>
            <div class="form-group flex-1">
              <label class="form-label small">CATEGORY</label>
              <select class="form-select" bind:value={newPromiseCategory}>
                {#each categories as cat}
                  <option value={cat.value}>{cat.label}</option>
                {/each}
              </select>
            </div>
          </div>
          
          <div class="form-group">
            <label class="form-label small">DESCRIPTION & SUCCESS METRICS</label>
            <textarea 
              class="form-textarea small"
              placeholder="Describe the goal and how success will be measured..."
              rows="3"
              bind:value={newPromiseDescription}
            ></textarea>
          </div>
          
          <button type="button" class="add-promise-btn" on:click={addPromise}>
            <Plus size={16} />
            Add Promise to List
          </button>
        </div>
        
        <!-- Promise List -->
        <div class="promise-list">
          {#each promises as promise}
            <div class="promise-item">
              <div class="promise-icon" class:environment={promise.category === 'environment'} class:education={promise.category === 'education'}>
                {#if promise.category === 'environment'}
                  <Trees size={18} />
                {:else}
                  <Lightbulb size={18} />
                {/if}
              </div>
              <div class="promise-content">
                <div class="promise-header">
                  <h4>{promise.title}</h4>
                  <span class="category-badge {promise.category}">{promise.category.toUpperCase()}</span>
                </div>
                <p>{promise.description}</p>
              </div>
              <button type="button" class="remove-btn" on:click={() => removePromise(promise.id)}>
                <Trash2 size={18} />
              </button>
            </div>
          {/each}
        </div>
      </div>
      
      <!-- Warning Notice -->
      <div class="warning-notice">
        <Info size={20} />
        <div>
          <strong>Immutable Action</strong>
          <p>Once published, this manifesto is hashed to the ledger. Future changes require transparent amendments. Deletion is not possible.</p>
        </div>
      </div>
      
      <!-- Digital Signature Section -->
      <div class="signing-section">
        <h2><Key size={20} /> Digital Signature</h2>
        <p class="section-desc">Your manifesto must be cryptographically signed to prove authorship.</p>
        
        {#if !walletStatus?.has_wallet}
          <div class="signing-step warning">
            <AlertTriangle size={24} />
            <div>
              <strong>No Wallet Found</strong>
              <p>You need to generate a cryptographic wallet before you can sign manifestos.</p>
              <a href="/politician/wallet" class="btn btn-primary btn-sm">
                <Key size={16} />
                Generate Wallet
              </a>
            </div>
          </div>
        {:else if signingStep === 'upload-keystore'}
          <div class="signing-step">
            <div class="step-header">
              <span class="step-number">1</span>
              <strong>Upload Your Keystore File</strong>
            </div>
            <p>Load the encrypted keystore file you downloaded when creating your wallet.</p>
            <div class="wallet-info">
              <span class="label">Expected Address:</span>
              <code>{formatAddress(walletStatus.wallet_address || '')}</code>
            </div>
            <label class="keystore-upload">
              <input type="file" accept=".json" on:change={handleKeystoreUpload} />
              <Upload size={20} />
              <span>{keystoreFile ? keystoreFile.name : 'Click to upload keystore.json'}</span>
            </label>
          </div>
        {:else if signingStep === 'enter-passphrase'}
          <div class="signing-step">
            <div class="step-header">
              <span class="step-number">2</span>
              <strong>Enter Your Passphrase</strong>
            </div>
            <p>Enter the passphrase you used when creating your wallet to unlock signing.</p>
            <div class="passphrase-input">
              <Lock size={18} />
              <input 
                type="password" 
                placeholder="Enter your passphrase"
                bind:value={passphrase}
              />
            </div>
            <div class="keystore-loaded">
              <CheckCircle size={16} />
              <span>Keystore loaded: {keystoreFile?.name}</span>
              <button type="button" class="change-btn" on:click={() => { keystoreFile = null; keystoreData = null; signingStep = 'upload-keystore'; }}>
                Change
              </button>
            </div>
          </div>
        {:else if signingStep === 'signing'}
          <div class="signing-step signing">
            <Loader size={24} class="spinner" />
            <div>
              <strong>Signing Manifesto...</strong>
              <p>Please wait while your manifesto is being signed.</p>
            </div>
          </div>
        {:else if signingStep === 'complete'}
          <div class="signing-step success">
            <CheckCircle size={24} />
            <div>
              <strong>Manifesto Signed & Submitted!</strong>
              <p>Your manifesto has been cryptographically signed and recorded.</p>
              <div class="signature-details">
                <div class="detail">
                  <span class="label">Content Hash:</span>
                  <code>0x{manifestoHash.slice(0, 16)}...</code>
                </div>
                <div class="detail">
                  <span class="label">Signature:</span>
                  <code>{signature.slice(0, 20)}...</code>
                </div>
              </div>
              <a href="/politician/dashboard" class="btn btn-primary btn-sm">
                View in Dashboard
              </a>
            </div>
          </div>
        {/if}
        
        {#if submitError}
          <div class="error-message">
            <AlertTriangle size={16} />
            {submitError}
          </div>
        {/if}
      </div>
      
      <!-- Footer Actions -->
      <div class="form-footer">
        <div class="hash-preview">
          <span class="preview-label">MERKLE ROOT PREVIEW</span>
          <HashDisplay hash={previewHash} />
        </div>
        
        <div class="action-buttons">
          <button type="button" class="btn btn-secondary btn-lg">Save Draft</button>
          <button 
            type="submit" 
            class="btn btn-success btn-lg"
            disabled={isSubmitting || !walletStatus?.has_wallet || !passphrase || submitSuccess}
          >
            {#if isSubmitting}
              <Loader size={18} class="spinner" />
              Signing...
            {:else}
              <Upload size={18} />
              Sign & Publish
            {/if}
          </button>
        </div>
      </div>
    </form>
  </div>
</main>

<Footer />

<style>
  .draft-page {
    min-height: 100vh;
    background: var(--gray-50);
    padding-bottom: var(--space-8);
  }
  
  .container {
    max-width: 800px;
    margin: 0 auto;
    padding: var(--space-6) var(--space-4);
  }
  
  .breadcrumb {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    font-size: 0.875rem;
    margin-bottom: var(--space-4);
  }
  
  .breadcrumb a {
    color: var(--gray-500);
    text-decoration: none;
  }
  
  .breadcrumb span {
    color: var(--gray-400);
  }
  
  .breadcrumb .current {
    color: var(--gray-700);
  }
  
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: var(--space-8);
    flex-wrap: wrap;
    gap: var(--space-4);
  }
  
  .header-content h1 {
    font-size: 1.75rem;
    margin-bottom: var(--space-2);
  }
  
  .header-content p {
    color: var(--gray-500);
    max-width: 500px;
  }
  
  .secure-badge {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-2) var(--space-3);
    background: var(--success-50);
    color: var(--success-700);
    border-radius: var(--radius-full);
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.02em;
  }
  
  .status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
  }
  
  .status-dot.online {
    background: var(--success-500);
  }
  
  /* Form */
  .manifesto-form {
    display: flex;
    flex-direction: column;
    gap: var(--space-6);
  }
  
  .form-section {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
  }
  
  .form-label {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--gray-700);
  }
  
  .form-label.small {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--gray-500);
  }
  
  .form-input {
    padding: var(--space-3);
    border: 1px solid var(--gray-300);
    border-radius: var(--radius-lg);
    font-size: 0.9rem;
    transition: all 0.2s;
  }
  
  .form-input.large {
    padding: var(--space-4);
    font-size: 1rem;
  }
  
  .form-input:focus {
    outline: none;
    border-color: var(--primary-500);
    box-shadow: 0 0 0 3px var(--primary-100);
  }
  
  .form-textarea {
    padding: var(--space-4);
    border: 1px solid var(--gray-300);
    border-radius: var(--radius-lg);
    font-size: 0.9rem;
    resize: vertical;
    font-family: inherit;
  }
  
  .form-textarea.small {
    padding: var(--space-3);
    font-size: 0.85rem;
  }
  
  .form-textarea:focus {
    outline: none;
    border-color: var(--primary-500);
    box-shadow: 0 0 0 3px var(--primary-100);
  }
  
  .form-select {
    padding: var(--space-3);
    border: 1px solid var(--gray-300);
    border-radius: var(--radius-lg);
    font-size: 0.9rem;
    background: white;
    cursor: pointer;
  }
  
  .upload-zone {
    border: 2px dashed var(--gray-300);
    border-radius: var(--radius-xl);
    padding: var(--space-8);
    text-align: center;
    background: var(--gray-50);
    cursor: pointer;
    transition: all 0.2s;
  }
  
  .upload-zone:hover {
    border-color: var(--primary-400);
    background: var(--primary-50);
  }
  
  .upload-zone :global(svg) {
    color: var(--gray-400);
    margin-bottom: var(--space-2);
  }
  
  .upload-zone p {
    color: var(--gray-600);
    font-size: 0.875rem;
    margin-bottom: var(--space-1);
  }
  
  .upload-link {
    color: var(--primary-600);
    font-weight: 500;
  }
  
  .upload-hint {
    font-size: 0.75rem;
    color: var(--gray-400);
  }
  
  /* Promises Section */
  .promises-section h2 {
    font-size: 1.25rem;
    margin-bottom: var(--space-1);
  }
  
  .section-desc {
    font-size: 0.875rem;
    color: var(--gray-500);
    margin-bottom: var(--space-4);
  }
  
  .add-promise-form {
    padding: var(--space-5);
    margin-bottom: var(--space-4);
  }
  
  .form-row {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: var(--space-4);
    margin-bottom: var(--space-4);
  }
  
  .form-group {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
  }
  
  .add-promise-btn {
    display: inline-flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-2) var(--space-4);
    border: 2px solid var(--primary-500);
    background: transparent;
    color: var(--primary-600);
    border-radius: var(--radius-lg);
    font-weight: 600;
    font-size: 0.875rem;
    cursor: pointer;
    transition: all 0.2s;
  }
  
  .add-promise-btn:hover {
    background: var(--primary-50);
  }
  
  .promise-list {
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
  }
  
  .promise-item {
    display: flex;
    align-items: flex-start;
    gap: var(--space-4);
    padding: var(--space-4);
    background: white;
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-lg);
  }
  
  .promise-icon {
    width: 40px;
    height: 40px;
    border-radius: var(--radius-lg);
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--gray-100);
    color: var(--gray-500);
    flex-shrink: 0;
  }
  
  .promise-icon.environment {
    background: var(--success-100);
    color: var(--success-600);
  }
  
  .promise-icon.education {
    background: var(--primary-100);
    color: var(--primary-600);
  }
  
  .promise-content {
    flex: 1;
  }
  
  .promise-header {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    margin-bottom: var(--space-1);
  }
  
  .promise-header h4 {
    font-size: 0.95rem;
  }
  
  .category-badge {
    padding: 2px 6px;
    font-size: 0.6rem;
    font-weight: 600;
    border-radius: var(--radius-sm);
  }
  
  .category-badge.environment {
    background: var(--success-100);
    color: var(--success-700);
  }
  
  .category-badge.education {
    background: var(--primary-100);
    color: var(--primary-700);
  }
  
  .promise-content p {
    font-size: 0.85rem;
    color: var(--gray-600);
    line-height: 1.5;
  }
  
  .remove-btn {
    width: 36px;
    height: 36px;
    border: none;
    background: transparent;
    color: var(--gray-400);
    cursor: pointer;
    border-radius: var(--radius-md);
  }
  
  .remove-btn:hover {
    background: var(--error-50);
    color: var(--error-500);
  }
  
  /* Warning */
  .warning-notice {
    display: flex;
    gap: var(--space-3);
    padding: var(--space-4);
    background: var(--warning-50);
    border-radius: var(--radius-lg);
    border-left: 4px solid var(--warning-500);
  }
  
  .warning-notice :global(svg) {
    color: var(--warning-600);
    flex-shrink: 0;
  }
  
  .warning-notice strong {
    display: block;
    color: var(--warning-800);
    margin-bottom: var(--space-1);
  }
  
  .warning-notice p {
    font-size: 0.85rem;
    color: var(--gray-600);
    margin: 0;
  }
  
  /* Footer */
  .form-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-6) 0;
    border-top: 1px solid var(--gray-200);
    flex-wrap: wrap;
    gap: var(--space-4);
  }
  
  .hash-preview {
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
  }
  
  .preview-label {
    font-size: 0.65rem;
    font-weight: 600;
    color: var(--gray-400);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  
  .action-buttons {
    display: flex;
    gap: var(--space-3);
  }
  
  /* Signing Section */
  .signing-section {
    background: white;
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-xl);
    padding: var(--space-6);
  }
  
  .signing-section h2 {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    font-size: 1.25rem;
    margin-bottom: var(--space-2);
  }
  
  .signing-section .section-desc {
    margin-bottom: var(--space-4);
  }
  
  .signing-step {
    display: flex;
    gap: var(--space-4);
    padding: var(--space-4);
    background: var(--gray-50);
    border-radius: var(--radius-lg);
    align-items: flex-start;
  }
  
  .signing-step.warning {
    background: var(--warning-50);
    border: 1px solid var(--warning-200);
  }
  
  .signing-step.warning :global(svg) {
    color: var(--warning-600);
    flex-shrink: 0;
  }
  
  .signing-step.success {
    background: var(--success-50);
    border: 1px solid var(--success-200);
  }
  
  .signing-step.success :global(svg) {
    color: var(--success-600);
    flex-shrink: 0;
  }
  
  .signing-step.signing {
    align-items: center;
  }
  
  .signing-step strong {
    display: block;
    margin-bottom: var(--space-1);
  }
  
  .signing-step p {
    font-size: 0.875rem;
    color: var(--gray-600);
    margin-bottom: var(--space-3);
  }
  
  .step-header {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    margin-bottom: var(--space-2);
  }
  
  .step-number {
    width: 24px;
    height: 24px;
    background: var(--primary-500);
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    font-weight: 600;
  }
  
  .wallet-info {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    margin-bottom: var(--space-3);
    font-size: 0.85rem;
  }
  
  .wallet-info .label {
    color: var(--gray-500);
  }
  
  .wallet-info code {
    background: var(--gray-100);
    padding: 2px 8px;
    border-radius: var(--radius-sm);
    font-family: var(--font-mono);
  }
  
  .keystore-upload {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-4);
    background: white;
    border: 2px dashed var(--gray-300);
    border-radius: var(--radius-lg);
    cursor: pointer;
    transition: all 0.2s;
  }
  
  .keystore-upload:hover {
    border-color: var(--primary-400);
    background: var(--primary-50);
  }
  
  .keystore-upload input {
    display: none;
  }
  
  .keystore-upload :global(svg) {
    color: var(--gray-400);
  }
  
  .keystore-upload span {
    color: var(--gray-600);
  }
  
  .passphrase-input {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-3) var(--space-4);
    background: white;
    border: 1px solid var(--gray-300);
    border-radius: var(--radius-lg);
    margin-bottom: var(--space-3);
  }
  
  .passphrase-input :global(svg) {
    color: var(--gray-400);
  }
  
  .passphrase-input input {
    flex: 1;
    border: none;
    font-size: 0.9rem;
    outline: none;
  }
  
  .keystore-loaded {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    font-size: 0.85rem;
    color: var(--success-600);
  }
  
  .keystore-loaded :global(svg) {
    color: var(--success-500);
  }
  
  .change-btn {
    margin-left: auto;
    padding: var(--space-1) var(--space-2);
    background: transparent;
    border: 1px solid var(--gray-300);
    border-radius: var(--radius-sm);
    font-size: 0.75rem;
    cursor: pointer;
    color: var(--gray-600);
  }
  
  .change-btn:hover {
    background: var(--gray-100);
  }
  
  .signature-details {
    background: white;
    padding: var(--space-3);
    border-radius: var(--radius-md);
    margin: var(--space-3) 0;
  }
  
  .signature-details .detail {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    font-size: 0.8rem;
    margin-bottom: var(--space-2);
  }
  
  .signature-details .detail:last-child {
    margin-bottom: 0;
  }
  
  .signature-details .label {
    color: var(--gray-500);
  }
  
  .signature-details code {
    font-family: var(--font-mono);
    font-size: 0.75rem;
  }
  
  .error-message {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    margin-top: var(--space-3);
    padding: var(--space-3);
    background: var(--error-50);
    border: 1px solid var(--error-200);
    border-radius: var(--radius-md);
    color: var(--error-700);
    font-size: 0.875rem;
  }
  
  .error-message :global(svg) {
    flex-shrink: 0;
  }
  
  .spinner {
    animation: spin 1s linear infinite;
  }
  
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
  
  .btn-sm {
    padding: var(--space-2) var(--space-3);
    font-size: 0.875rem;
  }
</style>
