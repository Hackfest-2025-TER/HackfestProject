<script lang="ts">
  import Header from '$lib/components/Header.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import { Shield, Key, Download, AlertTriangle, Check, Copy, RefreshCw, FileKey } from 'lucide-svelte';
  import { onMount } from 'svelte';
  import { generatePoliticianWallet, getPoliticianWalletStatus } from '$lib/api';
  import { downloadKeystore, formatAddress } from '$lib/utils/crypto';
  
  // This would come from auth/session in production
  let politicianId = 1;
  let politicianName = 'Politician';
  
  // State
  let walletStatus: any = null;
  let isLoading = true;
  let error = '';
  
  // Key generation form
  let passphrase = '';
  let passphraseConfirm = '';
  let isGenerating = false;
  let generatedKeystore: any = null;
  let keystoreDownloaded = false;
  let savedConfirmed = false;
  
  // Passphrase strength
  $: passphraseStrength = getPassphraseStrength(passphrase);
  $: passphrasesMatch = passphrase === passphraseConfirm && passphrase.length > 0;
  $: canGenerate = passphraseStrength >= 2 && passphrasesMatch && !walletStatus?.has_wallet;
  
  function getPassphraseStrength(pass: string): number {
    let strength = 0;
    if (pass.length >= 8) strength++;
    if (pass.length >= 12) strength++;
    if (/[A-Z]/.test(pass)) strength++;
    if (/[0-9]/.test(pass)) strength++;
    if (/[^A-Za-z0-9]/.test(pass)) strength++;
    return Math.min(strength, 4);
  }
  
  function getStrengthLabel(strength: number): string {
    if (strength === 0) return 'Too weak';
    if (strength === 1) return 'Weak';
    if (strength === 2) return 'Fair';
    if (strength === 3) return 'Good';
    return 'Strong';
  }
  
  function getStrengthColor(strength: number): string {
    if (strength === 0) return '#ef4444';
    if (strength === 1) return '#f97316';
    if (strength === 2) return '#eab308';
    if (strength === 3) return '#22c55e';
    return '#10b981';
  }
  
  onMount(async () => {
    await loadWalletStatus();
  });
  
  async function loadWalletStatus() {
    try {
      isLoading = true;
      walletStatus = await getPoliticianWalletStatus(politicianId);
    } catch (e: any) {
      error = e.message;
    } finally {
      isLoading = false;
    }
  }
  
  async function generateWallet() {
    if (!canGenerate) return;
    
    try {
      isGenerating = true;
      error = '';
      
      const result = await generatePoliticianWallet(politicianId, passphrase);
      generatedKeystore = result;
      
      // Refresh wallet status
      await loadWalletStatus();
    } catch (e: any) {
      error = e.message;
    } finally {
      isGenerating = false;
    }
  }
  
  function handleDownloadKeystore() {
    if (!generatedKeystore?.keystore) return;
    
    downloadKeystore(
      generatedKeystore.keystore,
      generatedKeystore.keystore_filename || `politician-${politicianId}-key.json`
    );
    keystoreDownloaded = true;
  }
  
  function copyAddress() {
    if (walletStatus?.wallet_address) {
      navigator.clipboard.writeText(walletStatus.wallet_address);
    }
  }
  
  function resetForm() {
    generatedKeystore = null;
    keystoreDownloaded = false;
    savedConfirmed = false;
    passphrase = '';
    passphraseConfirm = '';
  }
</script>

<svelte:head>
  <title>Wallet Management - Politician Portal</title>
</svelte:head>

<Header variant="politician" />

<main class="wallet-page">
  <div class="container">
    <div class="page-header">
      <div class="header-icon">
        <Key size={32} />
      </div>
      <div>
        <h1>Digital Identity & Signing Keys</h1>
        <p>Manage your cryptographic identity for signing manifestos</p>
      </div>
    </div>
    
    {#if isLoading}
      <div class="loading-state">
        <div class="spinner"></div>
        <p>Loading wallet status...</p>
      </div>
    {:else if error && !generatedKeystore}
      <div class="error-banner">
        <AlertTriangle size={20} />
        <span>{error}</span>
      </div>
    {:else}
      <!-- Current Wallet Status -->
      {#if walletStatus?.has_wallet}
        <div class="status-card success">
          <div class="status-icon">
            <Shield size={24} />
          </div>
          <div class="status-content">
            <h3>Wallet Active</h3>
            <p>Your cryptographic identity is set up. You can sign manifestos.</p>
            
            <div class="wallet-details">
              <div class="detail-row">
                <span class="label">Wallet Address:</span>
                <span class="value">
                  <code>{walletStatus.wallet_address}</code>
                  <button class="copy-btn" on:click={copyAddress}>
                    <Copy size={14} />
                  </button>
                </span>
              </div>
              <div class="detail-row">
                <span class="label">Key Version:</span>
                <span class="value">{walletStatus.key_version}</span>
              </div>
              <div class="detail-row">
                <span class="label">Created:</span>
                <span class="value">{new Date(walletStatus.wallet_created_at).toLocaleDateString()}</span>
              </div>
              {#if walletStatus.previous_keys_count > 0}
                <div class="detail-row warning">
                  <span class="label">Previous Keys:</span>
                  <span class="value">{walletStatus.previous_keys_count} (revoked)</span>
                </div>
              {/if}
            </div>
            
            <div class="action-buttons">
              <a href="/politician/new-manifesto" class="btn btn-primary">
                <FileKey size={16} />
                Sign New Manifesto
              </a>
            </div>
          </div>
        </div>
        
        <!-- Key Recovery Info -->
        <div class="info-card">
          <h4>🔐 Lost Your Keystore File?</h4>
          <p>
            If you've lost your keystore file or forgotten your passphrase, 
            you'll need to contact the platform administrator for key rotation.
            Old manifestos will remain tied to the old key (historical integrity).
          </p>
          <a href="/politician/request-key-rotation" class="link">Request Key Rotation →</a>
        </div>
        
      {:else}
        <!-- No Wallet - Show Generation Form -->
        <div class="generation-section">
          {#if generatedKeystore}
            <!-- Key Generated - Show Download -->
            <div class="generated-card">
              <div class="success-icon">
                <Check size={32} />
              </div>
              <h2>🎉 Wallet Generated Successfully!</h2>
              <p class="warning-text">
                <AlertTriangle size={16} />
                <strong>CRITICAL:</strong> Download and save your keystore file now. 
                We do NOT store your private key and cannot recover it.
              </p>
              
              <div class="wallet-info">
                <div class="info-row">
                  <span>Wallet Address:</span>
                  <code>{generatedKeystore.wallet_address}</code>
                </div>
              </div>
              
              <div class="download-section">
                <button 
                  class="btn btn-primary large" 
                  on:click={handleDownloadKeystore}
                  disabled={keystoreDownloaded}
                >
                  <Download size={20} />
                  {keystoreDownloaded ? 'Downloaded ✓' : 'Download Keystore File'}
                </button>
                
                {#if keystoreDownloaded}
                  <div class="confirm-save">
                    <label>
                      <input type="checkbox" bind:checked={savedConfirmed} />
                      I have saved my keystore file in a secure location
                    </label>
                  </div>
                {/if}
              </div>
              
              <div class="instructions">
                <h4>📋 Important Instructions:</h4>
                <ol>
                  {#each generatedKeystore.instructions as instruction}
                    <li>{instruction}</li>
                  {/each}
                </ol>
              </div>
              
              {#if keystoreDownloaded && savedConfirmed}
                <div class="next-steps">
                  <a href="/politician/new-manifesto" class="btn btn-success">
                    Continue to Sign Your First Manifesto →
                  </a>
                </div>
              {/if}
            </div>
          {:else}
            <!-- Generation Form -->
            <div class="form-card">
              <div class="form-header">
                <Key size={24} />
                <h2>Generate Your Signing Key</h2>
              </div>
              
              <p class="form-desc">
                Create a cryptographic key pair for signing your manifestos.
                Your private key will be encrypted with a passphrase you choose.
              </p>
              
              <div class="form-group">
                <label>
                  Passphrase
                  <span class="hint">Used to encrypt your keystore file</span>
                </label>
                <input 
                  type="password" 
                  bind:value={passphrase}
                  placeholder="Choose a strong passphrase..."
                />
                
                <div class="strength-meter">
                  <div class="strength-bar">
                    {#each [0, 1, 2, 3] as i}
                      <div 
                        class="strength-segment" 
                        style="background-color: {i < passphraseStrength ? getStrengthColor(passphraseStrength) : '#374151'}"
                      ></div>
                    {/each}
                  </div>
                  <span style="color: {getStrengthColor(passphraseStrength)}">
                    {getStrengthLabel(passphraseStrength)}
                  </span>
                </div>
              </div>
              
              <div class="form-group">
                <label>Confirm Passphrase</label>
                <input 
                  type="password" 
                  bind:value={passphraseConfirm}
                  placeholder="Re-enter your passphrase..."
                />
                {#if passphraseConfirm && !passphrasesMatch}
                  <span class="error-text">Passphrases do not match</span>
                {/if}
              </div>
              
              <div class="security-tips">
                <h4>🔒 Security Tips:</h4>
                <ul>
                  <li>Use a unique passphrase (not used elsewhere)</li>
                  <li>Store the keystore file and passphrase separately</li>
                  <li>Consider using a password manager</li>
                  <li>Make multiple backups of your keystore file</li>
                </ul>
              </div>
              
              {#if error}
                <div class="error-message">
                  <AlertTriangle size={16} />
                  {error}
                </div>
              {/if}
              
              <button 
                class="btn btn-primary large" 
                on:click={generateWallet}
                disabled={!canGenerate || isGenerating}
              >
                {#if isGenerating}
                  <span class="spinner-small"></span>
                  Generating...
                {:else}
                  <Key size={20} />
                  Generate Key Pair
                {/if}
              </button>
            </div>
          {/if}
        </div>
      {/if}
      
      <!-- How It Works -->
      <div class="how-it-works">
        <h3>How Digital Signatures Work</h3>
        <div class="steps-grid">
          <div class="step">
            <div class="step-number">1</div>
            <h4>Generate Key Pair</h4>
            <p>Create a public/private key pair. Public key is stored, private key is given to you.</p>
          </div>
          <div class="step">
            <div class="step-number">2</div>
            <h4>Sign Manifestos</h4>
            <p>When you create a manifesto, sign it with your private key to prove authorship.</p>
          </div>
          <div class="step">
            <div class="step-number">3</div>
            <h4>Anyone Can Verify</h4>
            <p>Citizens can verify your signature using your public key. No trust needed.</p>
          </div>
        </div>
      </div>
    {/if}
  </div>
</main>

<Footer />

<style>
  .wallet-page {
    min-height: 100vh;
    background: linear-gradient(to bottom, #0f172a, #1e293b);
    padding: 2rem 0;
  }
  
  .container {
    max-width: 800px;
    margin: 0 auto;
    padding: 0 1rem;
  }
  
  .page-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 2rem;
    padding: 1.5rem;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.1);
  }
  
  .header-icon {
    width: 60px;
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #3b82f6, #8b5cf6);
    border-radius: 12px;
    color: white;
  }
  
  .page-header h1 {
    font-size: 1.5rem;
    color: white;
    margin: 0 0 0.25rem 0;
  }
  
  .page-header p {
    color: #94a3b8;
    margin: 0;
  }
  
  .loading-state {
    text-align: center;
    padding: 3rem;
    color: #94a3b8;
  }
  
  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid rgba(255, 255, 255, 0.1);
    border-top-color: #3b82f6;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 1rem;
  }
  
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
  
  .error-banner {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 1rem;
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.3);
    border-radius: 8px;
    color: #ef4444;
    margin-bottom: 1rem;
  }
  
  .status-card {
    display: flex;
    gap: 1.5rem;
    padding: 1.5rem;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    margin-bottom: 1.5rem;
  }
  
  .status-card.success {
    border-color: rgba(34, 197, 94, 0.3);
    background: rgba(34, 197, 94, 0.05);
  }
  
  .status-icon {
    width: 48px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(34, 197, 94, 0.2);
    border-radius: 12px;
    color: #22c55e;
    flex-shrink: 0;
  }
  
  .status-content h3 {
    color: #22c55e;
    margin: 0 0 0.5rem 0;
  }
  
  .status-content p {
    color: #94a3b8;
    margin: 0 0 1rem 0;
  }
  
  .wallet-details {
    background: rgba(0, 0, 0, 0.2);
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 1rem;
  }
  
  .detail-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  }
  
  .detail-row:last-child {
    border-bottom: none;
  }
  
  .detail-row .label {
    color: #64748b;
    font-size: 0.875rem;
  }
  
  .detail-row .value {
    color: white;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  
  .detail-row .value code {
    font-family: monospace;
    font-size: 0.875rem;
  }
  
  .copy-btn {
    background: none;
    border: none;
    color: #64748b;
    cursor: pointer;
    padding: 0.25rem;
    display: flex;
    align-items: center;
  }
  
  .copy-btn:hover {
    color: white;
  }
  
  .action-buttons {
    display: flex;
    gap: 1rem;
  }
  
  .info-card {
    padding: 1.5rem;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.1);
  }
  
  .info-card h4 {
    color: white;
    margin: 0 0 0.5rem 0;
  }
  
  .info-card p {
    color: #94a3b8;
    margin: 0 0 1rem 0;
    line-height: 1.6;
  }
  
  .info-card .link {
    color: #3b82f6;
    text-decoration: none;
  }
  
  .info-card .link:hover {
    text-decoration: underline;
  }
  
  .form-card, .generated-card {
    padding: 2rem;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    margin-bottom: 1.5rem;
  }
  
  .form-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.5rem;
    color: white;
  }
  
  .form-header h2 {
    margin: 0;
    font-size: 1.25rem;
  }
  
  .form-desc {
    color: #94a3b8;
    margin: 0 0 1.5rem 0;
  }
  
  .form-group {
    margin-bottom: 1.5rem;
  }
  
  .form-group label {
    display: block;
    color: white;
    margin-bottom: 0.5rem;
    font-weight: 500;
  }
  
  .form-group .hint {
    color: #64748b;
    font-weight: normal;
    font-size: 0.875rem;
    margin-left: 0.5rem;
  }
  
  .form-group input {
    width: 100%;
    padding: 0.75rem 1rem;
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    color: white;
    font-size: 1rem;
  }
  
  .form-group input:focus {
    outline: none;
    border-color: #3b82f6;
  }
  
  .strength-meter {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-top: 0.5rem;
  }
  
  .strength-bar {
    display: flex;
    gap: 4px;
    flex: 1;
  }
  
  .strength-segment {
    height: 4px;
    flex: 1;
    border-radius: 2px;
    transition: background-color 0.3s;
  }
  
  .error-text {
    color: #ef4444;
    font-size: 0.875rem;
    margin-top: 0.25rem;
    display: block;
  }
  
  .security-tips {
    padding: 1rem;
    background: rgba(59, 130, 246, 0.1);
    border: 1px solid rgba(59, 130, 246, 0.3);
    border-radius: 8px;
    margin-bottom: 1.5rem;
  }
  
  .security-tips h4 {
    color: #3b82f6;
    margin: 0 0 0.5rem 0;
    font-size: 0.875rem;
  }
  
  .security-tips ul {
    margin: 0;
    padding-left: 1.25rem;
    color: #94a3b8;
  }
  
  .security-tips li {
    margin-bottom: 0.25rem;
  }
  
  .error-message {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #ef4444;
    padding: 0.75rem;
    background: rgba(239, 68, 68, 0.1);
    border-radius: 8px;
    margin-bottom: 1rem;
  }
  
  .btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
    text-decoration: none;
    transition: all 0.2s;
  }
  
  .btn.large {
    width: 100%;
    padding: 1rem;
    font-size: 1rem;
  }
  
  .btn-primary {
    background: linear-gradient(135deg, #3b82f6, #2563eb);
    color: white;
  }
  
  .btn-primary:hover:not(:disabled) {
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
  }
  
  .btn-primary:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  .btn-success {
    background: linear-gradient(135deg, #22c55e, #16a34a);
    color: white;
  }
  
  .spinner-small {
    width: 16px;
    height: 16px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-top-color: white;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }
  
  .generated-card {
    text-align: center;
  }
  
  .success-icon {
    width: 64px;
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(34, 197, 94, 0.2);
    border-radius: 50%;
    color: #22c55e;
    margin: 0 auto 1rem;
  }
  
  .generated-card h2 {
    color: white;
    margin: 0 0 1rem 0;
  }
  
  .warning-text {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    color: #f97316;
    background: rgba(249, 115, 22, 0.1);
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 1.5rem;
  }
  
  .wallet-info {
    background: rgba(0, 0, 0, 0.2);
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 1.5rem;
  }
  
  .wallet-info .info-row {
    display: flex;
    justify-content: center;
    gap: 0.5rem;
    color: #94a3b8;
  }
  
  .wallet-info code {
    color: #22c55e;
    font-family: monospace;
  }
  
  .download-section {
    margin-bottom: 1.5rem;
  }
  
  .confirm-save {
    margin-top: 1rem;
  }
  
  .confirm-save label {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    color: #94a3b8;
    cursor: pointer;
  }
  
  .confirm-save input[type="checkbox"] {
    width: 18px;
    height: 18px;
  }
  
  .instructions {
    text-align: left;
    background: rgba(0, 0, 0, 0.2);
    padding: 1.5rem;
    border-radius: 8px;
    margin-bottom: 1.5rem;
  }
  
  .instructions h4 {
    color: white;
    margin: 0 0 0.75rem 0;
  }
  
  .instructions ol {
    margin: 0;
    padding-left: 1.25rem;
    color: #94a3b8;
  }
  
  .instructions li {
    margin-bottom: 0.5rem;
    line-height: 1.5;
  }
  
  .next-steps {
    padding-top: 1rem;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
  }
  
  .how-it-works {
    padding: 2rem;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.1);
  }
  
  .how-it-works h3 {
    color: white;
    text-align: center;
    margin: 0 0 1.5rem 0;
  }
  
  .steps-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.5rem;
  }
  
  .step {
    text-align: center;
    padding: 1rem;
  }
  
  .step-number {
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #3b82f6, #8b5cf6);
    border-radius: 50%;
    color: white;
    font-weight: bold;
    margin: 0 auto 0.75rem;
  }
  
  .step h4 {
    color: white;
    margin: 0 0 0.5rem 0;
  }
  
  .step p {
    color: #64748b;
    font-size: 0.875rem;
    margin: 0;
  }
  
  @media (max-width: 768px) {
    .steps-grid {
      grid-template-columns: 1fr;
    }
    
    .status-card {
      flex-direction: column;
    }
  }
</style>
