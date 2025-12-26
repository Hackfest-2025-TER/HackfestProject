<script lang="ts">
  import {
    Shield,
    FileText,
    BarChart3,
    LogOut,
    CheckCircle,
    TrendingUp,
    Vote,
    Copy,
    Settings,
    Eye,
    Key,
    AlertCircle,
    Users,
    Plus,
    Download,
    AlertTriangle,
    User,
  } from "lucide-svelte";
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";
  import { authStore, credential } from "$lib/stores";
  import { get } from "svelte/store";
  import HashDisplay from "$lib/components/HashDisplay.svelte";
  import ManifestoCard from "$lib/components/ManifestoCard.svelte";
  import {
    generateRepresentativeWallet,
    getRepresentativeWalletStatus,
  } from "$lib/api";
  import { downloadKeystore } from "$lib/utils/crypto";

  // Representative data - will be loaded from auth and API
  let representative: any = null;

  // Dynamic data from API
  let manifestos: any[] = [];
  let manifesto: any = null;
  let comments: any[] = [];
  let loading = true;
  let error = "";

  let activeNav = "dashboard";

  // Wallet generation state
  let passphrase = "";
  let passphraseConfirm = "";
  let isGeneratingWallet = false;
  let generatedKeystore: any = null;
  let keystoreDownloaded = false;
  let walletError = "";

  onMount(async () => {
    // Check if user is authenticated and is a representative
    const cred = get(credential);
    if (!cred || !cred.isRepresentative) {
      error = "Access denied. Please register as a representative first.";
      setTimeout(() => goto("/representative/register"), 2000);
      return;
    }

    await loadRepresentativeData(cred.representativeId!);
  });

  async function loadRepresentativeData(representativeId: number) {
    try {
      // Load representative profile
      const profileResponse = await fetch(
        `http://localhost:8000/api/representatives/${representativeId}`,
      );
      if (profileResponse.ok) {
        const profileData = await profileResponse.json();
        representative = {
          name: profileData.name,
          id: representativeId,
          slug: profileData.slug,
          party: profileData.party,
          position: profileData.position,
          bio: profileData.bio,
          avatarUrl: profileData.image_url,
          integrityScore: profileData.integrity_score || 98,
          manifestosAudited: profileData.manifesto_count || 0,
          voteParticipation: 95,
          walletAddress: profileData.wallet_address,
          hasWallet: profileData.has_wallet,
        };
      }

      // Load representative's manifestos
      const manifestoResponse = await fetch(
        `http://localhost:8000/api/manifestos?representative_id=${representativeId}`,
      );
      if (manifestoResponse.ok) {
        const data = await manifestoResponse.json();
        manifestos = data.manifestos || [];

        // Get the first manifesto as example
        if (manifestos.length > 0) {
          manifesto = manifestos[0];

          // Load comments for this manifesto
          const commentsResponse = await fetch(
            `http://localhost:8000/api/manifestos/${manifesto.id}/comments`,
          );
          if (commentsResponse.ok) {
            const commentsData = await commentsResponse.json();
            comments = commentsData.comments || [];
          }
        }
      }
    } catch (err) {
      console.error("Failed to load representative data:", err);
      error = "Failed to load dashboard data. Please check your connection.";
    }
    loading = false;
  }

  function handleLogout() {
    authStore.logout();
    goto("/");
  }

  // Wallet generation
  $: passphrasesMatch =
    passphrase === passphraseConfirm && passphrase.length > 0;
  $: canGenerateWallet =
    passphrase.length >= 8 &&
    passphrasesMatch &&
    representative &&
    !representative.hasWallet;

  async function handleGenerateWallet() {
    if (!canGenerateWallet || !representative) return;
    try {
      isGeneratingWallet = true;
      walletError = "";
      const result = await generateRepresentativeWallet(representative.id, passphrase);
      generatedKeystore = result;
      if (generatedKeystore?.keystore) {
        downloadKeystore(
          generatedKeystore.keystore,
          generatedKeystore.keystore_filename ||
            `representative-${representative.id}-key.json`,
        );
        keystoreDownloaded = true;
      }
      // Reload representative data to update hasWallet status
      await loadRepresentativeData(representative.id);
    } catch (e: any) {
      walletError = e.message;
    } finally {
      isGeneratingWallet = false;
    }
  }
</script>

<svelte:head>
  <title>Representative Dashboard - PromiseThread</title>
</svelte:head>

{#if error}
  <div class="min-h-screen bg-gray-50 flex items-center justify-center p-4">
    <div
      class="bg-red-50 border border-red-200 rounded-xl p-8 max-w-md text-center shadow-sm"
    >
      <AlertCircle class="w-12 h-12 text-red-500 mx-auto mb-4" />
      <h2 class="text-xl font-bold text-gray-900 mb-2">Access Denied</h2>
      <p class="text-gray-600">{error}</p>
    </div>
  </div>
{:else if loading || !representative}
  <div class="min-h-screen bg-gray-50 flex items-center justify-center">
    <div class="text-center">
      <div
        class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"
      ></div>
      <p class="text-gray-600 font-medium">Loading dashboard...</p>
    </div>
  </div>
{:else}
  <div class="dashboard-layout">
    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="user-info">
          <div class="avatar">
            {representative.name[0]}
          </div>
          <div class="user-details">
            <span class="user-name">{representative.name}</span>
            <span class="user-id">ID: {representative.id}</span>
          </div>
        </div>
      </div>

      <nav class="sidebar-nav">
        <a
          href="/representative/dashboard"
          class="nav-item"
          class:active={activeNav === "dashboard"}
        >
          <BarChart3 size={18} />
          Dashboard
        </a>
        <a
          href="/representative/manifestos"
          class="nav-item"
          class:active={activeNav === "manifestos"}
        >
          <FileText size={18} />
          Manifestos
        </a>
        <a
          href="/representative/profile"
          class="nav-item"
          class:active={activeNav === "profile"}
        >
          <User size={18} />
          Profile
        </a>
      </nav>

      <div class="sidebar-footer">
        <button class="logout-btn" on:click={handleLogout}>
          <LogOut size={18} />
          Secure Logout
        </button>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="main-content">
      <!-- Header -->
      <header class="content-header">
        <div class="header-left">
          <Shield size={24} />
          <h1>Representative Audit Portal</h1>
        </div>
        <div class="header-right">
          <span class="node-status">
            <span class="status-dot online"></span>
            Active
          </span>
        </div>
      </header>

      <!-- Breadcrumb -->
      <div class="breadcrumb">
        <a href="/representative/dashboard">Dashboard</a>
        <span>/</span>
        <span class="current">{manifesto ? manifesto.title : "Overview"}</span>
      </div>

      <!-- Dashboard Overview Grid -->
      {#if loading}
        <div class="loading-state">Loading...</div>
      {:else}
        <div class="dashboard-grid">
          <!-- Profile Card -->
          <div class="dashboard-card profile-card">
            <div class="card-header">
              <h3>Profile</h3>
              <a href="/representative/profile" class="edit-link">Edit</a>
            </div>
            <div class="profile-info">
              <div class="profile-avatar">{representative?.name?.[0] || "P"}</div>
              <div class="profile-details">
                <h4>{representative?.name || "Representative"}</h4>
                <p class="profile-meta">
                  {representative?.party || "Independent"} • {representative?.position ||
                    "Representative"}
                </p>
              </div>
            </div>
            <div class="profile-stats">
              <div class="profile-stat">
                <span class="stat-num">{manifestos.length}</span>
                <span class="stat-desc">Promises</span>
              </div>
              <div class="profile-stat">
                <span class="stat-num">{representative?.integrityScore || 0}%</span>
                <span class="stat-desc">Integrity</span>
              </div>
            </div>
          </div>

          <!-- Wallet Status Card -->
          <div class="dashboard-card wallet-card">
            <div class="card-header">
              <h3>Wallet & Signing</h3>
            </div>
            {#if representative?.hasWallet}
              <div class="wallet-active">
                <div class="wallet-status-badge">
                  <CheckCircle class="w-5 h-5 text-success-600" />
                  <span class="text-success-700 font-medium">Active</span>
                </div>
                <div class="wallet-address">
                  <span class="text-xs text-gray-500 uppercase">Address</span>
                  <code class="text-sm font-mono text-gray-700 truncate"
                    >{representative?.walletAddress?.slice(0, 20)}...</code
                  >
                </div>
              </div>
            {:else}
              <!-- Inline Wallet Generation -->
              <div class="wallet-setup">
                {#if generatedKeystore}
                  <div
                    class="bg-success-50 border border-success-200 rounded-lg p-4 text-center"
                  >
                    <CheckCircle
                      class="w-6 h-6 text-success-600 mx-auto mb-2"
                    />
                    <p class="text-success-800 font-medium text-sm">
                      Wallet Created!
                    </p>
                  </div>
                {:else}
                  <p class="text-gray-600 text-sm mb-4">
                    Generate a signing key to create promises.
                  </p>
                  <div class="space-y-3">
                    <input
                      type="password"
                      bind:value={passphrase}
                      placeholder="Passphrase (8+ chars)"
                      class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg"
                    />
                    <input
                      type="password"
                      bind:value={passphraseConfirm}
                      placeholder="Confirm passphrase"
                      class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg"
                    />
                    {#if walletError}
                      <p class="text-error-600 text-xs">{walletError}</p>
                    {/if}
                    <button
                      on:click={handleGenerateWallet}
                      disabled={!canGenerateWallet || isGeneratingWallet}
                      class="w-full py-2 bg-primary-600 hover:bg-primary-700 disabled:bg-gray-300 text-white text-sm font-medium rounded-lg flex items-center justify-center gap-2"
                    >
                      <Key class="w-4 h-4" />
                      {isGeneratingWallet ? "Generating..." : "Generate Wallet"}
                    </button>
                  </div>
                {/if}
              </div>
            {/if}
          </div>

          <!-- Quick Actions Card -->
          <div class="dashboard-card actions-card">
            <div class="card-header">
              <h3>Quick Actions</h3>
            </div>
            <div class="quick-actions">
              <a
                href="/representative/new-manifesto"
                class="action-btn primary"
                class:disabled={!representative?.hasWallet}
              >
                <Plus class="w-5 h-5" />
                <span>New Promise</span>
              </a>
              <a href="/representative/manifestos" class="action-btn secondary">
                <FileText class="w-5 h-5" />
                <span>All Promises</span>
              </a>
            </div>
          </div>

          <!-- Manifestos List Card (spans full width) -->
          <div class="dashboard-card manifestos-card">
            <div class="card-header">
              <h3>Recent Promises</h3>
              <a href="/representative/manifestos" class="view-all-link"
                >View All →</a
              >
            </div>
            {#if manifestos.length > 0}
              <div class="manifestos-list">
                {#each manifestos.slice(0, 5) as m}
                  <a href="/manifestos/{m.id}" class="manifesto-row">
                    <div class="manifesto-info">
                      <span class="manifesto-title">{m.title}</span>
                      <span class="manifesto-date"
                        >{m.created_at
                          ? new Date(m.created_at).toLocaleDateString()
                          : "N/A"}</span
                      >
                    </div>
                    <div class="manifesto-stats">
                      <span class="manifesto-status {m.status}">{m.status}</span
                      >
                      <span class="manifesto-votes"
                        >{(m.vote_kept || 0) + (m.vote_broken || 0)} votes</span
                      >
                    </div>
                  </a>
                {/each}
              </div>
            {:else}
              <div class="empty-manifestos">
                <FileText class="w-10 h-10 text-gray-300 mx-auto mb-2" />
                <p class="text-gray-500 text-sm">No promises yet.</p>
                {#if representative?.hasWallet}
                  <a
                    href="/representative/new-manifesto"
                    class="text-primary-600 text-sm font-medium mt-2 inline-block"
                    >Create your first promise →</a
                  >
                {/if}
              </div>
            {/if}
          </div>
        </div>
      {/if}

      <!-- Comments Section -->
      {#if manifesto}
        <div class="comments-section">
          <div class="comments-header">
            <div class="comments-title">
              <h3>Citizen Comments</h3>
              <span class="comment-count">{comments.length}</span>
            </div>
            <div class="comments-controls">
              <div class="search-box">
                <input type="text" placeholder="Search comments..." />
              </div>
              <button class="sort-btn"> ≡ Newest First </button>
            </div>
          </div>

          <div class="comments-list">
            {#if comments.length > 0}
              {#each comments as comment}
                <div class="comment-item">
                  <div class="comment-avatar">
                    <Users size={20} />
                  </div>
                  <div class="comment-content">
                    <div class="comment-header">
                      <span class="author">Verified Citizen</span>
                      <span class="citizen-id"
                        >{comment.nullifier || "Anonymous"}</span
                      >
                      <span class="date"
                        >{comment.created_at
                          ? new Date(comment.created_at).toLocaleString()
                          : "N/A"}</span
                      >
                    </div>
                    <p class="comment-text">{comment.content}</p>
                    <div class="comment-stats">
                      <span class="upvotes">👍 {comment.upvotes || 0}</span>
                      <span class="downvotes">👎 {comment.downvotes || 0}</span>
                    </div>
                  </div>
                  <button class="copy-btn" title="Copy">
                    <Copy size={14} />
                  </button>
                </div>
              {/each}
            {:else}
              <div class="empty-comments">No comments yet</div>
            {/if}
          </div>
        </div>
      {/if}
    </main>
  </div>

  <style>
    .dashboard-layout {
      display: flex;
      min-height: 100vh;
      background: var(--gray-50);
    }

    /* Sidebar */
    .sidebar {
      width: 260px;
      background: white;
      border-right: 1px solid var(--gray-200);
      display: flex;
      flex-direction: column;
      position: sticky;
      top: 0;
      height: 100vh;
    }

    .sidebar-header {
      padding: var(--space-6);
      border-bottom: 1px solid var(--gray-200);
    }

    .user-info {
      display: flex;
      align-items: center;
      gap: var(--space-3);
    }

    .avatar {
      width: 48px;
      height: 48px;
      border-radius: 50%;
      background: var(--primary-100);
      color: var(--primary-700);
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 600;
      font-size: 1.25rem;
    }

    .user-details {
      display: flex;
      flex-direction: column;
    }

    .user-name {
      font-weight: 600;
      color: var(--gray-900);
    }

    .user-id {
      font-size: 0.75rem;
      font-family: var(--font-mono);
      color: var(--gray-500);
    }

    .sidebar-nav {
      flex: 1;
      padding: var(--space-4);
      display: flex;
      flex-direction: column;
      gap: var(--space-1);
    }

    .nav-item {
      display: flex;
      align-items: center;
      gap: var(--space-3);
      padding: var(--space-3) var(--space-4);
      color: var(--gray-600);
      text-decoration: none;
      border-radius: var(--radius-lg);
      font-size: 0.875rem;
      font-weight: 500;
      transition: all 0.2s;
    }

    .nav-item:hover {
      background: var(--gray-100);
      color: var(--gray-900);
    }

    .nav-item.active {
      background: var(--primary-50);
      color: var(--primary-700);
    }

    .sidebar-footer {
      padding: var(--space-4);
      border-top: 1px solid var(--gray-200);
    }

    .logout-btn {
      display: flex;
      align-items: center;
      gap: var(--space-2);
      width: 100%;
      padding: var(--space-3);
      border: none;
      background: transparent;
      color: var(--gray-500);
      font-size: 0.875rem;
      cursor: pointer;
      border-radius: var(--radius-lg);
    }

    .logout-btn:hover {
      background: var(--gray-100);
      color: var(--gray-700);
    }

    /* Main Content */
    .main-content {
      flex: 1;
      padding: var(--space-6);
      overflow-y: auto;
    }

    .content-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: var(--space-4);
    }

    .header-left {
      display: flex;
      align-items: center;
      gap: var(--space-3);
    }

    .header-left h1 {
      font-size: 1.25rem;
    }

    .header-right {
      display: flex;
      align-items: center;
      gap: var(--space-4);
    }

    .node-status {
      display: flex;
      align-items: center;
      gap: var(--space-2);
      padding: var(--space-2) var(--space-3);
      background: var(--gray-100);
      border-radius: var(--radius-full);
      font-size: 0.8rem;
      color: var(--gray-600);
    }

    .status-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
    }

    .status-dot.online {
      background: var(--success-500);
    }

    .icon-btn {
      width: 40px;
      height: 40px;
      border: 1px solid var(--gray-200);
      background: white;
      border-radius: var(--radius-lg);
      cursor: pointer;
    }

    /* Breadcrumb */
    .breadcrumb {
      display: flex;
      align-items: center;
      gap: var(--space-2);
      font-size: 0.875rem;
      margin-bottom: var(--space-6);
    }

    .breadcrumb a {
      color: var(--gray-500);
      text-decoration: none;
    }

    .breadcrumb a:hover {
      color: var(--primary-600);
    }

    .breadcrumb span {
      color: var(--gray-400);
    }

    .breadcrumb .current {
      color: var(--gray-900);
      font-weight: 500;
    }

    /* Manifesto Detail */
    .manifesto-detail {
      background: white;
      border: 1px solid var(--gray-200);
      border-radius: var(--radius-xl);
      padding: var(--space-6);
      margin-bottom: var(--space-6);
    }

    .detail-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: var(--space-4);
    }

    .status-row {
      display: flex;
      align-items: center;
      gap: var(--space-3);
    }

    .status-badge {
      padding: var(--space-1) var(--space-2);
      font-size: 0.7rem;
      font-weight: 600;
      border-radius: var(--radius-sm);
    }

    .status-badge.active {
      background: var(--success-100);
      color: var(--success-700);
    }

    .manifesto-id {
      font-size: 0.8rem;
      color: var(--gray-500);
      font-family: var(--font-mono);
    }

    .view-doc {
      font-size: 0.875rem;
      color: var(--primary-600);
      text-decoration: none;
    }

    .manifesto-detail h2 {
      font-size: 1.5rem;
      margin-bottom: var(--space-3);
    }

    .description {
      color: var(--gray-600);
      line-height: 1.6;
      margin-bottom: var(--space-6);
    }

    .meta-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: var(--space-4);
      padding-top: var(--space-4);
      border-top: 1px solid var(--gray-200);
    }

    .meta-item {
      display: flex;
      flex-direction: column;
      gap: var(--space-1);
    }

    .meta-label {
      font-size: 0.65rem;
      font-weight: 600;
      color: var(--gray-400);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .meta-value {
      font-size: 0.875rem;
      color: var(--gray-900);
      font-weight: 500;
    }

    /* Comments Section */
    .comments-section {
      background: white;
      border: 1px solid var(--gray-200);
      border-radius: var(--radius-xl);
      overflow: hidden;
    }

    .comments-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: var(--space-4) var(--space-6);
      border-bottom: 1px solid var(--gray-200);
      flex-wrap: wrap;
      gap: var(--space-3);
    }

    .comments-title {
      display: flex;
      align-items: center;
      gap: var(--space-2);
    }

    .comments-title h3 {
      font-size: 1rem;
    }

    .comment-count {
      padding: var(--space-1) var(--space-2);
      background: var(--gray-100);
      border-radius: var(--radius-full);
      font-size: 0.75rem;
      color: var(--gray-600);
    }

    .comments-controls {
      display: flex;
      gap: var(--space-3);
    }

    .search-box input {
      padding: var(--space-2) var(--space-3);
      border: 1px solid var(--gray-200);
      border-radius: var(--radius-lg);
      font-size: 0.8rem;
      width: 200px;
    }

    .sort-btn {
      padding: var(--space-2) var(--space-3);
      border: 1px solid var(--gray-200);
      background: white;
      border-radius: var(--radius-lg);
      font-size: 0.8rem;
      color: var(--gray-600);
      cursor: pointer;
    }

    .comments-list {
      max-height: 500px;
      overflow-y: auto;
    }

    .comment-item {
      display: flex;
      gap: var(--space-4);
      padding: var(--space-5) var(--space-6);
      border-bottom: 1px solid var(--gray-100);
    }

    .comment-avatar {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      background: var(--gray-100);
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--gray-500);
      flex-shrink: 0;
    }

    .comment-content {
      flex: 1;
    }

    .comment-header {
      display: flex;
      align-items: center;
      gap: var(--space-2);
      margin-bottom: var(--space-2);
      flex-wrap: wrap;
    }

    .author {
      font-weight: 600;
      color: var(--gray-900);
    }

    .date {
      font-size: 0.75rem;
      color: var(--gray-400);
    }

    .comment-text {
      font-size: 0.875rem;
      color: var(--gray-700);
      line-height: 1.6;
      margin-bottom: var(--space-3);
    }

    .evidence {
      display: flex;
      align-items: center;
      gap: var(--space-2);
      font-size: 0.75rem;
    }

    .evidence-label {
      color: var(--gray-400);
    }

    .evidence-link {
      color: var(--success-600);
      font-family: var(--font-mono);
    }

    .copy-btn {
      width: 36px;
      height: 36px;
      border: none;
      background: transparent;
      cursor: pointer;
      border-radius: var(--radius-md);
      opacity: 0.5;
    }

    .copy-btn:hover {
      background: var(--gray-100);
      opacity: 1;
    }

    /* Dashboard Grid Layout */
    .dashboard-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: var(--space-6);
    }

    .dashboard-card {
      background: white;
      border: 1px solid var(--gray-200);
      border-radius: var(--radius-xl);
      padding: var(--space-5);
      box-shadow: var(--shadow-sm);
    }

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: var(--space-4);
    }

    .card-header h3 {
      font-size: 0.9rem;
      font-weight: 700;
      color: var(--gray-900);
      margin: 0;
    }

    .edit-link,
    .view-all-link {
      font-size: 0.8rem;
      color: var(--primary-600);
      text-decoration: none;
      font-weight: 500;
    }

    .edit-link:hover,
    .view-all-link:hover {
      text-decoration: underline;
    }

    /* Profile Card */
    .profile-info {
      display: flex;
      align-items: center;
      gap: var(--space-3);
      margin-bottom: var(--space-4);
    }

    .profile-avatar {
      width: 48px;
      height: 48px;
      border-radius: 50%;
      background: var(--primary-100);
      color: var(--primary-700);
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      font-size: 1.25rem;
    }

    .profile-details h4 {
      font-size: 1rem;
      font-weight: 600;
      color: var(--gray-900);
      margin: 0 0 2px 0;
    }

    .profile-meta {
      font-size: 0.8rem;
      color: var(--gray-500);
      margin: 0;
    }

    .profile-stats {
      display: flex;
      gap: var(--space-6);
      padding-top: var(--space-3);
      border-top: 1px solid var(--gray-100);
    }

    .profile-stat {
      display: flex;
      flex-direction: column;
    }

    .stat-num {
      font-size: 1.25rem;
      font-weight: 700;
      color: var(--gray-900);
    }

    .stat-desc {
      font-size: 0.75rem;
      color: var(--gray-500);
    }

    /* Wallet Card */
    .wallet-active {
      display: flex;
      flex-direction: column;
      gap: var(--space-3);
    }

    .wallet-status-badge {
      display: flex;
      align-items: center;
      gap: var(--space-2);
    }

    .wallet-address {
      display: flex;
      flex-direction: column;
      gap: 2px;
    }

    /* Quick Actions */
    .quick-actions {
      display: flex;
      flex-direction: column;
      gap: var(--space-3);
    }

    .action-btn {
      display: flex;
      align-items: center;
      gap: var(--space-2);
      padding: var(--space-3);
      border-radius: var(--radius-lg);
      text-decoration: none;
      font-weight: 500;
      font-size: 0.9rem;
      transition: all 0.2s;
    }

    .action-btn.primary {
      background: var(--primary-600);
      color: white;
    }

    .action-btn.primary:hover {
      background: var(--primary-700);
    }

    .action-btn.primary.disabled {
      background: var(--gray-300);
      pointer-events: none;
    }

    .action-btn.secondary {
      background: var(--gray-50);
      color: var(--gray-700);
      border: 1px solid var(--gray-200);
    }

    .action-btn.secondary:hover {
      background: var(--gray-100);
    }

    /* Manifestos Card */
    .manifestos-card {
      grid-column: span 3;
    }

    .manifestos-list {
      display: flex;
      flex-direction: column;
    }

    .manifesto-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: var(--space-3) 0;
      border-bottom: 1px solid var(--gray-100);
      text-decoration: none;
      transition: background 0.2s;
    }

    .manifesto-row:last-child {
      border-bottom: none;
    }

    .manifesto-row:hover {
      background: var(--gray-50);
      margin: 0 calc(-1 * var(--space-3));
      padding-left: var(--space-3);
      padding-right: var(--space-3);
      border-radius: var(--radius-md);
    }

    .manifesto-info {
      display: flex;
      flex-direction: column;
      gap: 2px;
    }

    .manifesto-title {
      font-weight: 500;
      color: var(--gray-900);
      font-size: 0.9rem;
    }

    .manifesto-date {
      font-size: 0.75rem;
      color: var(--gray-500);
    }

    .manifesto-stats {
      display: flex;
      align-items: center;
      gap: var(--space-3);
    }

    .manifesto-status {
      font-size: 0.7rem;
      font-weight: 600;
      text-transform: uppercase;
      padding: 2px 8px;
      border-radius: var(--radius-full);
    }

    .manifesto-status.pending {
      background: var(--warning-100);
      color: var(--warning-700);
    }

    .manifesto-status.kept {
      background: var(--success-100);
      color: var(--success-700);
    }

    .manifesto-status.broken {
      background: var(--error-100);
      color: var(--error-700);
    }

    .manifesto-votes {
      font-size: 0.8rem;
      color: var(--gray-500);
    }

    .empty-manifestos {
      text-align: center;
      padding: var(--space-6);
    }

    @media (max-width: 1024px) {
      .dashboard-grid {
        grid-template-columns: 1fr;
      }
      .manifestos-card {
        grid-column: span 1;
      }
    }
  </style>
{/if}
