<script lang="ts">
  import { browser } from "$app/environment";
  import ManifestoCard from "$lib/components/ManifestoCard.svelte";
  import {
    Search,
    CheckCircle,
    Clock,
    FileText,
    Shield,
    AlertCircle,
    Users,
    MessageCircle,
    TrendingUp,
    Filter,
    X,
  } from "lucide-svelte";
  import { onMount } from "svelte";
  import { authStore, isAuthenticated, credential } from "$lib/stores";
  import { getManifestos, getMerkleRoot, getNetworkStats } from "$lib/api";

  // Reactive auth state
  $: isAuth = $isAuthenticated;
  $: userCredential = $credential;

  // Data state
  let manifestos: any[] = [];
  let networkStats: any = null;
  let merkleRoot = "";
  let isLoading = true;
  let error = "";

  let searchQuery = "";
  let statusFilter = "all";

  // Load data on mount
  onMount(async () => {
    if (!browser) return;

    try {
      const [manifestoData, rootData, stats] = await Promise.all([
        getManifestos(),
        getMerkleRoot(),
        getNetworkStats(),
      ]);

      manifestos = (manifestoData.manifestos || []) as any[];
      merkleRoot = rootData.merkle_root;
      networkStats = stats;
    } catch (e) {
      error = "Failed to load data. Please try again.";
      console.error(e);
    }
    isLoading = false;
  });

  // Check if grace period has passed for voting
  function canVote(manifesto: any): boolean {
    if (!manifesto.grace_period_end) return false;
    const graceEnd = new Date(manifesto.grace_period_end);
    return new Date() >= graceEnd;
  }

  // Get remaining time until voting opens
  function getTimeUntilVoting(manifesto: any): string {
    if (!manifesto.grace_period_end) return "Unknown";
    const graceEnd = new Date(manifesto.grace_period_end);
    const now = new Date();

    if (now >= graceEnd) return "Open";

    const diff = graceEnd.getTime() - now.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days > 0) return `${days} days`;

    const hours = Math.floor(diff / (1000 * 60 * 60));
    return `${hours} hours`;
  }

  // Check if user has voted on this manifesto
  function hasVoted(manifestoId: string): boolean {
    return userCredential?.usedVotes?.includes(manifestoId) ?? false;
  }

  // Get human-readable status
  function getStatusLabel(status: string): string {
    switch (status) {
      case "kept":
        return "Being Kept";
      case "broken":
        return "Not Being Kept";
      default:
        return "Under Review";
    }
  }

  // Get citizen feedback text
  function getFeedbackText(kept: number, broken: number): string {
    const total = kept + broken;
    if (total === 0) return "No feedback yet";
    const keptPercent = (kept / total) * 100;
    if (keptPercent >= 70) return "Most citizens say this is being kept";
    if (keptPercent >= 50) return "Citizens are divided on this promise";
    if (keptPercent >= 30) return "Many citizens say this is not being kept";
    return "Most citizens say this is not being kept";
  }

  // Filter manifestos based on search and status
  $: filteredManifestos = manifestos.filter((m) => {
    const matchesSearch =
      !searchQuery ||
      m.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      m.category?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      m.representative_name?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === "all" || m.status === statusFilter;
    return matchesSearch && matchesStatus;
  });
</script>

<svelte:head>
  <title>Election Promises - WaachaPatra</title>
</svelte:head>

<main class="manifestos-page">
  <!-- Hero Section -->
  <section class="hero-section">
    <div class="container hero-content">
      <div class="hero-text">
        <h1>Election Promises</h1>
        <p>
          Official, immutable records of political commitments. Track their
          progress and hold your representatives accountable.
        </p>
      </div>

      <!-- Network Stats Ticker -->
    </div>
  </section>

  <div class="container content-wrapper">
    <!-- Stats Row -->
    <div class="stats-row">
      <div class="stat-item">
        <div class="stat-icon bg-blue-50 text-blue-600">
          <FileText class="w-6 h-6" />
        </div>
        <div class="stat-info">
          <span class="stat-value">{manifestos.length}</span>
          <span class="stat-label">Total Promises</span>
        </div>
      </div>

      <div class="stat-item">
        <div class="stat-icon bg-purple-50 text-purple-600">
          <Users class="w-6 h-6" />
        </div>
        <div class="stat-info">
          <span class="stat-value"
            >{networkStats?.total_votes?.toLocaleString() || "-"}</span
          >
          <span class="stat-label">Citizen Votes</span>
        </div>
      </div>

      <div class="stat-item">
        <div class="stat-icon bg-emerald-50 text-emerald-600">
          <Shield class="w-6 h-6" />
        </div>
        <div class="stat-info">
          <span class="stat-value text-emerald-600"
            >{networkStats?.integrity_score?.toFixed(1) || "-"}%</span
          >
          <span class="stat-label">Integrity Score</span>
        </div>
      </div>
    </div>
    <!-- Toolbar -->
    <div class="toolbar-section">
      <div class="search-box">
        <Search class="w-5 h-5 text-gray-400" />
        <input
          type="text"
          placeholder="Search promises, representatives, or topics..."
          bind:value={searchQuery}
        />
        {#if searchQuery}
          <button
            class="text-gray-400 hover:text-gray-600"
            on:click={() => (searchQuery = "")}
          >
            <X class="w-4 h-4" />
          </button>
        {/if}
      </div>

      <div class="flex items-center gap-4">
        <div class="flex items-center gap-2 text-gray-500 font-medium">
          <Filter class="w-4 h-4" />
          <span>Filter:</span>
        </div>
        <div class="filter-tabs">
          <button
            class="filter-tab"
            class:active={statusFilter === "all"}
            on:click={() => (statusFilter = "all")}
          >
            All
          </button>
          <button
            class="filter-tab kept"
            class:active={statusFilter === "kept"}
            on:click={() => (statusFilter = "kept")}
          >
            Kept
          </button>
          <button
            class="filter-tab broken"
            class:active={statusFilter === "broken"}
            on:click={() => (statusFilter = "broken")}
          >
            Broken
          </button>
          <button
            class="filter-tab pending"
            class:active={statusFilter === "pending"}
            on:click={() => (statusFilter = "pending")}
          >
            In Progress
          </button>
        </div>
      </div>
    </div>

    <!-- Content Area -->
    <div class="promises-grid-wrapper">
      {#if isLoading}
        <div class="loading-state">
          <div class="spinner"></div>
          <p>Loading promises from blockchain...</p>
        </div>
      {:else if error}
        <div class="error-state">
          <AlertCircle class="w-12 h-12 text-error-500 mb-4" />
          <h3>Unable to load data</h3>
          <p>{error}</p>
          <button
            class="btn btn-primary mt-4"
            on:click={() => location.reload()}>Retry Connection</button
          >
        </div>
      {:else if filteredManifestos.length === 0}
        <div class="empty-state">
          <div class="empty-icon">
            <Search class="w-8 h-8" />
          </div>
          <h3>No promises found</h3>
          <p>Try adjusting your search or filters.</p>
          <button
            class="btn btn-secondary mt-4"
            on:click={() => {
              searchQuery = "";
              statusFilter = "all";
            }}
          >
            Clear Filters
          </button>
        </div>
      {:else}
        <div class="promises-grid">
          {#each filteredManifestos as manifesto (manifesto.id)}
            <ManifestoCard {manifesto} />
          {/each}
        </div>

        <div class="results-count">
          Showing {filteredManifestos.length} results
        </div>
      {/if}
    </div>
  </div>
</main>

<style>
</style>
