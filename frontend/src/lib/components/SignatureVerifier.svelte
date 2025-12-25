<script lang="ts">
  import { Shield, CheckCircle, XCircle, AlertTriangle, Clock, Loader, ExternalLink } from 'lucide-svelte';
  import { onMount } from 'svelte';
  import { verifyManifesto } from '$lib/api';
  import { formatAddress } from '$lib/utils/crypto';
  
  export let manifestoId: number;
  export let compact = false;
  
  interface VerificationResult {
    verified: boolean;
    is_legacy: boolean;
    politician_name?: string;
    signer_address?: string;
    signature_preview?: string;
    signed_at?: string;
    blockchain_confirmed?: boolean;
    blockchain_tx?: string;
    message?: string;
    verification_bundle?: {
      manifesto_hash: string;
      signature: string;
      signer_address: string;
      how_to_verify: string[];
    };
  }
  
  let verificationResult: VerificationResult | null = null;
  let isLoading = true;
  let error = '';
  let showDetails = false;
  
  onMount(async () => {
    await checkVerification();
  });
  
  async function checkVerification() {
    isLoading = true;
    error = '';
    
    try {
      verificationResult = await verifyManifesto(manifestoId);
    } catch (e: any) {
      error = e.message || 'Failed to verify signature';
    } finally {
      isLoading = false;
    }
  }
</script>

{#if compact}
  <!-- Compact badge for list views -->
  <div class="signature-badge" class:verified={verificationResult?.verified} class:legacy={verificationResult?.is_legacy} class:loading={isLoading}>
    {#if isLoading}
      <Loader size={14} class="spinner" />
      <span>Verifying...</span>
    {:else if error}
      <AlertTriangle size={14} />
      <span>Error</span>
    {:else if verificationResult?.verified}
      <CheckCircle size={14} />
      <span>Verified</span>
    {:else if verificationResult?.is_legacy}
      <Clock size={14} />
      <span>Legacy</span>
    {:else}
      <XCircle size={14} />
      <span>Unverified</span>
    {/if}
  </div>
{:else}
  <!-- Full verification panel -->
  <div class="verification-panel" class:verified={verificationResult?.verified} class:legacy={verificationResult?.is_legacy}>
    <div class="panel-header">
      <Shield size={20} />
      <h3>Digital Signature Verification</h3>
    </div>
    
    <div class="panel-content">
      {#if isLoading}
        <div class="status-row loading">
          <Loader size={24} class="spinner" />
          <div>
            <strong>Verifying Signature...</strong>
            <p>Checking cryptographic proof of authorship</p>
          </div>
        </div>
      {:else if error}
        <div class="status-row error">
          <AlertTriangle size={24} />
          <div>
            <strong>Verification Error</strong>
            <p>{error}</p>
          </div>
        </div>
      {:else if verificationResult?.verified}
        <div class="status-row verified">
          <CheckCircle size={24} />
          <div>
            <strong>Signature Verified ✓</strong>
            <p>This manifesto was cryptographically signed by the politician.</p>
          </div>
        </div>
        
        <div class="details-grid">
          <div class="detail-item">
            <span class="label">Signed By</span>
            <span class="value">{verificationResult.politician_name || 'Unknown'}</span>
          </div>
          <div class="detail-item">
            <span class="label">Wallet Address</span>
            <code>{formatAddress(verificationResult.signer_address || '')}</code>
          </div>
          <div class="detail-item">
            <span class="label">Signed At</span>
            <span class="value">{verificationResult.signed_at ? new Date(verificationResult.signed_at).toLocaleString() : 'Unknown'}</span>
          </div>
          {#if verificationResult.blockchain_confirmed}
            <div class="detail-item blockchain">
              <span class="label">Blockchain</span>
              <span class="value confirmed">
                <CheckCircle size={12} />
                Confirmed
              </span>
            </div>
          {/if}
        </div>
        
        <button class="show-details-btn" on:click={() => showDetails = !showDetails}>
          {showDetails ? 'Hide' : 'Show'} Technical Details
        </button>
        
        {#if showDetails && verificationResult.verification_bundle}
          <div class="technical-details">
            <h4>Verification Bundle</h4>
            <div class="code-block">
              <div class="code-row">
                <span class="key">Manifesto Hash:</span>
                <code>{verificationResult.verification_bundle.manifesto_hash}</code>
              </div>
              <div class="code-row">
                <span class="key">Signature:</span>
                <code>{verificationResult.verification_bundle.signature.slice(0, 40)}...</code>
              </div>
              <div class="code-row">
                <span class="key">Signer Address:</span>
                <code>{verificationResult.verification_bundle.signer_address}</code>
              </div>
            </div>
            <div class="how-to-verify">
              <h5>How to Independently Verify:</h5>
              <ol>
                {#each verificationResult.verification_bundle.how_to_verify as step}
                  <li>{step}</li>
                {/each}
              </ol>
            </div>
          </div>
        {/if}
      {:else if verificationResult?.is_legacy}
        <div class="status-row legacy">
          <Clock size={24} />
          <div>
            <strong>Legacy Manifesto</strong>
            <p>This manifesto was created before digital signatures were implemented. It cannot be cryptographically verified.</p>
          </div>
        </div>
        <div class="legacy-notice">
          <p>Legacy manifestos are retained for historical transparency but should be treated as unverified claims.</p>
        </div>
      {:else}
        <div class="status-row unverified">
          <XCircle size={24} />
          <div>
            <strong>Signature Not Verified</strong>
            <p>{verificationResult?.message || 'Could not verify the authenticity of this manifesto.'}</p>
          </div>
        </div>
      {/if}
    </div>
  </div>
{/if}

<style>
  .signature-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 8px;
    border-radius: var(--radius-full);
    font-size: 0.75rem;
    font-weight: 600;
  }
  
  .signature-badge.verified {
    background: var(--success-100);
    color: var(--success-700);
  }
  
  .signature-badge.legacy {
    background: var(--warning-100);
    color: var(--warning-700);
  }
  
  .signature-badge.loading {
    background: var(--gray-100);
    color: var(--gray-600);
  }
  
  .signature-badge :global(.spinner) {
    animation: spin 1s linear infinite;
  }
  
  .verification-panel {
    background: white;
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-xl);
    overflow: hidden;
  }
  
  .panel-header {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-4);
    background: var(--gray-50);
    border-bottom: 1px solid var(--gray-200);
  }
  
  .panel-header h3 {
    font-size: 1rem;
    margin: 0;
  }
  
  .panel-content {
    padding: var(--space-4);
  }
  
  .status-row {
    display: flex;
    gap: var(--space-3);
    padding: var(--space-4);
    border-radius: var(--radius-lg);
    margin-bottom: var(--space-4);
  }
  
  .status-row.verified {
    background: var(--success-50);
  }
  
  .status-row.verified :global(svg) {
    color: var(--success-600);
    flex-shrink: 0;
  }
  
  .status-row.legacy {
    background: var(--warning-50);
  }
  
  .status-row.legacy :global(svg) {
    color: var(--warning-600);
    flex-shrink: 0;
  }
  
  .status-row.error,
  .status-row.unverified {
    background: var(--error-50);
  }
  
  .status-row.error :global(svg),
  .status-row.unverified :global(svg) {
    color: var(--error-600);
    flex-shrink: 0;
  }
  
  .status-row.loading {
    background: var(--gray-50);
    align-items: center;
  }
  
  .status-row strong {
    display: block;
    margin-bottom: var(--space-1);
  }
  
  .status-row p {
    font-size: 0.875rem;
    color: var(--gray-600);
    margin: 0;
  }
  
  .details-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-3);
    margin-bottom: var(--space-4);
  }
  
  .detail-item {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  
  .detail-item .label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--gray-500);
  }
  
  .detail-item .value {
    font-size: 0.875rem;
    color: var(--gray-900);
  }
  
  .detail-item code {
    font-family: var(--font-mono);
    font-size: 0.8rem;
    background: var(--gray-100);
    padding: 2px 6px;
    border-radius: var(--radius-sm);
  }
  
  .detail-item.blockchain .value.confirmed {
    display: flex;
    align-items: center;
    gap: 4px;
    color: var(--success-600);
  }
  
  .show-details-btn {
    width: 100%;
    padding: var(--space-2);
    background: transparent;
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-md);
    font-size: 0.8rem;
    cursor: pointer;
    color: var(--gray-600);
  }
  
  .show-details-btn:hover {
    background: var(--gray-50);
  }
  
  .technical-details {
    margin-top: var(--space-4);
    padding: var(--space-4);
    background: var(--gray-50);
    border-radius: var(--radius-lg);
  }
  
  .technical-details h4 {
    font-size: 0.875rem;
    margin-bottom: var(--space-3);
  }
  
  .code-block {
    background: var(--gray-900);
    border-radius: var(--radius-md);
    padding: var(--space-3);
    margin-bottom: var(--space-3);
  }
  
  .code-row {
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-2);
    margin-bottom: var(--space-2);
    font-size: 0.75rem;
  }
  
  .code-row:last-child {
    margin-bottom: 0;
  }
  
  .code-row .key {
    color: var(--gray-400);
  }
  
  .code-row code {
    color: var(--success-400);
    font-family: var(--font-mono);
    word-break: break-all;
  }
  
  .how-to-verify h5 {
    font-size: 0.8rem;
    margin-bottom: var(--space-2);
  }
  
  .how-to-verify ol {
    font-size: 0.8rem;
    color: var(--gray-600);
    padding-left: var(--space-4);
    margin: 0;
  }
  
  .how-to-verify li {
    margin-bottom: var(--space-1);
  }
  
  .legacy-notice {
    padding: var(--space-3);
    background: var(--gray-50);
    border-radius: var(--radius-md);
    font-size: 0.8rem;
    color: var(--gray-600);
  }
  
  .legacy-notice p {
    margin: 0;
  }
  
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
  
  @media (max-width: 600px) {
    .details-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
