<script lang="ts">
  import { onMount } from "svelte";
  import {
    Shield,
    CheckCircle,
    XCircle,
    Clock,
    ChevronRight,
    MapPin,
    Calendar,
    Award,
    Hash,
  } from "lucide-svelte";
  import { page } from "$app/stores";

  $: id = $page.params.id;

  let representative: any = null;
  let loading = true;
  let error = "";

  $: stats = representative
    ? {
        kept: representative.manifestos.filter((m: any) => m.status === "kept")
          .length,
        broken: representative.manifestos.filter(
          (m: any) => m.status === "broken",
        ).length,
        pending: representative.manifestos.filter(
          (m: any) => m.status === "pending",
        ).length,
        total: representative.manifestos.length,
      }
    : { kept: 0, broken: 0, pending: 0, total: 0 };

  onMount(async () => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/representatives/${id}`,
      );
      if (!response.ok) throw new Error("Representative not found");
      representative = await response.json();
    } catch (err: any) {
      error = err.message || "Failed to load representative data";
    } finally {
      loading = false;
    }
  });

  function formatDate(dateStr: string) {
    if (!dateStr) return "N/A";
    return new Date(dateStr).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  }

  function getStatusColor(status: string) {
    switch (status) {
      case "kept":
        return "text-green-600 bg-green-50 border-green-200";
      case "broken":
        return "text-red-600 bg-red-50 border-red-200";
      default:
        return "text-yellow-600 bg-yellow-50 border-yellow-200";
    }
  }
</script>

<svelte:head>
  <title>{representative?.name || "Profile"} - WaachaPatra</title>
</svelte:head>

<main class="profile-page">
  <div class="container mx-auto px-4 py-8 max-w-5xl">
    <!-- Breadcrumb -->
    <nav class="mb-6 text-sm text-gray-500">
      <a href="/representatives" class="hover:text-primary-600"
        >Representatives</a
      >
      <span class="mx-2">/</span>
      <span class="text-gray-900 font-medium"
        >{representative?.name || "Loading..."}</span
      >
    </nav>

    {#if loading}
      <div class="py-20 text-center text-gray-500">Loading profile...</div>
    {:else if error}
      <div
        class="bg-red-50 text-red-700 p-6 rounded-lg text-center border border-red-200"
      >
        <h2 class="text-xl font-bold mb-2">Error Loading Profile</h2>
        <p>{error}</p>
        <a
          href="/representatives"
          class="inline-block mt-4 text-sm font-semibold hover:underline"
          >Return to list</a
        >
      </div>
    {:else}
      <!-- Header Section -->
      <header
        class="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden mb-8"
      >
        <!-- Cover / Top Banner (Optional Gradient) -->
        <div
          class="h-32 bg-gradient-to-r from-blue-700 to-indigo-800 relative"
        ></div>

        <div class="px-8 pb-8 relative">
          <div class="flex flex-col md:flex-row gap-6 items-end -mt-10">
            <!-- Avatar -->
            <div class="relative">
              {#if representative.image_url}
                <img
                  src={representative.image_url}
                  alt={representative.name}
                  class="w-32 h-32 rounded-full border-4 border-white shadow-md object-cover bg-gray-100"
                />
              {:else}
                <div
                  class="w-32 h-32 rounded-full border-4 border-white shadow-md bg-gray-200 flex items-center justify-center text-4xl font-bold text-gray-400"
                >
                  {representative.name[0]}
                </div>
              {/if}
              {#if representative.verified}
                <div
                  class="absolute bottom-2 right-2 bg-blue-600 text-white p-1.5 rounded-full border-2 border-white shadow-sm"
                  title="Verified Representative"
                >
                  <Shield size={16} fill="currentColor" />
                </div>
              {/if}
            </div>

            <!-- Info -->
            <div class="flex-1 min-w-0 pb-1">
              <div class="flex items-center gap-3 mb-1">
                <h1 class="text-3xl font-bold text-gray-900 truncate">
                  {representative.name}
                </h1>
                {#if representative.party}
                  <span
                    class="px-2.5 py-0.5 rounded-full bg-gray-100 text-gray-700 text-xs font-semibold border border-gray-200 mt-1"
                  >
                    {representative.party}
                  </span>
                {/if}
              </div>
              <div class="flex flex-wrap gap-4 text-sm text-gray-700 mt-2">
                <div class="flex items-center gap-1.5">
                  <Award size={16} class="text-gray-500" />
                  <span>{representative.title || "Representative"}</span>
                </div>
                <div class="flex items-center gap-1.5">
                  <MapPin size={16} class="text-gray-500" />
                  <span
                    >{representative.constituency || "Unknown District"}</span
                  >
                </div>
              </div>
            </div>

            <!-- Integrity Score (Prominent) -->
            <div
              class="flex flex-col items-end md:border-l md:border-gray-100 md:pl-8"
            >
              <div
                class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1"
              >
                Integrity Score
              </div>
              <div class="flex items-baseline gap-1.5">
                <span
                  class="text-5xl font-black {representative.integrity_score >=
                  80
                    ? 'text-green-600'
                    : representative.integrity_score >= 50
                      ? 'text-yellow-600'
                      : 'text-red-600'}"
                >
                  {representative.integrity_score}
                </span>
                <span class="text-gray-400 font-medium">/100</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Stats Bar -->
        <div
          class="border-t border-gray-100 bg-gray-50/50 px-8 py-4 grid grid-cols-1 md:grid-cols-3 gap-4"
        >
          <div
            class="flex items-center justify-between p-3 bg-white rounded-lg border border-gray-200 shadow-sm"
          >
            <div class="flex items-center gap-3">
              <div class="p-2 bg-green-50 text-green-600 rounded-md">
                <CheckCircle size={20} />
              </div>
              <div>
                <p class="text-xs text-gray-500 font-medium uppercase">
                  Kept Promises
                </p>
                <p class="text-lg font-bold text-gray-900">{stats.kept}</p>
              </div>
            </div>
            <div class="h-10 w-px bg-gray-100 mx-2"></div>
            <span
              class="text-xs font-semibold text-green-600 bg-green-50 px-2 py-1 rounded"
            >
              {stats.total ? Math.round((stats.kept / stats.total) * 100) : 0}%
            </span>
          </div>

          <div
            class="flex items-center justify-between p-3 bg-white rounded-lg border border-gray-200 shadow-sm"
          >
            <div class="flex items-center gap-3">
              <div class="p-2 bg-red-50 text-red-600 rounded-md">
                <XCircle size={20} />
              </div>
              <div>
                <p class="text-xs text-gray-500 font-medium uppercase">
                  Broken Promises
                </p>
                <p class="text-lg font-bold text-gray-900">{stats.broken}</p>
              </div>
            </div>
            <div class="h-10 w-px bg-gray-100 mx-2"></div>
            <span
              class="text-xs font-semibold text-red-600 bg-red-50 px-2 py-1 rounded"
            >
              {stats.total
                ? Math.round((stats.broken / stats.total) * 100)
                : 0}%
            </span>
          </div>

          <div
            class="flex items-center justify-between p-3 bg-white rounded-lg border border-gray-200 shadow-sm"
          >
            <div class="flex items-center gap-3">
              <div class="p-2 bg-yellow-50 text-yellow-600 rounded-md">
                <Clock size={20} />
              </div>
              <div>
                <p class="text-xs text-gray-500 font-medium uppercase">
                  In Progress
                </p>
                <p class="text-lg font-bold text-gray-900">{stats.pending}</p>
              </div>
            </div>
            <div class="h-10 w-px bg-gray-100 mx-2"></div>
            <span
              class="text-xs font-semibold text-yellow-600 bg-yellow-50 px-2 py-1 rounded"
            >
              {stats.total
                ? Math.round((stats.pending / stats.total) * 100)
                : 0}%
            </span>
          </div>
        </div>
      </header>

      <!-- Manifestos List -->
      <section>
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-bold text-gray-900 flex items-center gap-2">
            Promise Record
            <span
              class="px-2 py-0.5 bg-gray-100 text-gray-600 rounded-full text-xs font-medium"
              >{stats.total}</span
            >
          </h2>

          <!-- Filter (Visual only for now) -->
          <div class="flex bg-gray-100 p-1 rounded-lg">
            <button
              class="px-3 py-1 text-xs font-semibold bg-white text-gray-800 shadow-sm rounded-md"
              >All</button
            >
            <button
              class="px-3 py-1 text-xs font-medium text-gray-500 hover:text-gray-700"
              >Kept</button
            >
            <button
              class="px-3 py-1 text-xs font-medium text-gray-500 hover:text-gray-700"
              >Broken</button
            >
          </div>
        </div>

        <div class="space-y-3">
          {#if representative.manifestos.length === 0}
            <div
              class="p-12 text-center bg-gray-50 rounded-xl border border-dashed border-gray-300"
            >
              <p class="text-gray-500">
                No promises recorded for this representative yet.
              </p>
            </div>
          {:else}
            {#each representative.manifestos as manifesto}
              <a
                href="/manifestos/{manifesto.id}"
                class="group block bg-white border border-gray-200 rounded-xl p-5 hover:shadow-md hover:border-gray-300 transition-all"
              >
                <div class="flex items-start justify-between gap-4">
                  <div class="flex-1">
                    <div class="flex items-center gap-2 mb-2">
                      <span
                        class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wide {getStatusColor(
                          manifesto.status,
                        )}"
                      >
                        {manifesto.status}
                      </span>
                      <span
                        class="text-xs text-gray-400 flex items-center gap-1"
                      >
                        <Calendar size={12} />
                        {formatDate(manifesto.deadline)}
                      </span>
                    </div>
                    <h3
                      class="text-lg font-semibold text-gray-900 group-hover:text-primary-600 transition-colors mb-1"
                    >
                      {manifesto.title}
                    </h3>
                    <p class="text-sm text-gray-600 line-clamp-2">
                      {manifesto.description || "No details provided."}
                    </p>
                  </div>
                  <div
                    class="text-gray-300 group-hover:text-primary-500 transition-colors self-center"
                  >
                    <ChevronRight size={20} />
                  </div>
                </div>
              </a>
            {/each}
          {/if}
        </div>
      </section>
    {/if}
  </div>
</main>

<style>
  :global(body) {
    background-color: var(--gray-50);
  }
</style>
