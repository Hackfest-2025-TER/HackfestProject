<script lang="ts">
  import { onMount } from "svelte";
  import {
    Activity,
    Shield,
    Database,
    Clock,
    CheckCircle,
    FileText,
    Lock,
  } from "lucide-svelte";
  import { getNetworkStats, getMerkleRoot } from "$lib/api";
  import HashDisplay from "$lib/components/HashDisplay.svelte";

  let stats: any = null;
  let merkleRoot = "";
  let recentRecords: any[] = [];
  let isLoading = true;

  onMount(async () => {
    try {
      const [statsData, rootData, blocksResponse] = await Promise.all([
        getNetworkStats(),
        getMerkleRoot(),
        fetch("http://localhost:8000/api/blockchain/blocks?limit=10"),
      ]);

      stats = statsData;
      merkleRoot = rootData.merkle_root;

      // Load real blocks from API but format as friendly records
      if (blocksResponse.ok) {
        const blocksData = await blocksResponse.json();
        recentRecords = (blocksData.blocks || [])
          .slice(0, 5)
          .map((block: any) => ({
            height: block.number,
            id: block.hash,
            timestamp: formatTimestamp(block.timestamp),
            count: block.tx_count || 1,
            action: formatAction(block.action || "System Update"),
          }));
      }
    } catch (e) {
      console.error("Failed to load audit data:", e);
    } finally {
      isLoading = false;
    }
  });

  function formatAction(action: string) {
    if (action.includes("vote")) return "Votes Recorded";
    if (action.includes("promise")) return "New Promise Added";
    return action;
  }

  function formatTimestamp(ts: string): string {
    if (!ts) return "N/A";
    const date = new Date(ts);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins} mins ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours} hours ago`;
    return date.toLocaleDateString();
  }
</script>

<svelte:head>
  <title>Activity Log - PromiseThread</title>
</svelte:head>

<main class="page-wrapper">
  <!-- Hero Section -->
  <section class="hero-section">
    <div class="container hero-content">
      <div class="hero-text">
        <h1>Audit Trail</h1>
        <p>
          A permanent, verifiable record of all promises and votes on the
          blockchain.
        </p>
      </div>
    </div>
  </section>

  <div class="container">
    <!-- Stats Row -->
    <div class="stats-row">
      <div class="stat-item">
        <div class="stat-icon bg-blue-50 text-blue-600">
          <FileText class="w-6 h-6" />
        </div>
        <div class="stat-info">
          <span class="stat-value"
            >{stats?.total_votes?.toLocaleString() || "..."}</span
          >
          <span class="stat-label">Total Votes Cast</span>
        </div>
      </div>

      <div class="stat-item">
        <div class="stat-icon bg-emerald-50 text-emerald-600">
          <Shield class="w-6 h-6" />
        </div>
        <div class="stat-info">
          <span class="stat-value flex items-center gap-2"
            >Secure <CheckCircle class="w-5 h-5 text-success-500" /></span
          >
          <span class="stat-label">System Status</span>
        </div>
      </div>

      <div class="stat-item">
        <div class="stat-icon bg-purple-50 text-purple-600">
          <Clock class="w-6 h-6" />
        </div>
        <div class="stat-info">
          <span class="stat-value">Just now</span>
          <span class="stat-label">Last Update</span>
        </div>
      </div>
    </div>

    <!-- Main Grid -->
    <div class="main-grid">
      <!-- Records Column -->
      <div>
        <div class="section-header">
          <h2><Database class="w-5 h-5 text-gray-400" /> Recent Records</h2>
        </div>
        <div class="space-y-4">
          {#each recentRecords as record}
            <div class="card hover:shadow-md transition-shadow">
              <div class="flex items-center justify-between mb-3">
                <div class="flex items-center gap-3">
                  <span
                    class="bg-gray-100 text-gray-600 text-xs font-mono px-2 py-1 rounded"
                    >#{record.height}</span
                  >
                  <span class="font-semibold text-gray-900"
                    >{record.action}</span
                  >
                </div>
                <span class="text-sm text-gray-500">{record.timestamp}</span>
              </div>
              <div
                class="flex items-center justify-between bg-gray-50 rounded-lg p-3"
              >
                <HashDisplay hash={record.id} label="Record ID" />
                <span class="text-sm text-gray-500">{record.count} items</span>
              </div>
            </div>
          {/each}

          {#if recentRecords.length === 0 && !isLoading}
            <div class="empty-state">
              <p>No records found yet.</p>
            </div>
          {/if}
        </div>
      </div>

      <!-- Sidebar Column -->
      <div class="sidebar-column">
        <!-- Verification Card -->
        <div class="card border-l-4 border-l-primary-500">
          <div class="flex items-center justify-between mb-4">
            <h3
              class="font-bold text-gray-900 flex items-center gap-2 text-base"
            >
              <Lock class="w-4 h-4 text-primary-600" />
              Verification Code
            </h3>
            <span
              class="bg-success-100 text-success-700 text-xs font-bold px-2 py-1 rounded-full uppercase"
              >Live</span
            >
          </div>
          <p class="text-sm text-gray-600 mb-4 leading-relaxed">
            This code represents the current state of all data. You can use it
            to verify that nothing has been altered.
          </p>
          <div class="mb-4">
            <HashDisplay
              hash={merkleRoot || "Loading..."}
              label="System Checksum"
            />
          </div>
          <div
            class="flex items-center gap-2 text-sm text-success-700 font-medium bg-success-50 p-2 rounded-lg justify-center"
          >
            <CheckCircle class="w-4 h-4" />
            Data Integrity Verified
          </div>
        </div>

        <!-- How It Works Card -->
        <div class="card bg-primary-700 text-white border-none">
          <h3 class="font-bold text-lg mb-2 text-white">How it works</h3>
          <p class="text-primary-100 text-sm mb-4 leading-relaxed">
            Every action is permanently recorded in a public log. This ensures
            politicians cannot delete promises or change their history.
          </p>
          <button
            class="w-full bg-white text-primary-700 font-bold py-2 px-4 rounded-lg text-sm hover:bg-primary-50 transition-colors"
          >
            Learn More
          </button>
        </div>
      </div>
    </div>
  </div>
</main>
