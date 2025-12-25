<script lang="ts">
  import HashDisplay from "$lib/components/HashDisplay.svelte";
  import {
    Shield,
    Search,
    CheckCircle,
    XCircle,
    FileText,
    Link,
    Clock,
    AlertTriangle,
    Copy,
    ExternalLink,
    RefreshCw,
  } from "lucide-svelte";

  // State
  let manifestoId: number | null = null;
  let manifestoText = "";
  let isVerifying = false;
  let verificationResult: any = null;
  let localHash = "";
  let blockchainHash = "";
  let showAdvanced = false;

  // Step tracking for UX
  let currentStep = 0;

  /**
   * STEP 1: Local Fingerprint Computation
   * This happens entirely in your browser. We never see this data.
   */
  async function computeLocalHash(text: string): Promise<string> {
    const encoder = new TextEncoder();
    const data = encoder.encode(text);
    const hashBuffer = await crypto.subtle.digest("SHA-256", data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const hashHex = hashArray
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("");
    return "0x" + hashHex;
  }

  /**
   * STEP 2: Fetch Official Record
   */
  async function fetchBlockchainHash(manifestoId: number): Promise<any> {
    const response = await fetch(
      `http://localhost:8000/api/manifestos/${manifestoId}`,
    );
    if (!response.ok) {
      throw new Error("Failed to fetch official record");
    }
    const data = await response.json();
    return { hash: data.hash, manifesto: data };
  }

  /**
   * MAIN VERIFICATION FLOW
   */
  async function verifyManifesto() {
    if (!manifestoId || !manifestoText.trim()) {
      alert("Please enter manifesto ID and manifesto text");
      return;
    }

    isVerifying = true;
    verificationResult = null;
    currentStep = 1;

    try {
      // STEP 1: Compute local hash (trustless)
      localHash = await computeLocalHash(manifestoText);
      currentStep = 2;

      await new Promise((r) => setTimeout(r, 500));

      // STEP 2: Fetch blockchain hash
      const blockchainData = await fetchBlockchainHash(manifestoId);
      blockchainHash = blockchainData.hash;
      currentStep = 3;

      await new Promise((r) => setTimeout(r, 500));

      // STEP 3: Compare
      const isValid = localHash === blockchainHash;
      currentStep = 4;

      verificationResult = {
        valid: isValid,
        localHash,
        blockchainHash,
        blockchainData,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      console.error("Verification error:", error);
      verificationResult = {
        valid: false,
        error: true,
        message: error instanceof Error ? error.message : "Verification failed",
      };
    } finally {
      isVerifying = false;
    }
  }

  function copyHash(hash: string) {
    navigator.clipboard.writeText(hash);
  }

  function loadSample() {
    const scenarios = [
      {
        manifestoId: 1,
        manifestoText: `धुलिखेल-काभ्रे सडक विस्तार:धुलिखेलदेखि काभ्रेसम्मको सडकलाई चार लेन बनाउने। यो परियोजनाले यातायात सुधार गर्नेछ र आर्थिक विकासमा योगदान पुर्याउनेछ।:1`,
      },
      {
        manifestoId: 2,
        manifestoText: `प्रत्येक गाउँमा स्वास्थ्य चौकी:हरेक गाउँमा कम्तीमा एक अति स्वास्थ्य चौकी स्थापना गर्ने र आधारभूत स्वास्थ्य सेवा सुनिश्चित गर्ने।:2`,
      },
    ];

    const selected = scenarios[Math.floor(Math.random() * scenarios.length)];
    manifestoId = selected.manifestoId;
    manifestoText = selected.manifestoText;
  }
</script>

<svelte:head>
  <title>Verify Authenticity - PromiseThread</title>
</svelte:head>

<main class="min-h-screen bg-gray-50 py-12">
  <div class="container-custom max-w-4xl">
    <!-- Hero Section -->
    <div class="text-center mb-12">
      <div
        class="inline-flex items-center justify-center w-20 h-20 bg-primary-100 text-primary-600 rounded-2xl mb-6"
      >
        <Shield size={40} />
      </div>
      <h1 class="text-4xl font-bold font-serif text-gray-900 mb-4">
        Verify Authenticity
      </h1>
      <p class="text-xl text-gray-600 max-w-2xl mx-auto">
        Independently verify that a promise hasn't been changed.
        <strong class="text-primary-700"
          >This happens entirely on your device.</strong
        >
      </p>
    </div>

    <!-- How It Works -->
    <div class="bg-white border border-gray-200 rounded-2xl p-8 mb-8 shadow-sm">
      <h3 class="font-bold text-gray-900 mb-6 flex items-center gap-2">
        <Shield size={20} class="text-primary-600" />
        How Verification Works
      </h3>
      <div
        class="flex flex-col md:flex-row items-center justify-center gap-4 md:gap-8"
      >
        <div
          class="flex items-center gap-3 p-4 bg-gray-50 rounded-xl flex-1 w-full"
          class:ring-2={currentStep >= 1}
          class:ring-primary-500={currentStep >= 1}
        >
          <div
            class="w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold text-sm"
          >
            1
          </div>
          <div class="flex flex-col">
            <strong class="text-gray-900 text-sm">Generate Fingerprint</strong>
            <span class="text-xs text-gray-500"
              >Created from text on your device</span
            >
          </div>
        </div>

        <div class="hidden md:block text-gray-300">→</div>

        <div
          class="flex items-center gap-3 p-4 bg-gray-50 rounded-xl flex-1 w-full"
          class:ring-2={currentStep >= 2}
          class:ring-primary-500={currentStep >= 2}
        >
          <div
            class="w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold text-sm"
          >
            2
          </div>
          <div class="flex flex-col">
            <strong class="text-gray-900 text-sm">Fetch Official Record</strong>
            <span class="text-xs text-gray-500"
              >Get the original from public log</span
            >
          </div>
        </div>

        <div class="hidden md:block text-gray-300">→</div>

        <div
          class="flex items-center gap-3 p-4 bg-gray-50 rounded-xl flex-1 w-full"
          class:ring-2={currentStep >= 3}
          class:ring-primary-500={currentStep >= 3}
        >
          <div
            class="w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold text-sm"
          >
            3
          </div>
          <div class="flex flex-col">
            <strong class="text-gray-900 text-sm">Compare</strong>
            <span class="text-xs text-gray-500"
              >If they match, it's authentic</span
            >
          </div>
        </div>
      </div>
    </div>

    <!-- Main Verification Form -->
    <div
      class="bg-white border border-gray-200 rounded-2xl shadow-sm overflow-hidden mb-8"
    >
      <div
        class="px-6 py-4 bg-gray-50 border-b border-gray-200 flex items-center gap-3"
      >
        <FileText size={20} class="text-gray-500" />
        <h2 class="font-bold text-gray-900">Promise Details</h2>
      </div>

      <div class="p-6 md:p-8 space-y-6">
        <!-- Manifesto ID Input -->
        <div>
          <label
            for="manifesto-id"
            class="block font-medium text-gray-700 mb-1"
          >
            Promise ID
          </label>
          <input
            type="number"
            id="manifesto-id"
            bind:value={manifestoId}
            placeholder="e.g. 1"
            min="1"
            class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all outline-none"
          />
        </div>

        <!-- Manifesto Text Input -->
        <div>
          <label
            for="manifesto-text"
            class="block font-medium text-gray-700 mb-1"
          >
            Promise Text
            <span class="text-gray-500 font-normal text-sm ml-2"
              >Must match exactly (spaces, punctuation)</span
            >
          </label>
          <textarea
            id="manifesto-text"
            bind:value={manifestoText}
            placeholder="Paste the promise content here to verify..."
            rows="6"
            class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all outline-none resize-y font-sans"
          />
          <div class="text-right text-xs text-gray-500 mt-1">
            {manifestoText.length} chars
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex justify-end gap-3 pt-4 border-t border-gray-100">
          <button
            class="btn bg-gray-100 text-gray-700 hover:bg-gray-200"
            on:click={loadSample}
          >
            Load Sample
          </button>
          <button
            class="btn btn-primary min-w-[140px]"
            on:click={verifyManifesto}
            disabled={isVerifying || !manifestoId || !manifestoText.trim()}
          >
            {#if isVerifying}
              <RefreshCw size={18} class="animate-spin" />
              Checking...
            {:else}
              <Search size={18} />
              Verify Now
            {/if}
          </button>
        </div>
      </div>
    </div>

    <!-- Verification Result -->
    {#if verificationResult}
      <div
        class="bg-white border rounded-2xl shadow-sm overflow-hidden animate-fade-in"
        class:border-success-200={verificationResult.valid}
        class:ring-4={verificationResult.valid}
        class:ring-success-50={verificationResult.valid}
        class:border-error-200={!verificationResult.valid}
        class:ring-error-50={!verificationResult.valid &&
          !verificationResult.error}
      >
        {#if verificationResult.error}
          <div class="p-8 text-center">
            <div
              class="w-16 h-16 bg-warning-50 text-warning-600 rounded-full flex items-center justify-center mx-auto mb-4"
            >
              <AlertTriangle size={32} />
            </div>
            <h2 class="text-xl font-bold text-gray-900 mb-2">
              Error Verifying
            </h2>
            <p class="text-gray-600">{verificationResult.message}</p>
          </div>
        {:else if verificationResult.valid}
          <!-- AUTHENTIC -->
          <div
            class="p-8 bg-success-50/50 border-b border-success-100 flex items-center gap-6"
          >
            <div
              class="w-16 h-16 bg-success-100 text-success-600 rounded-full flex items-center justify-center flex-shrink-0"
            >
              <CheckCircle size={32} />
            </div>
            <div>
              <h2 class="text-2xl font-bold text-success-700 mb-1">
                Authentic Record
              </h2>
              <p class="text-success-800">
                The text you entered matches the official immutable record
                exactly.
              </p>
            </div>
          </div>
        {:else}
          <!-- TAMPERED -->
          <div
            class="p-8 bg-error-50/50 border-b border-error-100 flex items-center gap-6"
          >
            <div
              class="w-16 h-16 bg-error-100 text-error-600 rounded-full flex items-center justify-center flex-shrink-0"
            >
              <XCircle size={32} />
            </div>
            <div>
              <h2 class="text-2xl font-bold text-error-700 mb-1">
                Verification Failed
              </h2>
              <p class="text-error-800">
                The text does not match the official record. It may have been
                modified.
              </p>
            </div>
          </div>
        {/if}

        {#if !verificationResult.error}
          <!-- Comparison Details -->
          <div class="p-6 md:p-8 bg-white space-y-6">
            <div class="flex flex-col md:flex-row gap-6 items-stretch">
              <!-- Local -->
              <div
                class="flex-1 p-4 rounded-xl bg-gray-50 border border-gray-200"
              >
                <span
                  class="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2"
                  >My Device Fingerprint</span
                >
                <code
                  class="block text-xs font-mono text-gray-700 break-all mb-2"
                  >{verificationResult.localHash}</code
                >
              </div>

              <div
                class="flex items-center justify-center text-gray-400 font-bold text-2xl"
              >
                {verificationResult.valid ? "=" : "≠"}
              </div>

              <!-- Remote -->
              <div
                class="flex-1 p-4 rounded-xl bg-primary-50 border border-primary-100"
              >
                <span
                  class="block text-xs font-bold text-primary-600 uppercase tracking-wider mb-2"
                  >Official Record Fingerprint</span
                >
                <code
                  class="block text-xs font-mono text-primary-800 break-all mb-2"
                  >{verificationResult.blockchainHash}</code
                >
              </div>
            </div>

            <!-- Advanced Toggle -->
            <div class="border-t border-gray-100 pt-6">
              <button
                class="flex items-center gap-2 text-sm text-gray-500 hover:text-primary-600 transition-colors"
                on:click={() => (showAdvanced = !showAdvanced)}
              >
                {showAdvanced ? "Hide" : "Show"} Technical Details
              </button>

              {#if showAdvanced}
                <div class="mt-4 p-4 bg-slate-900 rounded-xl overflow-x-auto">
                  <pre class="text-xs text-slate-300 font-mono">
// Independent verification code
const text = "{manifestoText.substring(0, 30)}...";
const hash = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(text));
// Compare with contract: {verificationResult.blockchainData?.contract_address}
                  </pre>
                </div>
              {/if}
            </div>
          </div>
        {/if}
      </div>
    {/if}
  </div>
</main>
