<script lang="ts">
  import Header from "$lib/components/Header.svelte";
  import Footer from "$lib/components/Footer.svelte";
  import {
    Shield,
    Key,
    Download,
    AlertTriangle,
    Check,
    Copy,
    RefreshCw,
    FileKey,
  } from "lucide-svelte";
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";
  import { credential } from "$lib/stores";
  import { get } from "svelte/store";
  import {
    generateRepresentativeWallet,
    getRepresentativeWalletStatus,
  } from "$lib/api";
  import { downloadKeystore, formatAddress } from "$lib/utils/crypto";

  // Get from auth
  let representativeId: number | null = null;
  let representativeName = "";

  // State
  let walletStatus: any = null;
  let isLoading = true;
  let error = "";

  // Key generation form
  let passphrase = "";
  let passphraseConfirm = "";
  let isGenerating = false;
  let generatedKeystore: any = null;
  let keystoreDownloaded = false;
  let savedConfirmed = false;

  // Passphrase strength
  $: passphraseStrength = getPassphraseStrength(passphrase);
  $: passphrasesMatch =
    passphrase === passphraseConfirm && passphrase.length > 0;
  $: canGenerate =
    passphraseStrength >= 2 && passphrasesMatch && !walletStatus?.has_wallet;

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
    if (strength === 0) return "Too weak";
    if (strength === 1) return "Weak";
    if (strength === 2) return "Fair";
    if (strength === 3) return "Good";
    return "Strong";
  }

  function getStrengthColor(strength: number): string {
    if (strength === 0) return "#ef4444";
    if (strength === 1) return "#f97316";
    if (strength === 2) return "#eab308";
    if (strength === 3) return "#22c55e";
    return "#10b981";
  }

  onMount(async () => {
    const cred = get(credential);
    if (!cred || !cred.isRepresentative || !cred.representativeId) {
      error = "You must be a registered representative to access wallet features";
      setTimeout(() => goto("/representative/register"), 2000);
      return;
    }
    representativeId = cred.representativeId;
    // Fetch representative name from backend or use from cred if available
    await loadWalletStatus();
  });

  async function loadWalletStatus() {
    if (!representativeId) return;
    try {
      isLoading = true;
      walletStatus = await getRepresentativeWalletStatus(representativeId);
    } catch (e: any) {
      error = e.message;
    } finally {
      isLoading = false;
    }
  }

  async function generateWallet() {
    if (!canGenerate || !representativeId) return;

    try {
      isGenerating = true;
      error = "";

      const result = await generateRepresentativeWallet(representativeId, passphrase);
      generatedKeystore = result;

      // Auto-download keystore immediately
      if (generatedKeystore?.keystore) {
        downloadKeystore(
          generatedKeystore.keystore,
          generatedKeystore.keystore_filename ||
            `representative-${representativeId}-key.json`,
        );
        keystoreDownloaded = true;
      }

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
      generatedKeystore.keystore_filename ||
        `representative-${representativeId}-key.json`,
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
    passphrase = "";
    passphraseConfirm = "";
  }
</script>

<svelte:head>
  <title>Wallet Management - Representative Portal</title>
</svelte:head>

<main class="wallet-page">
  <div class="container">
    <!-- Breadcrumb -->
    <div class="flex items-center gap-2 text-sm text-gray-500 mb-6">
      <a
        href="/representative/dashboard"
        class="hover:text-primary-600 transition-colors">Dashboard</a
      >
      <span>/</span>
      <span class="text-gray-900 font-medium">Wallet & Keys</span>
    </div>

    <div class="page-header">
      <div class="header-icon">
        <Key size={32} />
      </div>
      <div>
        <h1>Digital Identity & Signing Keys</h1>
        <p>Manage your cryptographic identity for signing promises</p>
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
            <p>Your cryptographic identity is set up. You can sign promises.</p>

            <div class="wallet-details">
              <div class="detail-row">
                <span class="label">Wallet Address:</span>
                <span class="value">
                  <code>{walletStatus.wallet_address}</code>
                  <button
                    class="copy-btn"
                    on:click={copyAddress}
                    title="Copy Address"
                  >
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
                <span class="value"
                  >{new Date(
                    walletStatus.wallet_created_at,
                  ).toLocaleDateString()}</span
                >
              </div>
              {#if walletStatus.previous_keys_count > 0}
                <div class="detail-row warning">
                  <span class="label">Previous Keys:</span>
                  <span class="value text-warning-600"
                    >{walletStatus.previous_keys_count} (revoked)</span
                  >
                </div>
              {/if}
            </div>

            <div class="wallet-notice">
              <p class="text-sm text-gray-600 mb-4 flex items-start gap-2">
                <AlertTriangle
                  size={16}
                  class="inline text-warning-500 mt-0.5 flex-shrink-0"
                />
                <span>
                  <strong>Important:</strong> Your keystore file was provided during
                  wallet creation. If you've lost it, you'll need key rotation enabled
                  by an administrator.
                </span>
              </p>
            </div>

            <div class="action-buttons">
              <a href="/representative/new-manifesto" class="btn btn-primary">
                <FileKey size={16} />
                Sign New Promise
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
            Old promises will remain tied to the old key to maintain historical
            integrity.
          </p>
          <a href="/representative/request-key-rotation" class="link"
            >Request Key Rotation →</a
          >
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
              <div class="warning-text">
                <AlertTriangle size={18} />
                <div>
                  <strong>CRITICAL:</strong> Download and save your keystore file
                  now. We do NOT store your private key and cannot recover it.
                </div>
              </div>

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
                  {keystoreDownloaded
                    ? "Downloaded ✓"
                    : "Download Keystore File"}
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
                  <a href="/representative/new-manifesto" class="btn btn-success">
                    Continue to Sign Your First Promise →
                  </a>
                </div>
              {/if}
            </div>
          {:else}
            <!-- Generation Form -->
            <div class="form-card">
              <div class="form-header">
                <div class="p-3 bg-primary-100 rounded-lg text-primary-600">
                  <Key size={24} />
                </div>
                <h2>Generate Your Signing Key</h2>
              </div>

              <p class="form-desc">
                Create a cryptographic key pair for signing your promises. Your
                private key will be encrypted with a passphrase you choose.
              </p>

              <div class="form-group">
                <label for="passphrase">
                  Passphrase
                  <span class="hint">Used to encrypt your keystore file</span>
                </label>
                <input
                  id="passphrase"
                  type="password"
                  bind:value={passphrase}
                  placeholder="Choose a strong passphrase..."
                />

                <div class="strength-meter">
                  <div class="strength-bar">
                    {#each [0, 1, 2, 3] as i}
                      <div
                        class="strength-segment"
                        style="background-color: {i < passphraseStrength
                          ? getStrengthColor(passphraseStrength)
                          : '#e5e7eb'}"
                      ></div>
                    {/each}
                  </div>
                  <span style="color: {getStrengthColor(passphraseStrength)}">
                    {getStrengthLabel(passphraseStrength)}
                  </span>
                </div>
              </div>

              <div class="form-group">
                <label for="passphraseConfirm">Confirm Passphrase</label>
                <input
                  id="passphraseConfirm"
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
            <p>
              Create a public/private key pair. Public key is stored, private
              key is given to you.
            </p>
          </div>
          <div class="step">
            <div class="step-number">2</div>
            <h4>Sign Promises</h4>
            <p>
              When you create a promise, sign it with your private key to prove
              authorship.
            </p>
          </div>
          <div class="step">
            <div class="step-number">3</div>
            <h4>Anyone Can Verify</h4>
            <p>
              Citizens can verify your signature using your public key. No trust
              needed.
            </p>
          </div>
        </div>
      </div>
    {/if}
  </div>
</main>

<style>
  .wallet-page {
    min-height: 100vh;
    background: var(--gray-50);
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
    gap: 1.5rem;
    margin-bottom: 2rem;
    padding: 2rem;
    background: white;
    border-radius: var(--radius-xl);
    border: 1px solid var(--gray-200);
    box-shadow: var(--shadow-sm);
  }

  .header-icon {
    width: 64px;
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--primary-100);
    border-radius: var(--radius-xl);
    color: var(--primary-600);
    flex-shrink: 0;
  }

  .page-header h1 {
    font-size: 1.5rem;
    color: var(--gray-900);
    margin: 0 0 0.5rem 0;
    font-weight: 700;
  }

  .page-header p {
    color: var(--gray-600);
    margin: 0;
    font-size: 1.05rem;
  }

  .loading-state {
    text-align: center;
    padding: 4rem;
    color: var(--gray-500);
  }

  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid var(--gray-200);
    border-top-color: var(--primary-600);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 1.5rem;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  .error-banner {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem;
    background: var(--error-50);
    border: 1px solid var(--error-200);
    border-radius: var(--radius-lg);
    color: var(--error-700);
    margin-bottom: 1.5rem;
  }

  .status-card {
    display: flex;
    gap: 1.5rem;
    padding: 2rem;
    background: white;
    border-radius: var(--radius-xl);
    border: 1px solid var(--gray-200);
    margin-bottom: 2rem;
    box-shadow: var(--shadow-sm);
  }

  .status-card.success {
    border-left: 5px solid var(--success-500);
  }

  .status-icon {
    width: 48px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--success-50);
    border-radius: var(--radius-lg);
    color: var(--success-600);
    flex-shrink: 0;
  }

  .status-content {
    flex: 1;
  }

  .status-content h3 {
    color: var(--gray-900);
    font-weight: 700;
    font-size: 1.25rem;
    margin: 0 0 0.5rem 0;
  }

  .status-content p {
    color: var(--gray-600);
    margin: 0 0 1.5rem 0;
  }

  .wallet-details {
    background: var(--gray-50);
    padding: 1.5rem;
    border-radius: var(--radius-lg);
    margin-bottom: 1.5rem;
    border: 1px solid var(--gray-200);
  }

  .detail-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 0;
    border-bottom: 1px solid var(--gray-200);
  }

  .detail-row:last-child {
    border-bottom: none;
  }

  .detail-row .label {
    color: var(--gray-500);
    font-size: 0.875rem;
    font-weight: 600;
  }

  .detail-row .value {
    color: var(--gray-900);
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-weight: 500;
  }

  .detail-row .value code {
    font-family: var(--font-mono);
    font-size: 0.875rem;
    background: white;
    padding: 2px 6px;
    border-radius: 4px;
    border: 1px solid var(--gray-200);
    color: var(--primary-700);
  }

  .copy-btn {
    background: white;
    border: 1px solid var(--gray-200);
    color: var(--gray-500);
    cursor: pointer;
    padding: 4px;
    border-radius: 4px;
    display: flex;
    align-items: center;
    transition: all 0.2s;
  }

  .copy-btn:hover {
    color: var(--primary-600);
    border-color: var(--primary-300);
    background: var(--primary-50);
  }

  .action-buttons {
    display: flex;
    gap: 1rem;
    margin-top: 1.5rem;
  }

  .info-card {
    padding: 2rem;
    background: white;
    border-radius: var(--radius-xl);
    border: 1px solid var(--gray-200);
  }

  .info-card h4 {
    color: var(--gray-900);
    font-weight: 700;
    margin: 0 0 0.75rem 0;
    font-size: 1.1rem;
  }

  .info-card p {
    color: var(--gray-600);
    margin: 0 0 1rem 0;
    line-height: 1.6;
  }

  .info-card .link {
    color: var(--primary-600);
    text-decoration: none;
    font-weight: 600;
  }

  .info-card .link:hover {
    text-decoration: underline;
    color: var(--primary-700);
  }

  .form-card,
  .generated-card {
    padding: 2.5rem;
    background: white;
    border-radius: var(--radius-xl);
    border: 1px solid var(--gray-200);
    margin-bottom: 2rem;
    box-shadow: var(--shadow-sm);
  }

  .form-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1rem;
    color: var(--gray-900);
  }

  .form-header h2 {
    margin: 0;
    font-size: 1.5rem;
    font-weight: 700;
  }

  .form-desc {
    color: var(--gray-600);
    margin: 0 0 2rem 0;
    line-height: 1.6;
    max-width: 600px;
  }

  .form-group {
    margin-bottom: 1.5rem;
  }

  .form-group label {
    display: block;
    color: var(--gray-700);
    margin-bottom: 0.5rem;
    font-weight: 600;
    font-size: 0.9rem;
  }

  .form-group .hint {
    color: var(--gray-500);
    font-weight: normal;
    font-size: 0.85rem;
    margin-left: 0.5rem;
  }

  .form-group input {
    width: 100%;
    padding: 0.875rem 1rem;
    background: white;
    border: 1px solid var(--gray-300);
    border-radius: var(--radius-lg);
    color: var(--gray-900);
    font-size: 1rem;
    transition: all 0.2s;
  }

  .form-group input:focus {
    outline: none;
    border-color: var(--primary-500);
    box-shadow: 0 0 0 3px var(--primary-100);
  }

  .strength-meter {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-top: 0.75rem;
  }

  .strength-bar {
    display: flex;
    gap: 4px;
    flex: 1;
    height: 6px;
  }

  .strength-segment {
    flex: 1;
    border-radius: 3px;
    transition: background-color 0.3s;
  }

  .error-text {
    color: var(--error-600);
    font-size: 0.875rem;
    margin-top: 0.5rem;
    display: block;
    font-weight: 500;
  }

  .security-tips {
    padding: 1.5rem;
    background: var(--primary-50);
    border: 1px solid var(--primary-100);
    border-radius: var(--radius-lg);
    margin-bottom: 2rem;
  }

  .security-tips h4 {
    color: var(--primary-800);
    margin: 0 0 0.75rem 0;
    font-size: 0.95rem;
    font-weight: 700;
  }

  .security-tips ul {
    margin: 0;
    padding-left: 1.25rem;
    color: var(--primary-700);
  }

  .security-tips li {
    margin-bottom: 0.4rem;
    font-size: 0.9rem;
  }

  .error-message {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    color: var(--error-700);
    padding: 1rem;
    background: var(--error-50);
    border-radius: var(--radius-lg);
    margin-bottom: 1.5rem;
    border: 1px solid var(--error-200);
    font-weight: 500;
  }

  .btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: var(--radius-lg);
    font-size: 1rem;
    font-weight: 600;
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
    background: var(--primary-600);
    color: white;
  }

  .btn-primary:hover:not(:disabled) {
    background: var(--primary-700);
    transform: translateY(-1px);
    box-shadow: var(--shadow-md);
  }

  .btn-primary:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    background: var(--gray-400);
  }

  .btn-success {
    background: var(--success-600);
    color: white;
  }

  .btn-success:hover {
    background: var(--success-700);
    transform: translateY(-1px);
    box-shadow: var(--shadow-md);
  }

  .spinner-small {
    width: 20px;
    height: 20px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-top-color: white;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  .generated-card {
    text-align: center;
  }

  .success-icon {
    width: 80px;
    height: 80px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--success-50);
    border-radius: 50%;
    color: var(--success-600);
    margin: 0 auto 1.5rem;
    border: 1px solid var(--success-100);
  }

  .generated-card h2 {
    color: var(--gray-900);
    margin: 0 0 1.5rem 0;
    font-weight: 700;
  }

  .warning-text {
    display: flex;
    align-items: flex-start;
    justify-content: center;
    gap: 0.75rem;
    color: var(--warning-800);
    background: var(--warning-50);
    padding: 1.5rem;
    border-radius: var(--radius-lg);
    margin-bottom: 2rem;
    border: 1px solid var(--warning-200);
    text-align: left;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
  }

  .warning-text :global(svg) {
    flex-shrink: 0;
    color: var(--warning-600);
    margin-top: 2px;
  }

  .wallet-info {
    background: var(--gray-50);
    padding: 1.5rem;
    border-radius: var(--radius-lg);
    margin-bottom: 2rem;
    border: 1px solid var(--gray-200);
  }

  .wallet-info .info-row {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 0.75rem;
    flex-wrap: wrap;
    color: var(--gray-600);
  }

  .wallet-info code {
    color: var(--primary-700);
    font-family: var(--font-mono);
    background: white;
    padding: 4px 8px;
    border-radius: 4px;
    border: 1px solid var(--gray-200);
    font-size: 0.9rem;
    word-break: break-all;
  }

  .download-section {
    margin-bottom: 2rem;
  }

  .confirm-save {
    margin-top: 1.5rem;
  }

  .confirm-save label {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.75rem;
    color: var(--gray-700);
    cursor: pointer;
    font-weight: 500;
  }

  .confirm-save input[type="checkbox"] {
    width: 20px;
    height: 20px;
    border-radius: 4px;
    border: 1px solid var(--gray-300);
  }

  .instructions {
    text-align: left;
    background: white;
    padding: 2rem;
    border-radius: var(--radius-lg);
    margin-bottom: 2rem;
    border: 1px solid var(--gray-200);
  }

  .instructions h4 {
    color: var(--gray-900);
    margin: 0 0 1rem 0;
    font-weight: 700;
  }

  .instructions ol {
    margin: 0;
    padding-left: 1.5rem;
    color: var(--gray-600);
  }

  .instructions li {
    margin-bottom: 0.75rem;
    line-height: 1.6;
  }

  .next-steps {
    padding-top: 2rem;
    border-top: 1px solid var(--gray-200);
  }

  .how-it-works {
    padding: 2.5rem;
    background: white;
    border-radius: var(--radius-xl);
    border: 1px solid var(--gray-200);
  }

  .how-it-works h3 {
    color: var(--gray-900);
    text-align: center;
    margin: 0 0 2rem 0;
    font-size: 1.25rem;
    font-weight: 700;
  }

  .steps-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 2rem;
  }

  .step {
    text-align: center;
    padding: 1.5rem;
    background: var(--gray-50);
    border-radius: var(--radius-lg);
    border: 1px solid var(--gray-100);
  }

  .step-number {
    width: 48px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--primary-100);
    border-radius: 50%;
    color: var(--primary-700);
    font-weight: 700;
    font-size: 1.2rem;
    margin: 0 auto 1rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  }

  .step h4 {
    color: var(--gray-900);
    margin: 0 0 0.5rem 0;
    font-weight: 600;
  }

  .step p {
    color: var(--gray-600);
    font-size: 0.9rem;
    margin: 0;
    line-height: 1.5;
  }

  @media (max-width: 768px) {
    .steps-grid {
      grid-template-columns: 1fr;
    }

    .status-card {
      flex-direction: column;
    }

    .page-header {
      flex-direction: column;
      text-align: center;
      padding: 1.5rem;
    }
  }
</style>
