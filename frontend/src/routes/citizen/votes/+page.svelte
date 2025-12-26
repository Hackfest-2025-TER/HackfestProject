<script lang="ts">
  import {
    Vote,
    CheckCircle,
    XCircle,
    Clock,
    Calendar,
    Hash,
    ChevronRight,
    Shield,
    AlertCircle,
    ExternalLink,
    Filter,
  } from "lucide-svelte";
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";
  import { browser } from "$app/environment";
  import { authStore, isAuthenticated, credential } from "$lib/stores";
  import { getManifesto } from "$lib/api";

  // Reactive auth state
  $: isAuth = $isAuthenticated;
  $: userCredential = $credential;

  // Data
  let votedManifestos: any[] = [];
  let isLoading = true;
  let error = "";

  // Filter
  let voteFilter = "all";

  onMount(async () => {
    if (!browser) return;

    // Check if authenticated
    if (!$isAuthenticated) {
      goto("/auth");
      return;
    }

    await loadVotedManifestos();
  });

  async function loadVotedManifestos() {
    try {
      isLoading = true;
      const votedIds = userCredential?.usedVotes || [];

      // Load details for each voted manifesto
      const manifestoPromises = votedIds.map(async (id: string) => {
        try {
          const manifesto = await getManifesto(id);
          // In a real app, we'd store the vote type with the ID
          // For demo, we'll randomly assign or use local storage
          const storedVote = localStorage.getItem(`vote_${id}`);
          return {
            ...manifesto,
            myVote: storedVote || "kept", // Default assumption
            votedAt:
              localStorage.getItem(`vote_time_${id}`) ||
              new Date().toISOString(),
          };
        } catch (e) {
          return null;
        }
      });

      const results = await Promise.all(manifestoPromises);
      votedManifestos = results.filter((m) => m !== null);
    } catch (e: any) {
      error = e.message || "Failed to load votes";
    } finally {
      isLoading = false;
    }
  }

  // Filtered manifestos
  $: filteredManifestos =
    voteFilter === "all"
      ? votedManifestos
      : votedManifestos.filter((m) => m.myVote === voteFilter);

  // Stats
  $: stats = {
    total: votedManifestos.length,
    kept: votedManifestos.filter((m) => m.myVote === "kept").length,
    broken: votedManifestos.filter((m) => m.myVote === "broken").length,
  };

  function formatDate(dateStr: string) {
    return new Date(dateStr).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  }

  function getVoteIcon(vote: string) {
    return vote === "kept" ? CheckCircle : XCircle;
  }

  function getVoteColor(vote: string) {
    return vote === "kept"
      ? "text-emerald-400 bg-emerald-500/10 border-emerald-500/20"
      : "text-red-400 bg-red-500/10 border-red-500/20";
  }
</script>

<svelte:head>
  <title>My Votes - WaachaPatra</title>
</svelte:head>

<main class="page-wrapper">
  <div class="container container-sm">
    <!-- Header -->
    <div class="hero-section mb-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">My Votes</h1>
      <p class="text-gray-600">Your anonymous voting history</p>
    </div>

    {#if !isAuth}
      <!-- Not authenticated -->
      <div class="bg-gray-800 rounded-xl p-8 text-center">
        <Shield class="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h2 class="text-xl font-semibold text-white mb-2">
          Authentication Required
        </h2>
        <p class="text-gray-400 mb-6">
          You need to verify as a citizen to view your votes.
        </p>
        <a href="/auth" class="btn btn-primary">
          <Shield class="w-5 h-5 mr-2" />
          Verify as Citizen
        </a>
      </div>
    {:else if isLoading}
      <div class="text-center py-12">
        <div
          class="w-8 h-8 border-2 border-primary-500/30 border-t-primary-500 rounded-full animate-spin mx-auto mb-4"
        ></div>
        <p class="text-gray-500">Loading your votes...</p>
      </div>
    {:else if error}
      <div class="card p-6 text-center border-error-200 bg-error-50">
        <AlertCircle class="w-8 h-8 text-error-500 mx-auto mb-2" />
        <p class="text-error-600">{error}</p>
      </div>
    {:else}
      <!-- Stats -->
      <div class="grid grid-cols-3 gap-4 mb-8">
        <div class="card p-4 text-center">
          <div class="text-2xl font-bold text-gray-900 mb-1">{stats.total}</div>
          <div
            class="text-gray-500 text-sm font-medium uppercase tracking-wide"
          >
            Total Votes
          </div>
        </div>
        <div class="card p-4 text-center">
          <div class="text-2xl font-bold text-success-600 mb-1">
            {stats.kept}
          </div>
          <div
            class="text-gray-500 text-sm font-medium uppercase tracking-wide"
          >
            Voted Kept
          </div>
        </div>
        <div class="card p-4 text-center">
          <div class="text-2xl font-bold text-error-600 mb-1">
            {stats.broken}
          </div>
          <div
            class="text-gray-500 text-sm font-medium uppercase tracking-wide"
          >
            Voted Broken
          </div>
        </div>
      </div>

      <!-- Privacy Notice -->
      <div
        class="bg-primary-50 border border-primary-100 rounded-xl p-4 mb-8 flex gap-3"
      >
        <Shield class="w-5 h-5 text-primary-600 flex-shrink-0 mt-0.5" />
        <div>
          <h3 class="text-primary-800 font-medium mb-1 text-sm">
            Your Privacy is Protected
          </h3>
          <p class="text-primary-700 text-sm leading-relaxed">
            This history is stored locally in your browser. No one else can see
            your individual votes. Only aggregate totals are public on the
            blockchain.
          </p>
        </div>
      </div>

      <!-- Filter -->
      <div class="flex items-center gap-3 mb-6">
        <Filter class="w-4 h-4 text-gray-400" />
        <div class="flex gap-2">
          <button
            on:click={() => (voteFilter = "all")}
            class="px-4 py-1.5 rounded-full text-sm font-medium transition-all
              {voteFilter === 'all'
              ? 'bg-gray-800 text-white'
              : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-50'}"
          >
            All
          </button>
          <button
            on:click={() => (voteFilter = "kept")}
            class="px-4 py-1.5 rounded-full text-sm font-medium transition-all
              {voteFilter === 'kept'
              ? 'bg-success-100 text-success-700 border border-success-200'
              : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-50'}"
          >
            Kept
          </button>
          <button
            on:click={() => (voteFilter = "broken")}
            class="px-4 py-1.5 rounded-full text-sm font-medium transition-all
              {voteFilter === 'broken'
              ? 'bg-error-100 text-error-700 border border-error-200'
              : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-50'}"
          >
            Broken
          </button>
        </div>
      </div>

      <!-- Votes List -->
      {#if filteredManifestos.length === 0}
        <div class="card p-12 text-center">
          <Vote class="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <h3 class="text-lg font-semibold text-gray-900 mb-2">
            No votes found
          </h3>
          <p class="text-gray-500 mb-6">
            {votedManifestos.length === 0
              ? "You haven't voted on any promises yet."
              : "No votes match this filter."}
          </p>
          {#if votedManifestos.length === 0}
            <a
              href="/manifestos"
              class="inline-flex items-center gap-2 px-6 py-3 bg-primary-700 hover:bg-primary-800 text-white font-semibold rounded-xl shadow-lg shadow-primary-700/20 transition-all hover:shadow-xl"
            >
              Browse Promises
              <ChevronRight class="w-4 h-4" />
            </a>
          {/if}
        </div>
      {:else}
        <div class="space-y-4">
          {#each filteredManifestos as manifesto}
            {@const total =
              (manifesto.vote_kept || 0) + (manifesto.vote_broken || 0)}
            {@const keptPercent =
              total > 0 ? ((manifesto.vote_kept || 0) / total) * 100 : 50}

            <div class="card p-5 hover:shadow-md transition-shadow">
              <div class="flex items-start justify-between gap-4">
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-3 mb-2">
                    <a
                      href="/manifestos/{manifesto.id}"
                      class="text-lg font-semibold text-gray-900 hover:text-primary-600 transition-colors truncate"
                    >
                      {manifesto.title}
                    </a>
                  </div>

                  <p
                    class="text-gray-600 text-sm line-clamp-2 mb-3 leading-relaxed"
                  >
                    {manifesto.description}
                  </p>

                  <div
                    class="flex flex-wrap items-center gap-4 text-xs text-gray-500"
                  >
                    <div class="flex items-center gap-1">
                      <span>By {manifesto.representative_name}</span>
                    </div>
                    <div class="flex items-center gap-1">
                      <Calendar class="w-3.5 h-3.5" />
                      <span>{formatDate(manifesto.votedAt)}</span>
                    </div>
                  </div>
                </div>

                <div class="flex flex-col items-end gap-2">
                  <!-- My Vote Badge -->
                  <span
                    class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border uppercase tracking-wider {getVoteColor(
                      manifesto.myVote,
                    )}"
                  >
                    <svelte:component
                      this={getVoteIcon(manifesto.myVote)}
                      class="w-3.5 h-3.5"
                    />
                    {manifesto.myVote === "kept" ? "Kept" : "Broken"}
                  </span>

                  <!-- Current Status -->
                  <span
                    class="text-xs text-gray-400 capitalize bg-gray-50 px-2 py-0.5 rounded border border-gray-100"
                  >
                    {manifesto.status || "pending"}
                  </span>
                </div>
              </div>

              <!-- Vote Comparison -->
              <div class="mt-4 pt-4 border-t border-gray-100">
                <div class="flex items-center justify-between text-xs mb-2">
                  <span class="text-gray-500 font-medium"
                    >Community Consensus</span
                  >
                  <div class="flex items-center gap-3">
                    <span class="text-success-600 font-medium">
                      {manifesto.vote_kept || 0} kept
                    </span>
                    <span class="text-error-600 font-medium">
                      {manifesto.vote_broken || 0} broken
                    </span>
                  </div>
                </div>
                <!-- Progress Bar -->
                <div
                  class="h-1.5 bg-gray-100 rounded-full overflow-hidden flex"
                >
                  <div
                    class="h-full bg-success-500"
                    style="width: {keptPercent}%"
                  ></div>
                  <div
                    class="h-full bg-error-500"
                    style="width: {100 - keptPercent}%"
                  ></div>
                </div>
              </div>
            </div>
          {/each}
        </div>
      {/if}

      <!-- Nullifier Info -->
      <div
        class="mt-8 flex items-center justify-center gap-2 text-xs text-gray-400"
      >
        <Hash class="w-3 h-3" />
        <span
          >Anonymous ID: <span class="font-mono text-gray-500"
            >{userCredential?.nullifierShort || "Unknown"}</span
          ></span
        >
      </div>
    {/if}
  </div>
</main>
