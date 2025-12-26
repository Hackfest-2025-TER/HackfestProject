<script lang="ts">
  import Header from "$lib/components/Header.svelte";
  import Footer from "$lib/components/Footer.svelte";
  import {
    FileText,
    Plus,
    Clock,
    CheckCircle,
    XCircle,
    Eye,
    Filter,
    Search,
    Calendar,
    TrendingUp,
    ChevronRight,
    Hash,
    Shield,
    BarChart,
  } from "lucide-svelte";
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";
  import { getManifestos } from "$lib/api";

  // Representative session (in production, get from auth)
  let representativeSession: any = null;
  let manifestos: any[] = [];
  let isLoading = true;
  let error = "";

  // Filters
  let statusFilter = "all";
  let searchQuery = "";

  onMount(async () => {
    // Check if logged in
    const session = localStorage.getItem("representative_session");
    if (!session) {
      goto("/representative/login");
      return;
    }
    representativeSession = JSON.parse(session);

    await loadManifestos();
  });

  async function loadManifestos() {
    try {
      isLoading = true;
      const data = await getManifestos({
        representative_id: representativeSession?.id,
      });
      manifestos = data.manifestos || [];
    } catch (e: any) {
      error = e.message;
    } finally {
      isLoading = false;
    }
  }

  // Filter manifestos
  $: filteredManifestos = manifestos.filter((m) => {
    const matchesStatus = statusFilter === "all" || m.status === statusFilter;
    const matchesSearch =
      !searchQuery ||
      m.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      m.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesStatus && matchesSearch;
  });

  // Stats
  $: stats = {
    total: manifestos.length,
    pending: manifestos.filter((m) => m.status === "pending").length,
    kept: manifestos.filter((m) => m.status === "kept").length,
    broken: manifestos.filter((m) => m.status === "broken").length,
  };

  function getStatusColor(status: string) {
    switch (status) {
      case "kept":
        return "text-success-700 bg-success-50 border-success-200";
      case "broken":
        return "text-error-700 bg-error-50 border-error-200";
      default:
        return "text-warning-700 bg-warning-50 border-warning-200";
    }
  }

  function getStatusIcon(status: string) {
    switch (status) {
      case "kept":
        return CheckCircle;
      case "broken":
        return XCircle;
      default:
        return Clock;
    }
  }

  function formatDate(dateStr: string) {
    return new Date(dateStr).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  }
</script>

<svelte:head>
  <title>My Promises - PromiseThread</title>
</svelte:head>

<Header />

<main class="page-wrapper">
  <!-- Hero Section -->
  <section class="hero-section">
    <div class="container hero-content">
      <div class="hero-text">
        <h1>My Promises</h1>
        <p>
          {#if representativeSession}
            Manage your commitments as {representativeSession.name}
          {:else}
            Loading...
          {/if}
        </p>
      </div>
      <div class="hero-actions mt-6">
        <a href="/representative/new-manifesto" class="btn btn-primary btn-lg">
          <Plus class="w-5 h-5" />
          New Promise
        </a>
      </div>
    </div>
  </section>

  <div class="container content-wrapper">
    <!-- Stats Row -->
    <div
      class="grid grid-cols-2 md:grid-cols-4 gap-6 -mt-20 mb-10 relative z-10"
    >
      <div class="stat-item">
        <div class="stat-icon bg-blue-50 text-blue-600">
          <FileText class="w-6 h-6" />
        </div>
        <div class="stat-info">
          <span class="stat-value">{stats.total}</span>
          <span class="stat-label">Total</span>
        </div>
      </div>

      <div class="stat-item">
        <div class="stat-icon bg-warning-50 text-warning-600">
          <Clock class="w-6 h-6" />
        </div>
        <div class="stat-info">
          <span class="stat-value">{stats.pending}</span>
          <span class="stat-label">Pending</span>
        </div>
      </div>

      <div class="stat-item">
        <div class="stat-icon bg-success-50 text-success-600">
          <CheckCircle class="w-6 h-6" />
        </div>
        <div class="stat-info">
          <span class="stat-value">{stats.kept}</span>
          <span class="stat-label">Kept</span>
        </div>
      </div>

      <div class="stat-item">
        <div class="stat-icon bg-error-50 text-error-600">
          <XCircle class="w-6 h-6" />
        </div>
        <div class="stat-info">
          <span class="stat-value">{stats.broken}</span>
          <span class="stat-label">Broken</span>
        </div>
      </div>
    </div>

    <!-- Toolbar -->
    <div class="toolbar-section">
      <div class="search-box">
        <Search class="w-5 h-5 text-gray-400" />
        <input
          type="text"
          bind:value={searchQuery}
          placeholder="Search promises..."
        />
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
            class="filter-tab pending"
            class:active={statusFilter === "pending"}
            on:click={() => (statusFilter = "pending")}
          >
            Pending
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
        </div>
      </div>
    </div>

    <!-- Manifestos List -->
    {#if isLoading}
      <div class="loading-state">
        <div
          class="w-8 h-8 border-2 border-primary-500/30 border-t-primary-500 rounded-full animate-spin mx-auto mb-4"
        ></div>
        <p>Loading your promises...</p>
      </div>
    {:else if error}
      <div class="error-state">
        <XCircle class="w-12 h-12 text-error-500 mb-4" />
        <p class="text-error-700">{error}</p>
      </div>
    {:else if filteredManifestos.length === 0}
      <div class="empty-state">
        <div
          class="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center mb-4"
        >
          <FileText class="w-8 h-8 text-gray-400" />
        </div>
        <h3>No promises found</h3>
        <p class="mb-6">
          {manifestos.length === 0
            ? "You haven't created any promises yet."
            : "No promises match your filters."}
        </p>
        {#if manifestos.length === 0}
          <a href="/representative/new-manifesto" class="btn btn-primary">
            <Plus class="w-5 h-5" />
            Create Your First Promise
          </a>
        {/if}
      </div>
    {:else}
      <div class="grid gap-4">
        {#each filteredManifestos as manifesto}
          <a
            href="/manifestos/{manifesto.id}"
            class="card hover:border-primary-500 transition-all group no-underline"
          >
            <div class="flex items-start justify-between gap-4">
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-3 mb-2">
                  <h3
                    class="text-lg font-bold text-gray-900 truncate group-hover:text-primary-700 transition-colors"
                  >
                    {manifesto.title}
                  </h3>
                  <span
                    class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold border {getStatusColor(
                      manifesto.status,
                    )}"
                  >
                    <svelte:component
                      this={getStatusIcon(manifesto.status)}
                      class="w-3 h-3"
                    />
                    {manifesto.status}
                  </span>
                </div>

                <p class="text-gray-600 text-sm line-clamp-2 mb-4">
                  {manifesto.description}
                </p>

                <div class="flex flex-wrap items-center gap-4 text-sm">
                  <div class="flex items-center gap-1.5 text-gray-500">
                    <Calendar class="w-4 h-4" />
                    <span>{formatDate(manifesto.created_at)}</span>
                  </div>
                  <div class="flex items-center gap-1 text-gray-500">
                    <span
                      class="px-2 py-0.5 bg-gray-100 border border-gray-200 rounded text-xs font-medium text-gray-700"
                      >{manifesto.category}</span
                    >
                  </div>
                  {#if manifesto.hash}
                    <div class="flex items-center gap-1.5 text-gray-500">
                      <Hash class="w-4 h-4" />
                      <span
                        class="font-mono text-xs bg-gray-50 px-1.5 py-0.5 rounded border border-gray-200"
                        >{manifesto.hash.slice(0, 10)}...</span
                      >
                    </div>
                  {/if}
                  <div
                    class="flex items-center gap-2 text-gray-500 font-medium"
                  >
                    <TrendingUp class="w-4 h-4 text-primary-500" />
                    <span>
                      {manifesto.vote_kept || 0} kept / {manifesto.vote_broken ||
                        0} broken
                    </span>
                  </div>
                </div>
              </div>

              <ChevronRight
                class="w-5 h-5 text-gray-400 group-hover:text-primary-500 transition-colors flex-shrink-0"
              />
            </div>
          </a>
        {/each}
      </div>
    {/if}

    <!-- Quick Actions -->
    <div class="mt-12 grid md:grid-cols-3 gap-6">
      <a
        href="/representative/wallet"
        class="card hover:border-blue-500 transition-all group no-underline"
      >
        <Shield class="w-6 h-6 text-blue-500 mb-2" />
        <h3
          class="text-gray-900 text-lg font-bold group-hover:text-blue-600 transition-colors"
        >
          Wallet & Keys
        </h3>
        <p class="text-gray-500 text-sm">Manage your signing keys</p>
      </a>
      <a
        href="/representative/dashboard"
        class="card hover:border-primary-500 transition-all group no-underline"
      >
        <BarChart class="w-6 h-6 text-primary-600 mb-2" />
        <h3
          class="text-gray-900 text-lg font-bold group-hover:text-primary-700 transition-colors"
        >
          Dashboard
        </h3>
        <p class="text-gray-500 text-sm">View analytics and insights</p>
      </a>
      <a
        href="/representative/profile"
        class="card hover:border-purple-500 transition-all group no-underline"
      >
        <Eye class="w-6 h-6 text-purple-500 mb-2" />
        <h3
          class="text-gray-900 text-lg font-bold group-hover:text-purple-600 transition-colors"
        >
          Public Profile
        </h3>
        <p class="text-gray-500 text-sm">See how citizens view you</p>
      </a>
    </div>
  </div>
</main>

<Footer />
