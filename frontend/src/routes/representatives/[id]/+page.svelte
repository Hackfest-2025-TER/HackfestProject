<script lang="ts">
  import { onMount } from "svelte";
  import ProgressRing from "$lib/components/ProgressRing.svelte";
  import {
    Shield,
    Award,
    FileText,
    Calendar,
    ExternalLink,
    CheckCircle,
    XCircle,
    Clock,
    ChevronRight,
    Share2,
  } from "lucide-svelte";
  import { page } from "$app/stores";

  $: id = $page.params.id;

  let politician: any = null;
  let loading = true;
  let error = "";

  $: stats = politician
    ? {
        kept: politician.manifestos.filter((m: any) => m.status === "kept")
          .length,
        broken: politician.manifestos.filter((m: any) => m.status === "broken")
          .length,
        pending: politician.manifestos.filter(
          (m: any) => m.status === "pending",
        ).length,
      }
    : { kept: 0, broken: 0, pending: 0 };

  onMount(async () => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/politicians/${id}`,
      );
      if (!response.ok) throw new Error("Politician not found");
      const data = await response.json();
      politician = data;
      loading = false;
    } catch (err: any) {
      error = err.message || "Failed to load politician data";
      loading = false;
    }
  });

  function getStatusBadge(status: string) {
    switch (status) {
      case "kept":
        return { icon: CheckCircle, class: "success", label: "Kept" };
      case "broken":
        return { icon: XCircle, class: "error", label: "Broken" };
      default:
        return { icon: Clock, class: "warning", label: "Pending" };
    }
  }

  function formatDate(dateStr: string) {
    if (!dateStr) return "N/A";
    const date = new Date(dateStr);
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
    });
  }

  function handleImageError(event: Event) {
    const img = event.target as HTMLImageElement;
    img.style.display = "none";
  }
</script>

<svelte:head>
  <title>{politician?.name || "Loading..."} - PromiseThread</title>
</svelte:head>

{#if loading}
  <main class="politician-profile">
    <div class="container">
      <div class="loading-state">Loading politician profile...</div>
    </div>
  </main>
{:else if error}
  <main class="politician-profile">
    <div class="container">
      <div class="error-state">
        <h2>Politician Not Found</h2>
        <p>{error}</p>
        <a href="/representatives" class="btn-secondary">← Back to Politicians</a>
      </div>
    </div>
  </main>
{:else if politician}
  <main class="politician-profile">
    <div class="container">
      <!-- Back Navigation -->
      <a href="/representatives" class="back-link"> ← Back to Representatives </a>

      <!-- Profile Header -->
      <div class="profile-header card">
        <div class="profile-top">
          <div class="profile-avatar-section">
            {#if politician.image_url}
              <img
                src={politician.image_url}
                alt={politician.name}
                class="avatar-img"
                on:error={handleImageError}
              />
            {/if}
            <div
              class="avatar"
              style={politician.image_url ? "display: none;" : ""}
            >
              {politician.name
                .split(" ")
                .map((n) => n[0])
                .join("")}
            </div>
          </div>

          <div class="profile-info">
            <div class="name-row">
              <h1>{politician.name}</h1>
              {#if politician.verified}
                <span class="verified-badge">
                  <Shield size={16} />
                  Verified
                </span>
              {/if}
            </div>
            <p class="title">{politician.title}</p>
            <p class="party">{politician.party}</p>
          </div>
        </div>

        <!-- Stats Summary - Integrated into header -->
        <div class="stats-row">
          <div class="stat-item">
            <div class="stat-icon success">
              <CheckCircle size={18} />
            </div>
            <div class="stat-info">
              <span class="stat-value">{stats.kept}</span>
              <span class="stat-label">Kept</span>
            </div>
          </div>
          <div class="stat-item">
            <div class="stat-icon error">
              <XCircle size={18} />
            </div>
            <div class="stat-info">
              <span class="stat-value">{stats.broken}</span>
              <span class="stat-label">Broken</span>
            </div>
          </div>
          <div class="stat-item">
            <div class="stat-icon warning">
              <Clock size={18} />
            </div>
            <div class="stat-info">
              <span class="stat-value">{stats.pending}</span>
              <span class="stat-label">Pending</span>
            </div>
          </div>
          <div class="stat-item score-item">
            <div class="integrity-display">
              <div class="integrity-number">{politician.integrity_score}%</div>
              <div class="integrity-label">Integrity</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Manifestos List -->
      <div class="manifestos-section">
        <div class="section-header">
          <h2>Promise Records</h2>
          <span class="count-badge">{politician.manifestos.length} total</span>
        </div>

        {#if politician.manifestos.length > 0}
          <div class="manifestos-list">
            {#each politician.manifestos as manifesto}
              {@const badge = getStatusBadge(manifesto.status)}
              <a href="/manifestos/{manifesto.id}" class="manifesto-item card">
                <div class="manifesto-main">
                  <div class="status-icon {badge.class}">
                    <svelte:component this={badge.icon} size={20} />
                  </div>
                  <div class="manifesto-info">
                    <h3>{manifesto.title}</h3>
                    <div class="manifesto-meta">
                      <span class="deadline">
                        <Calendar size={12} />
                        {formatDate(manifesto.deadline)}
                      </span>
                      {#if manifesto.category}
                        <span class="category">{manifesto.category}</span>
                      {/if}
                    </div>
                  </div>
                </div>
                <div class="manifesto-status">
                  <span class="status-badge {badge.class}">{badge.label}</span>
                  <ChevronRight size={18} />
                </div>
              </a>
            {/each}
          </div>
        {:else}
          <div class="empty-state card">
            <FileText size={40} />
            <p>No promises recorded yet</p>
          </div>
        {/if}
      </div>
    </div>
  </main>
{/if}

<style>
  .politician-profile {
    min-height: 100vh;
    background: var(--gray-50);
    padding-bottom: var(--space-16);
  }

  .container {
    max-width: 800px;
    margin: 0 auto;
    padding: var(--space-6) var(--space-4);
  }

  .back-link {
    display: inline-flex;
    align-items: center;
    color: var(--gray-600);
    font-size: 0.875rem;
    margin-bottom: var(--space-6);
    text-decoration: none;
    transition: color 0.2s;
  }

  .back-link:hover {
    color: var(--primary-600);
    text-decoration: none;
  }

  /* Profile Header */
  .profile-header {
    padding: var(--space-8);
    margin-bottom: var(--space-8);
  }

  .profile-top {
    display: flex;
    gap: var(--space-6);
    align-items: center;
    margin-bottom: var(--space-6);
  }

  .profile-avatar-section {
    flex-shrink: 0;
  }

  .avatar {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--primary-100), var(--primary-200));
    color: var(--primary-700);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2.25rem;
    font-weight: 600;
  }

  .avatar-img {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    object-fit: cover;
    border: 3px solid white;
    box-shadow: var(--shadow-md);
  }

  .loading-state,
  .error-state {
    text-align: center;
    padding: var(--space-16) var(--space-4);
    color: var(--gray-600);
  }

  .error-state h2 {
    color: var(--error-600);
    margin-bottom: var(--space-4);
  }

  .empty-state {
    text-align: center;
    padding: var(--space-12);
    color: var(--gray-500);
  }

  .empty-state :global(svg) {
    margin-bottom: var(--space-4);
    opacity: 0.4;
  }

  .profile-info {
    flex: 1;
  }

  .name-row {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    flex-wrap: wrap;
    margin-bottom: var(--space-2);
  }

  .name-row h1 {
    font-size: 1.75rem;
    margin: 0;
    color: var(--gray-900);
    font-weight: 700;
  }

  .verified-badge {
    display: inline-flex;
    align-items: center;
    gap: var(--space-1);
    padding: var(--space-1) var(--space-3);
    background: var(--success-100);
    color: var(--success-700);
    border-radius: var(--radius-full);
    font-size: 0.75rem;
    font-weight: 600;
  }

  .title {
    color: var(--gray-700);
    font-size: 1rem;
    margin-bottom: var(--space-1);
    font-weight: 500;
  }

  .party {
    color: var(--gray-500);
    font-size: 0.9rem;
    margin: 0;
  }

  /* Stats Row */
  .stats-row {
    display: flex;
    gap: var(--space-4);
    padding-top: var(--space-6);
    border-top: 1px solid var(--gray-100);
    flex-wrap: wrap;
  }

  .stat-item {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-3) var(--space-4);
    background: var(--gray-50);
    border-radius: var(--radius-lg);
    flex: 1;
    min-width: 120px;
  }

  .stat-item.score-item {
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: var(--space-2);
  }

  .integrity-display {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: var(--space-1);
  }

  .integrity-number {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--success-600);
    line-height: 1;
  }

  .integrity-label {
    font-size: 0.75rem;
    color: var(--gray-500);
    text-transform: uppercase;
    letter-spacing: 0.02em;
    font-weight: 600;
  }

  .stat-icon {
    width: 36px;
    height: 36px;
    border-radius: var(--radius-md);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  .stat-icon.success {
    background: var(--success-100);
    color: var(--success-600);
  }

  .stat-icon.error {
    background: var(--error-100);
    color: var(--error-600);
  }

  .stat-icon.warning {
    background: var(--warning-100);
    color: var(--warning-600);
  }

  .stat-info {
    display: flex;
    flex-direction: column;
  }

  .stat-info .stat-value {
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--gray-900);
    line-height: 1.2;
  }

  .stat-info .stat-label,
  .stat-item .stat-label {
    font-size: 0.75rem;
    color: var(--gray-500);
    text-transform: uppercase;
    letter-spacing: 0.02em;
  }

  .btn-secondary {
    display: inline-flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-2) var(--space-4);
    border: 1px solid var(--gray-300);
    background: white;
    color: var(--gray-700);
    border-radius: var(--radius-lg);
    font-size: 0.85rem;
    font-weight: 500;
    cursor: pointer;
    text-decoration: none;
    transition: all 0.2s;
  }

  .btn-secondary:hover {
    border-color: var(--primary-500);
    color: var(--primary-600);
    text-decoration: none;
  }

  /* Manifestos Section */
  .manifestos-section {
    margin-top: var(--space-2);
  }

  .section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--space-5);
  }

  .section-header h2 {
    font-size: 1.25rem;
    color: var(--gray-900);
    margin: 0;
  }

  .count-badge {
    font-size: 0.8rem;
    color: var(--gray-500);
    background: var(--gray-100);
    padding: var(--space-1) var(--space-3);
    border-radius: var(--radius-full);
  }

  .manifestos-list {
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
  }

  .manifesto-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-5);
    text-decoration: none;
    color: inherit;
    transition: all 0.2s;
  }

  .manifesto-item:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-2px);
    text-decoration: none;
  }

  .manifesto-main {
    display: flex;
    align-items: center;
    gap: var(--space-4);
    flex: 1;
    min-width: 0;
  }

  .status-icon {
    width: 44px;
    height: 44px;
    border-radius: var(--radius-lg);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  .status-icon.success {
    background: var(--success-100);
    color: var(--success-600);
  }

  .status-icon.error {
    background: var(--error-100);
    color: var(--error-600);
  }

  .status-icon.warning {
    background: var(--warning-100);
    color: var(--warning-600);
  }

  .manifesto-info {
    flex: 1;
    min-width: 0;
  }

  .manifesto-info h3 {
    font-size: 1rem;
    margin-bottom: var(--space-2);
    color: var(--gray-900);
    font-weight: 600;
  }

  .manifesto-meta {
    display: flex;
    gap: var(--space-4);
    font-size: 0.8rem;
    color: var(--gray-500);
  }

  .manifesto-meta .deadline {
    display: flex;
    align-items: center;
    gap: var(--space-1);
  }

  .manifesto-meta .category {
    background: var(--gray-100);
    padding: 2px var(--space-2);
    border-radius: var(--radius-sm);
  }

  .manifesto-status {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    color: var(--gray-400);
    flex-shrink: 0;
  }

  .status-badge {
    padding: var(--space-1) var(--space-3);
    border-radius: var(--radius-full);
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.02em;
  }

  .status-badge.success {
    background: var(--success-100);
    color: var(--success-700);
  }

  .status-badge.error {
    background: var(--error-100);
    color: var(--error-700);
  }

  .status-badge.warning {
    background: var(--warning-100);
    color: var(--warning-700);
  }

  /* Responsive */
  @media (max-width: 640px) {
    .profile-top {
      flex-direction: column;
      align-items: flex-start;
      text-align: left;
    }

    .stats-row {
      flex-direction: column;
    }

    .stat-item {
      min-width: 100%;
    }

    .stat-item.score {
      flex-direction: row;
      justify-content: center;
    }

    .manifesto-item {
      flex-direction: column;
      align-items: flex-start;
      gap: var(--space-4);
    }

    .manifesto-status {
      align-self: flex-end;
    }
  }
</style>
