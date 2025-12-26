<script lang="ts">
  import { onMount } from "svelte";
  import { page } from "$app/stores";
  import CommentThread from "$lib/components/CommentThread.svelte";
  import VoteBox from "$lib/components/VoteBox.svelte";
  import HashDisplay from "$lib/components/HashDisplay.svelte";
  import { getManifesto } from "$lib/api";
  import {
    Shield,
    ThumbsUp,
    MessageSquare,
    Share2,
    ExternalLink,
    Clock,
    CheckCircle,
    Info,
    Search,
    Send,
    AlertCircle,
  } from "lucide-svelte";

  // Get manifesto ID from URL
  $: manifestoId = parseInt($page.params.id);

  // State
  let manifesto: any = null;
  let isLoading = true;
  let error = "";
  let commentSortBy = "top";

  // Load manifesto data
  onMount(async () => {
    await loadManifesto();
  });

  async function loadManifesto() {
    try {
      if (!manifestoId) return;
      manifesto = await getManifesto(manifestoId.toString());
    } catch (err: any) {
      console.error(err);
      error = err.message || "Failed to load manifesto";
    } finally {
      isLoading = false;
    }
  }

  function formatDate(dateStr: string) {
    if (!dateStr) return "N/A";
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return "Today";
    if (diffDays === 1) return "Yesterday";
    if (diffDays < 7) return `${diffDays} days ago`;
    return date.toLocaleDateString();
  }
</script>

<svelte:head>
  <title>{manifesto?.title || "Loading..."} - PromiseThread</title>
</svelte:head>

{#if isLoading}
  <main class="manifesto-detail">
    <div class="container">
      <div class="loading-state">
        <div class="spinner"></div>
        <p>Loading manifesto...</p>
      </div>
    </div>
  </main>
{:else if error}
  <main class="manifesto-detail">
    <div class="container">
      <div class="error-state">
        <AlertCircle size={48} />
        <h2>Manifesto Not Found</h2>
        <p>{error}</p>
        <a href="/manifestos" class="btn btn-secondary">← Back to Manifestos</a>
      </div>
    </div>
  </main>
{:else if manifesto}
  <main class="page-wrapper">
    <div class="container container-sm">
      <div class="content-grid">
        <!-- Main Content -->
        <div class="main-content">
          <!-- Manifesto Header -->
          <div class="card p-8 mb-6">
            <div class="flex items-center gap-3 mb-6">
              <span class="font-mono text-sm text-gray-400"
                >#{manifesto.id}</span
              >
              <span
                class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-success-50 text-success-700"
              >
                <CheckCircle size={12} />
                Verified
              </span>
              <span class="text-sm text-gray-400 ml-auto"
                >{manifesto.postedAgo}</span
              >
            </div>

            <h1 class="text-3xl font-bold text-gray-900 mb-6 leading-tight">
              {manifesto.title}
            </h1>

            <p class="text-gray-700 leading-relaxed text-lg mb-8">
              {manifesto.description}
            </p>

            <div class="flex items-center gap-6 pt-6 border-t border-gray-100">
              <div
                class="flex items-center gap-2 text-gray-600 text-sm font-medium"
              >
                <ThumbsUp size={18} class="text-success-500" />
                <span>{manifesto.vote_kept + manifesto.vote_broken} Votes</span>
              </div>
              <div
                class="flex items-center gap-2 text-gray-600 text-sm font-medium"
              >
                <MessageSquare size={18} class="text-primary-500" />
                <span>Discussion</span>
              </div>
              <button
                class="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-gray-200 hover:bg-gray-50 text-gray-600 text-sm font-medium ml-auto transition-colors"
              >
                <Share2 size={16} />
                Share
              </button>
            </div>
          </div>

          <!-- Discussion Section -->
          <CommentThread {manifestoId} />
        </div>

        <!-- Sidebar -->
        <aside class="sidebar space-y-6">
          <!-- Vote Box -->
          <VoteBox
            {manifestoId}
            voteKept={manifesto.vote_kept}
            voteBroken={manifesto.vote_broken}
            isLocked={manifesto.status === "locked"}
            gracePeriodEnd={manifesto.grace_period_end}
          />

          <!-- About Card -->
          <div class="card p-6">
            <div
              class="flex items-center gap-2 mb-4 pb-4 border-b border-gray-100"
            >
              <Info size={18} class="text-gray-400" />
              <h4
                class="font-bold text-gray-900 text-sm uppercase tracking-wider"
              >
                Proposal Details
              </h4>
            </div>

            <div class="mb-6">
              <span
                class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2 block"
                >TIMELINE</span
              >
              <div
                class="inline-flex items-center gap-2 px-3 py-1.5 bg-gray-100 text-gray-700 rounded-lg text-sm font-medium"
              >
                <Clock size={16} />
                {manifesto.grace_period_end
                  ? `Active until ${new Date(manifesto.grace_period_end).toLocaleDateString()}`
                  : "Start Date: " +
                    new Date(manifesto.created_at).toLocaleDateString()}
              </div>
            </div>

            <div>
              <span
                class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3 block"
                >Community Guidelines</span
              >
              <ul class="space-y-3">
                <li class="flex gap-3 text-sm text-gray-600">
                  <Shield
                    size={16}
                    class="text-primary-500 flex-shrink-0 mt-0.5"
                  />
                  <span
                    >All comments are permanent and immutable after 5 minutes.</span
                  >
                </li>
                <li class="flex gap-3 text-sm text-gray-600">
                  <Shield
                    size={16}
                    class="text-primary-500 flex-shrink-0 mt-0.5"
                  />
                  <span>Civil discourse is enforced by community voting.</span>
                </li>
              </ul>
            </div>
          </div>

          <!-- Related Proposals -->
          <div class="card p-6">
            <h4
              class="font-bold text-gray-900 text-sm uppercase tracking-wider mb-4"
            >
              Related Proposals
            </h4>
            <div class="space-y-2">
              <a
                href="/manifestos/4011"
                class="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50 transition-colors group"
              >
                <span class="font-mono text-xs text-gray-400">#4011</span>
                <span
                  class="text-sm text-gray-700 font-medium group-hover:text-primary-700 flex-1 truncate"
                  >Digital ID Implementation</span
                >
                <span
                  class="text-[10px] uppercase font-bold px-2 py-0.5 bg-gray-100 text-gray-500 rounded"
                  >Closed</span
                >
              </a>
              <a
                href="/manifestos/4088"
                class="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50 transition-colors group"
              >
                <span class="font-mono text-xs text-gray-400">#4088</span>
                <span
                  class="text-sm text-gray-700 font-medium group-hover:text-primary-700 flex-1 truncate"
                  >Tax Reform 2024</span
                >
                <span
                  class="text-[10px] uppercase font-bold px-2 py-0.5 bg-success-50 text-success-600 rounded"
                  >Active</span
                >
              </a>
            </div>
          </div>
        </aside>
      </div>
    </div>
  </main>
{/if}

<style>
  .page-wrapper {
    min-height: 100vh;
    background: var(--gray-50);
    padding: var(--space-6) 0;
  }

  .content-grid {
    display: grid;
    gap: var(--space-6);
  }

  @media (min-width: 1024px) {
    .content-grid {
      grid-template-columns: 1fr 340px;
      align-items: start;
    }
  }

  .sidebar {
    display: flex;
    flex-direction: column;
    gap: var(--space-6);
  }
</style>
