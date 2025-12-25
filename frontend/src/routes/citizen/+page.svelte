<script lang="ts">
  import { browser } from "$app/environment";
  import ManifestoCard from "$lib/components/ManifestoCard.svelte";
  import HashDisplay from "$lib/components/HashDisplay.svelte";
  import {
    Shield,
    FileText,
    CheckCircle,
    Clock,
    Activity,
    TrendingUp,
    Eye,
    AlertCircle,
    Fingerprint,
    MessageCircle,
    Users,
    Info,
    ChevronRight,
  } from "lucide-svelte";
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";
  import { authStore, isAuthenticated, credential } from "$lib/stores";
  import { getManifestos } from "$lib/api";

  // Reactive auth state
  $: isAuth = $isAuthenticated;
  $: userCredential = $credential;

  // Data
  let manifestos: any[] = [];
  let isLoading = true;

  // Load data without auth requirement
  onMount(async () => {
    if (!browser) return;

    try {
      const data = await getManifestos();
      manifestos = data.manifestos?.slice(0, 4) || [];
    } catch (e) {
      console.error("Failed to load manifestos:", e);
    }
    isLoading = false;
  });

  // Activity based on voted manifestos (or show demo data if not authenticated)
  $: recentActivity = isAuth
    ? (userCredential?.usedVotes || []).slice(-3).map((id) => ({
        type: "vote",
        description: `Shared opinion on promise ${id}`,
        time: "Recently",
        icon: CheckCircle,
      }))
    : [];
</script>

<svelte:head>
  <title>Citizen Overview - PromiseThread</title>
</svelte:head>

<main class="citizen-page">
  <!-- Hero Section -->
  <section class="hero-section">
    <div class="container hero-content">
      <div class="hero-text">
        <h1>
          Your Voice. Your Power.<br /><span class="text-primary-400"
            >Completely Anonymous.</span
          >
        </h1>
        <p class="text-lg opacity-90 max-w-2xl">
          Hold politicians accountable without compromising your privacy. Every
          vote is verified on the blockchain, yet your identity remains hidden.
        </p>
      </div>

      {#if !isAuth}
        <div class="hero-actions">
          <a
            href="/auth"
            class="btn btn-primary btn-lg shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all"
          >
            <Shield class="w-5 h-5 mr-2" />
            Verify Identity
          </a>
          <a
            href="/manifestos"
            class="btn btn-white btn-lg opacity-90 hover:opacity-100"
          >
            Browse Promises
          </a>
        </div>
      {:else}
        <!-- Authenticated users see a simpler hero since nav is in header -->
        <div class="hero-actions">
          <div
            class="bg-success-50 border border-success-200 px-6 py-3 rounded-full inline-flex items-center gap-3"
          >
            <Shield class="w-5 h-5 text-success-600" />
            <span class="text-success-800 font-medium">Verified Citizen</span>
            <span class="text-success-600 font-mono text-sm"
              >{userCredential?.nullifierShort || "Active"}</span
            >
          </div>
        </div>
      {/if}
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
          <span class="stat-label">Promises Tracked</span>
        </div>
      </div>

      <div class="stat-item">
        <div class="stat-icon bg-emerald-50 text-emerald-600">
          <MessageCircle class="w-6 h-6" />
        </div>
        <div class="stat-info">
          <span class="stat-value"
            >{isAuth ? userCredential?.usedVotes?.length || 0 : "-"}</span
          >
          <span class="stat-label">Contributions</span>
        </div>
      </div>

      <div class="stat-item">
        <div class="stat-icon bg-purple-50 text-purple-600">
          <Activity class="w-6 h-6" />
        </div>
        <div class="stat-info">
          <span class="stat-value">Active</span>
          <span class="stat-label">System Status</span>
        </div>
      </div>
    </div>

    <div class="main-grid">
      <!-- Left Column: Featured Content -->
      <div class="feed-column">
        <div class="section-header">
          <h2>
            <TrendingUp class="w-5 h-5 text-primary-600" />
            Suggested for Review
          </h2>
          <a href="/manifestos" class="view-all">View All</a>
        </div>

        {#if isLoading}
          <div class="loading-state">
            <div class="spinner"></div>
            <p>Loading promises...</p>
          </div>
        {:else if manifestos.length === 0}
          <div class="empty-state">
            <p>No promises found.</p>
          </div>
        {:else}
          <div class="manifesto-grid">
            {#each manifestos as manifesto}
              <ManifestoCard {manifesto} />
            {/each}
          </div>
        {/if}
      </div>

      <!-- Right Column: Sidebar -->
      <aside class="sidebar-column">
        <!-- Quick Actions -->
        <div class="sidebar-card">
          <h3>Quick Actions</h3>
          <div class="quick-links">
            <a href="/manifestos" class="quick-link">
              <div class="link-icon">
                <FileText class="w-4 h-4" />
              </div>
              <span>Browse Promises</span>
              <ChevronRight class="w-4 h-4 ml-auto text-gray-400" />
            </a>
            <a href="/representatives" class="quick-link">
              <div class="link-icon">
                <Users class="w-4 h-4" />
              </div>
              <span>Find Representatives</span>
              <ChevronRight class="w-4 h-4 ml-auto text-gray-400" />
            </a>
            <a href="/verify" class="quick-link">
              <div class="link-icon">
                <Shield class="w-4 h-4" />
              </div>
              <span>Verify Record</span>
              <ChevronRight class="w-4 h-4 ml-auto text-gray-400" />
            </a>
          </div>
        </div>

        <!-- Recent Activity -->
        {#if isAuth}
          <div class="sidebar-card">
            <h3>Recent Activity</h3>
            {#if recentActivity.length === 0}
              <p class="empty-text">No recent activity.</p>
            {:else}
              <div class="activity-params">
                {#each recentActivity as activity}
                  <div class="activity-row">
                    <div class="dot"></div>
                    <div class="act-content">
                      <p>{activity.description}</p>
                      <small>{activity.time}</small>
                    </div>
                  </div>
                {/each}
              </div>
            {/if}
          </div>
        {:else}
          <!-- Promo Card for Unauth -->
          <div class="sidebar-card promo">
            <div class="promo-icon">
              <Shield class="w-8 h-8" />
            </div>
            <h3>Participation is Anonymous</h3>
            <p>
              We use Zero-Knowledge Proofs to ensure your vote counts without
              revealing your identity.
            </p>
            <a href="/auth" class="btn btn-outline btn-sm w-full">Learn More</a>
          </div>
        {/if}
      </aside>
    </div>
  </div>
</main>
```

<style>
</style>
