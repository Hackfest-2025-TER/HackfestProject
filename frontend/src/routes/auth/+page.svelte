<script lang="ts">
  import { onMount } from "svelte";
  import {
    Shield,
    User,
    Lock,
    AlertCircle,
    Eye,
    EyeOff,
    Loader2,
    ArrowRight,
  } from "lucide-svelte";
  import { goto } from "$app/navigation";
  import { authStore } from "$lib/stores";
  import { getMerkleRoot } from "$lib/api";
  import { isValidSecret } from "$lib/utils/zkProof";
  import { authenticateWithZK } from "$lib/zk/zkAuth";

  // UI State
  let isLoading = false;
  let error = "";
  let statusMessage = "";

  // Form State
  let voterIdInput = "";
  let secretInput = "";
  let showSecret = false;

  async function authenticateDirectly() {
    error = "";
    statusMessage = "";

    if (!voterIdInput.trim()) {
      error = "Please enter your Voter ID";
      return;
    }

    if (!isValidSecret(secretInput)) {
      error = "Your secret must be at least 6 characters.";
      return;
    }

    isLoading = true;

    try {
      const result = await authenticateWithZK(
        voterIdInput.trim(),
        secretInput,
        (status) => {
          statusMessage = status;
        },
      );

      if (!result.success) {
        error = result.message || "Verification failed. Please try again.";
        authStore.setError(error);
        isLoading = false;
        return;
      }

      const usedVotes = result.used_votes?.map(String) || [];

      if (usedVotes.length > 0) {
        const localVotes = JSON.parse(
          localStorage.getItem("user_votes") || "{}",
        );
        usedVotes.forEach((id: string) => {
          if (!localVotes[id]) {
            localVotes[id] = "kept";
          }
        });
        localStorage.setItem("user_votes", JSON.stringify(localVotes));
      }

      let representativeData = null;
      try {
        const representativeCheck = await fetch(
          `http://localhost:8000/api/representatives/check-status?nullifier=${encodeURIComponent(result.nullifier!)}`,
        );
        if (representativeCheck.ok) {
          const data = await representativeCheck.json();
          if (data.is_representative) {
            representativeData = data.representative;
          }
        }
      } catch (e) {
        console.warn("Failed to check representative status:", e);
      }

      authStore.setCredential({
        nullifier: result.nullifier!,
        nullifierShort: result.nullifier!.substring(0, 12) + "...",
        credential: result.credential!,
        createdAt: new Date().toISOString(),
        usedVotes: usedVotes,
        verified: true,
        isRepresentative: !!representativeData,
        representativeId: representativeData?.id,
        representativeSlug: representativeData?.slug,
      });

      // Redirect to citizen portal
      goto("/citizen");
    } catch (e: any) {
      error = e.message || "Verification failed. Please check your connection.";
      console.error("Auth error:", e);
    }

    isLoading = false;
  }

  onMount(() => {
    getMerkleRoot().catch(console.error);
  });
</script>

<svelte:head>
  <title>Verify Your Identity - WaachaPatra</title>
</svelte:head>

<main class="min-h-screen bg-gray-50 flex items-center justify-center p-4">
  <div class="w-full max-w-md">
    <div class="bg-white rounded-2xl shadow-lg border border-gray-200 p-8">
      <!-- Header -->
      <div class="text-center mb-8">
        <div
          class="w-16 h-16 rounded-2xl bg-primary-100 flex items-center justify-center mx-auto mb-4"
        >
          <Shield class="w-8 h-8 text-primary-700" />
        </div>
        <h1 class="text-2xl font-bold text-gray-900 mb-2">
          Verify Your Identity
        </h1>
        <p class="text-gray-500 text-sm">Prove you're a citizen anonymously</p>
      </div>

      <!-- Form -->
      <div class="space-y-4">
        <div>
          <label
            for="voter-id"
            class="block text-sm font-medium text-gray-700 mb-1.5"
          >
            Voter ID
          </label>
          <div class="relative">
            <User
              class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2"
            />
            <input
              id="voter-id"
              type="text"
              class="w-full pl-10 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="Enter your voter ID"
              bind:value={voterIdInput}
            />
          </div>
        </div>

        <div>
          <label
            for="secret"
            class="block text-sm font-medium text-gray-700 mb-1.5"
          >
            Secret
          </label>
          <div class="relative">
            <Lock
              class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2"
            />
            {#if showSecret}
              <input
                id="secret"
                type="text"
                class="w-full pl-10 pr-12 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="Your secret (min 6 chars)"
                bind:value={secretInput}
              />
            {:else}
              <input
                id="secret"
                type="password"
                class="w-full pl-10 pr-12 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="Your secret (min 6 chars)"
                bind:value={secretInput}
              />
            {/if}
            <button
              type="button"
              class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
              on:click={() => (showSecret = !showSecret)}
            >
              {#if showSecret}
                <EyeOff class="w-5 h-5" />
              {:else}
                <Eye class="w-5 h-5" />
              {/if}
            </button>
          </div>
        </div>
      </div>

      <!-- Error -->
      {#if error}
        <div
          class="flex gap-2 items-start p-3 bg-error-50 border border-error-200 rounded-lg mt-4"
        >
          <AlertCircle class="w-5 h-5 text-error-600 flex-shrink-0" />
          <p class="text-sm text-error-700">{error}</p>
        </div>
      {/if}

      <!-- Loading Status -->
      {#if statusMessage && isLoading}
        <div
          class="flex gap-2 items-center p-3 bg-primary-50 border border-primary-200 rounded-lg mt-4"
        >
          <Loader2
            class="w-5 h-5 text-primary-600 animate-spin flex-shrink-0"
          />
          <p class="text-sm text-gray-700">{statusMessage}</p>
        </div>
      {/if}

      <!-- Submit -->
      <button
        class="w-full flex items-center justify-center gap-2 mt-6 px-6 py-3.5 bg-primary-700 hover:bg-primary-800 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-semibold rounded-xl transition-colors"
        on:click={authenticateDirectly}
        disabled={isLoading || !voterIdInput.trim() || !secretInput}
      >
        {#if isLoading}
          <Loader2 class="w-5 h-5 animate-spin" />
          Verifying...
        {:else}
          Verify
          <ArrowRight class="w-5 h-5" />
        {/if}
      </button>

      <!-- Footer -->
      <div class="mt-6 pt-6 border-t border-gray-100 text-center">
        <a href="/" class="text-sm text-gray-500 hover:text-gray-700">
          ← Back to Home
        </a>
      </div>
    </div>
  </div>
</main>
