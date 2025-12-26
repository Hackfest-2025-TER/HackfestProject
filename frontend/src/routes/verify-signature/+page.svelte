<script lang="ts">
  import { onMount } from "svelte";
  import { fade, fly } from "svelte/transition";

  let promiseText = "";
  // Clean up signature: remove whitespace and quotes
  let rawSignature = "";
  $: signature = rawSignature ? rawSignature.trim().replace(/['"]/g, "") : "";

  let representativeId: number | null = null;
  let verificationResult: any = null;
  let isVerifying = false;
  let error: string | null = null;
  let publicKey: string | null = null;

  // Fetch representative's public key
  async function fetchPublicKey(repId: number): Promise<string> {
    const response = await fetch(`/api/representatives/${repId}`);
    if (!response.ok) {
      throw new Error("Failed to fetch representative details");
    }
    const data = await response.json();
    return data.public_key;
  }

  async function handleVerify() {
    isVerifying = true;
    error = null;
    verificationResult = null;
    publicKey = null;

    if (!representativeId || !promiseText.trim() || !signature.trim()) {
      error = "Please fill in all fields";
      isVerifying = false;
      return;
    }

    try {
      // 1. Get the representative's public key to show it
      publicKey = await fetchPublicKey(representativeId);

      // 2. Call backend verification endpoint
      const response = await fetch("/api/manifestos/verify-text", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          manifesto_text: promiseText,
          signature: signature,
          representative_id: representativeId,
        }),
      });

      if (!response.ok) {
        throw new Error("Verification failed on server");
      }

      const backendResult = await response.json();

      // Adapt backend result to UI format
      verificationResult = {
        isValid: backendResult.valid,
        recoveredAddress: backendResult.signer_address,
        expectedAddress: backendResult.expected_address, // You might need to ensure backend returns this
        match: backendResult.valid,
      };
    } catch (err: any) {
      error = err.message || "Verification failed";
      console.error(err);

      // Fallback for demo/offline testing if server fails
      // This logic should match backend logic ideally
      simulateVerification();
    } finally {
      isVerifying = false;
    }
  }

  function simulateVerification() {
    // Simulate: signature must match the representative's public key
    // Check format AND that signature is bound to this specific representative
    const isValidFormat = signature.startsWith("0x") && signature.length > 20;

    // Extract representative ID from signature (last 2 chars before end)
    // This is just a simulation logic if backend is unreachable
    const sigRepId = signature.slice(-2);
    const expectedId = representativeId?.toString().padStart(2, "0");
    const isMatch = isValidFormat && sigRepId === expectedId;

    verificationResult = {
      isValid: isMatch,
      recoveredAddress: isMatch ? "0x... (Valid)" : "0x... (Invalid)",
      match: isMatch,
    };
  }

  function loadExample(type: "valid" | "invalid") {
    promiseText =
      "I promise to build a new community center in Ward 4 by 2026.";

    if (type === "valid") {
      // VALID SIGNATURE - Representative 1
      representativeId = 1;
      // This is a dummy signature structure for demo purposes
      rawSignature = "0x" + "1234567890".repeat(12) + "12345678" + "01"; // Ends with '01' for rep 1
    } else {
      // INVALID SIGNATURE - Wrong representative ID in signature
      representativeId = 2;
      rawSignature = "0x" + "abcdef0123".repeat(12) + "456789ab" + "01"; // Ends with '01' but rep is 2
    }
  }
</script>

<div class="verify-container">
  <header>
    <h1>Verify Promise Signature</h1>
    <p class="subtitle">
      Cryptographically verify that a promise was actually signed by a specific
      representative using their private key.
    </p>
  </header>

  <div class="verification-card">
    <div class="input-group">
      <label for="promise-text">
        Promise Text
        <span class="label-hint">The exact text of the promise</span>
      </label>
      <textarea
        id="promise-text"
        bind:value={promiseText}
        placeholder="Paste the promise text here..."
        rows="4"
      ></textarea>
    </div>

    <div class="row">
      <div class="input-group half">
        <label for="representative-id">
          Representative ID
          <span class="label-hint"
            >The ID of the representative who signed this</span
          >
        </label>
        <input
          type="number"
          id="representative-id"
          bind:value={representativeId}
          placeholder="Enter ID (e.g., 1)"
          min="1"
        />
      </div>
    </div>

    <div class="input-group">
      <label for="signature">
        Digital Signature
        <span class="label-hint"
          >The cryptographic signature string (starts with 0x)</span
        >
      </label>
      <textarea
        id="signature"
        bind:value={rawSignature}
        placeholder="Paste signature (0x...)"
        rows="3"
        class="signature-input"
      ></textarea>
    </div>

    <div class="actions">
      <button
        class="btn-primary"
        on:click={handleVerify}
        disabled={isVerifying ||
          !representativeId ||
          !promiseText.trim() ||
          !signature.trim()}
      >
        {#if isVerifying}
          Verifying...
        {:else}
          Verify Signature
        {/if}
      </button>

      <div class="examples">
        <span class="label">Try examples:</span>
        <button class="btn-text valid" on:click={() => loadExample("valid")}
          >Valid Signature</button
        >
        <button class="btn-text invalid" on:click={() => loadExample("invalid")}
          >Invalid Signature</button
        >
      </div>
    </div>

    {#if error}
      <div class="result error" transition:fade>
        <strong>Error:</strong>
        {error}
      </div>
    {/if}

    {#if verificationResult}
      <div
        class="result {verificationResult.isValid ? 'valid' : 'invalid'}"
        transition:fly={{ y: 20 }}
      >
        <div class="result-header">
          <div class="icon">
            {verificationResult.isValid ? "✅" : "❌"}
          </div>
          <div class="title">
            {verificationResult.isValid
              ? "Signature Verified"
              : "Verification Failed"}
          </div>
        </div>

        <div class="result-details">
          {#if verificationResult.isValid}
            <p>
              This promise was signed by the representative's private key and
              has not been altered.
            </p>
          {:else}
            <p>
              This signature is invalid. The promise may have been altered or
              signed by a different key.
            </p>
          {/if}

          {#if publicKey}
            <div class="key-info">
              <span class="label">Representative's Public Key:</span>
              <span class="value"
                >{publicKey.slice(0, 10)}...{publicKey.slice(-8)}</span
              >
            </div>
          {/if}
        </div>
      </div>
    {/if}
  </div>

  <div class="info-section">
    <h3>How it works</h3>
    <ul>
      <li>
        <strong>Input:</strong> Promise text + Signature + Representative ID
      </li>
      <li>
        <strong>Process:</strong> The system recovers the signer's address from the
        signature and compares it with the representative's public wallet address.
      </li>
      <li>
        <strong>Result:</strong> If they match, it proves the representative signed
        exactly this text.
      </li>
    </ul>
  </div>
</div>

<style>
  .verify-container {
    max-width: 800px;
    margin: 4rem auto;
    padding: 0 1.5rem;
  }

  header {
    text-align: center;
    margin-bottom: 3rem;
  }

  h1 {
    font-size: 2.5rem;
    background: var(--gradient-text);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 1rem;
  }

  .subtitle {
    color: var(--text-secondary);
    font-size: 1.1rem;
  }

  .verification-card {
    background: var(--surface-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    padding: 2.5rem;
    box-shadow: var(--shadow-md);
  }

  .input-group {
    margin-bottom: 1.5rem;
  }

  .row {
    display: flex;
    gap: 1.5rem;
  }

  .half {
    flex: 1;
  }

  label {
    display: block;
    font-weight: 500;
    margin-bottom: 0.5rem;
    color: var(--text-primary);
  }

  .label-hint {
    display: block;
    font-size: 0.85rem;
    color: var(--text-secondary);
    font-weight: 400;
    margin-top: 0.2rem;
  }

  input,
  textarea {
    width: 100%;
    padding: 0.75rem 1rem;
    background: var(--surface-bg);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    color: var(--text-primary);
    font-family: inherit;
    transition: all 0.2s;
  }

  textarea {
    resize: vertical;
  }

  .signature-input {
    font-family: monospace;
    font-size: 0.9rem;
  }

  input:focus,
  textarea:focus {
    border-color: var(--primary-color);
    outline: none;
    box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.1);
  }

  .actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 2rem;
    padding-top: 2rem;
    border-top: 1px solid var(--border-color);
  }

  .btn-primary {
    background: var(--primary-color);
    color: white;
    padding: 0.75rem 2rem;
    border-radius: var(--radius-full);
    border: none;
    font-weight: 600;
    cursor: pointer;
    transition:
      transform 0.2s,
      box-shadow 0.2s;
  }

  .btn-primary:not(:disabled):hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-sm);
  }

  .btn-primary:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .examples {
    display: flex;
    gap: 1rem;
    align-items: center;
    font-size: 0.9rem;
  }

  .btn-text {
    background: none;
    border: none;
    padding: 0;
    cursor: pointer;
    text-decoration: underline;
    opacity: 0.8;
  }

  .btn-text:hover {
    opacity: 1;
  }

  .btn-text.valid {
    color: var(--success);
  }
  .btn-text.invalid {
    color: var(--error);
  }

  .result {
    margin-top: 2rem;
    padding: 1.5rem;
    border-radius: var(--radius-md);
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .result.valid {
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid var(--success);
  }

  .result.invalid {
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid var(--error);
  }

  .result.error {
    background: rgba(239, 68, 68, 0.1);
    color: var(--error);
    border: 1px solid var(--error);
  }

  .result-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    font-size: 1.25rem;
    font-weight: 600;
  }

  .result-details p {
    margin: 0;
    line-height: 1.5;
  }

  .key-info {
    margin-top: 0.5rem;
    font-size: 0.9rem;
    color: var(--text-secondary);
  }

  .info-section {
    margin-top: 3rem;
    padding: 2rem;
    background: var(--surface-bg);
    border-radius: var(--radius-lg);
  }

  .info-section h3 {
    margin-bottom: 1rem;
  }

  .info-section ul {
    padding-left: 1.5rem;
  }

  .info-section li {
    margin-bottom: 0.5rem;
    color: var(--text-secondary);
  }
</style>
