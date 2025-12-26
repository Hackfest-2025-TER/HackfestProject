<script lang="ts">
  import { onMount } from "svelte";
  import RepresentativeCard from "$lib/components/RepresentativeCard.svelte";
  import {
    Search,
    Filter,
    Shield,
    Award,
    Clock,
    FileText,
    ChevronRight,
    CheckCircle,
    AlertCircle,
    UserPlus,
    X,
  } from "lucide-svelte";
  import { authStore } from "$lib/stores";

  // Fetch representatives from API
  let representatives: any[] = [];
  let loading = true;
  let error = "";
  let searchQuery = "";
  let selectedParty = "all";

  // Get unique parties for filter
  $: parties = [...new Set(representatives.map((p) => p.party))];

  onMount(async () => {
    try {
      // Use relative path which is proxied in dev/prod
      const response = await fetch("/api/representatives");
      const data = await response.json();
      representatives = data.representatives || [];
      loading = false;
    } catch (err) {
      error = "Failed to load representatives data";
      loading = false;
      console.error("Error fetching representatives:", err);
    }
  });

  $: filteredRepresentatives = representatives.filter((p) => {
    const matchesSearch =
      p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.title.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesParty = selectedParty === "all" || p.party === selectedParty;
    return matchesSearch && matchesParty;
  });
</script>

<svelte:head>
  <title>Elected Representatives - PromiseThread</title>
</svelte:head>

<main class="representatives-page">
  <!-- Hero Section -->
  <section class="hero-section">
    <div class="container text-center">
      <h1
        class="text-4xl md:text-5xl font-extrabold text-gray-900 mb-4 tracking-tight"
      >
        Elected Representatives
      </h1>
      <p class="text-xl text-gray-500 max-w-2xl mx-auto mb-8 leading-relaxed">
        Discover profiles, track performance, and hold your leaders accountable
        based on their promise fulfillment.
      </p>

      {#if $authStore.isAuthenticated && !$authStore.credential?.isRepresentative}
        <a
          href="/representative/register"
          class="inline-flex items-center gap-2 px-6 py-3 bg-primary-600 text-white rounded-full font-semibold shadow-md hover:bg-primary-700 transition-all hover:-translate-y-1"
        >
          <UserPlus class="w-5 h-5" />
          Register as Representative
        </a>
      {/if}
    </div>
  </section>

  <div class="container content-wrapper px-6 pb-20">
    <!-- Toolbar -->
    <div
      class="flex flex-col md:flex-row justify-between items-center gap-4 mb-8 bg-white p-4 rounded-xl shadow-sm border border-gray-200"
    >
      <!-- Search -->
      <div class="relative w-full md:w-96">
        <div
          class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400"
        >
          <Search class="w-5 h-5" />
        </div>
        <input
          type="text"
          placeholder="Search reps by name or title..."
          bind:value={searchQuery}
          class="w-full pl-10 pr-10 py-2.5 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-100 focus:border-primary-500 transition-all"
        />
        {#if searchQuery}
          <button
            class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 cursor-pointer"
            on:click={() => (searchQuery = "")}
          >
            <X class="w-4 h-4" />
          </button>
        {/if}
      </div>

      <!-- Filters -->
      <div
        class="flex items-center gap-3 w-full md:w-auto overflow-x-auto pb-2 md:pb-0"
      >
        <div
          class="flex items-center gap-2 text-sm font-semibold text-gray-500 whitespace-nowrap"
        >
          <Filter class="w-4 h-4" />
          <span>Filter Party:</span>
        </div>
        <select
          bind:value={selectedParty}
          class="px-4 py-2 bg-white border border-gray-200 rounded-lg text-sm text-gray-700 font-medium cursor-pointer focus:outline-none focus:border-primary-500 hover:border-gray-300 transition-all shadow-sm"
        >
          <option value="all">All Parties</option>
          {#each parties as party}
            <option value={party}>{party}</option>
          {/each}
        </select>
      </div>
    </div>

    <!-- Loading State -->
    {#if loading}
      <div
        class="flex flex-col items-center justify-center py-20 text-gray-500"
      >
        <div
          class="w-10 h-10 border-4 border-gray-200 border-t-primary-600 rounded-full animate-spin mb-4"
        ></div>
        <p>Loading representatives...</p>
      </div>
    {:else if error}
      <div
        class="flex flex-col items-center justify-center py-20 text-error-600 bg-error-50 rounded-xl border border-error-200"
      >
        <AlertCircle class="w-12 h-12 mb-4" />
        <p>{error}</p>
        <button
          class="mt-4 px-4 py-2 bg-white border border-error-200 rounded-lg text-sm font-medium hover:bg-error-50 transition-colors"
          on:click={() => location.reload()}>Retry</button
        >
      </div>
    {:else if filteredRepresentatives.length === 0}
      <div
        class="flex flex-col items-center justify-center py-20 text-gray-500 bg-white rounded-xl border border-gray-200 shadow-sm"
      >
        <div
          class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4 text-gray-400"
        >
          <Search class="w-8 h-8" />
        </div>
        <h3 class="text-lg font-bold text-gray-900 mb-2">
          No representatives found
        </h3>
        <p class="mb-6 text-center max-w-md">
          We couldn't find any representatives matching "{searchQuery}" or the
          selected filters.
        </p>
        <button
          class="px-4 py-2 bg-white border border-gray-300 rounded-lg font-medium text-gray-700 hover:bg-gray-50 transition-colors shadow-sm"
          on:click={() => {
            searchQuery = "";
            selectedParty = "all";
          }}
        >
          Clear Filters
        </button>
      </div>
    {:else}
      <!-- Representatives Grid -->
      <div
        class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
      >
        {#each filteredRepresentatives as representative (representative.id)}
          <RepresentativeCard {representative} />
        {/each}
      </div>

      <div class="text-center mt-12 text-gray-400 text-sm">
        Showing {filteredRepresentatives.length} representatives
      </div>
    {/if}
  </div>
</main>

<style>
  .representatives-page {
    min-height: 100vh;
  }
</style>
