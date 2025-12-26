<script lang="ts">
  import {
    Shield,
    FileText,
    BarChart3,
    LogOut,
    CheckCircle,
    Key,
    AlertCircle,
    Users,
    Copy,
    Plus,
    Upload,
    Lock,
    Loader,
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
    submitSignedManifesto,
    rotateKey,
  } from "$lib/api";
  import {
    downloadKeystore,
    computeSHA256,
    parseKeystore,
    decryptKeystore,
    signMessage,
  } from "$lib/utils/crypto";

  // Representative data - will be loaded from auth and API
  let representative: any = null;

  // Dynamic data from API
  let manifestos: any[] = [];
  let manifesto: any = null;
  let comments: any[] = [];
  let loading = true;
  let error = "";

  let activeNav = "dashboard";

  // Wallet generation/rotation state
  let passphrase = "";
  let passphraseConfirm = "";
  let isGeneratingWallet = false;
  let generatedKeystore: any = null;
  let keystoreDownloaded = false;
  let walletError = "";

  // Rotation specific
  let showRotationForm = false;
  let rotationReason = "lost_key"; // lost_key, compromised, scheduled
  let rotationReasonText = ""; // For custom reason if needed, or mapping logic

  // New Promise form state
  let showNewPromiseForm = false;
  let newPromiseTitle = "";
  let newPromiseDescription = "";
  let keystoreFile: File | null = null;
  let keystoreData: any = null;
  let signingPassphrase = "";
  let isSubmittingPromise = false;
  let promiseSubmitError = "";
  let promiseSubmitSuccess = false;

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
      const result = await generateRepresentativeWallet(
        representative.id,
        passphrase,
      );
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

  async function handleRotateKey() {
    if (!passphrasesMatch || !passphrase || !representative) return;

    try {
      isGeneratingWallet = true; // Reusing loading state
      walletError = "";

      // Default admin token for hackfest
      const ADMIN_TOKEN = "hackfest2025_admin";

      const result = await rotateKey(
        representative.id,
        "User initiated reset: " + rotationReason,
        passphrase,
        ADMIN_TOKEN,
      );

      generatedKeystore = result;
      if (generatedKeystore?.keystore) {
        downloadKeystore(
          generatedKeystore.keystore,
          generatedKeystore.keystore_filename ||
            `representative-${representative.id}-key-v${generatedKeystore.key_version}.json`,
        );
        keystoreDownloaded = true;
      }

      // Reload representative data
      await loadRepresentativeData(representative.id);

      // Reset form state but keep success message
      showRotationForm = false;
    } catch (e: any) {
      walletError = e.message;
    } finally {
      isGeneratingWallet = false;
    }
  }

  // New Promise form handlers
  async function handleKeystoreUpload(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      keystoreFile = input.files[0];
      try {
        const text = await keystoreFile.text();
        keystoreData = parseKeystore(text);
        if (!keystoreData) {
          promiseSubmitError = "Invalid keystore file format";
        }
      } catch (e) {
        promiseSubmitError = "Failed to read keystore file";
      }
    }
  }

  async function handleSubmitPromise() {
    if (!newPromiseTitle || !newPromiseDescription) {
      promiseSubmitError = "Please fill in title and description";
      return;
    }
    if (!keystoreData || !signingPassphrase) {
      promiseSubmitError = "Please upload keystore and enter passphrase";
      return;
    }

    promiseSubmitError = "";
    isSubmittingPromise = true;

    try {
      // Compute hash from description
      const hash = await computeSHA256(newPromiseDescription);
      const manifestoHash = hash.startsWith("0x") ? hash : "0x" + hash;

      // Decrypt keystore and sign
      const privateKey = await decryptKeystore(keystoreData, signingPassphrase);
      if (!privateKey) {
        throw new Error("Failed to decrypt keystore. Check your passphrase.");
      }

      // Sign the hash
      const hashForSigning = manifestoHash.startsWith("0x")
        ? manifestoHash.slice(2)
        : manifestoHash;
      const signature = await signMessage(
        hashForSigning,
        privateKey,
        representative?.walletAddress,
      );

      // Submit to backend
      const result = await submitSignedManifesto({
        representative_id: representative.id,
        title: newPromiseTitle,
        description: newPromiseDescription,
        category: "general",
        grace_period_days: 7,
        manifesto_hash: manifestoHash,
        signature: signature,
      });

      if (result.manifesto_id || result.success) {
        promiseSubmitSuccess = true;
        // Reset form and reload data
        newPromiseTitle = "";
        newPromiseDescription = "";
        keystoreFile = null;
        keystoreData = null;
        signingPassphrase = "";
        showNewPromiseForm = false;
        await loadRepresentativeData(representative.id);
        setTimeout(() => {
          promiseSubmitSuccess = false;
        }, 3000);
      } else {
        throw new Error(result.error || "Submission failed");
      }
    } catch (e: any) {
      promiseSubmitError = e.message || "Failed to sign and submit promise";
    } finally {
      isSubmittingPromise = false;
    }
  }
</script>

<svelte:head>
  <title>Representative Dashboard - WaachaPatra</title>
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
        <a href="/representative/dashboard" class="nav-item active">
          <BarChart3 size={18} />
          Dashboard
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
            </div>
            <div class="profile-info">
              <div class="profile-avatar">
                {representative?.name?.[0] || "P"}
              </div>
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
                <span class="stat-num"
                  >{representative?.integrityScore || 0}%</span
                >
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

                {#if !showRotationForm}
                  <button
                    class="reset-link"
                    on:click={() => (showRotationForm = true)}
                  >
                    Reset Wallet / Rotate Key
                  </button>
                {:else}
                  <div class="rotation-form">
                    <h4>Reset Wallet</h4>
                    <p class="text-xs text-gray-500 mb-3">
                      This will revoke your current key and generate a new one.
                      Old manifestos remain valid.
                    </p>

                    <div class="space-y-3">
                      <select
                        bind:value={rotationReason}
                        class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg bg-white"
                      >
                        <option value="lost_key"
                          >I lost my key/passphrase</option
                        >
                        <option value="compromised"
                          >My key was compromised</option
                        >
                        <option value="scheduled"
                          >Scheduled security rotation</option
                        >
                      </select>

                      <input
                        type="password"
                        bind:value={passphrase}
                        placeholder="New Passphrase (8+ chars)"
                        class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg"
                      />
                      <input
                        type="password"
                        bind:value={passphraseConfirm}
                        placeholder="Confirm new passphrase"
                        class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg"
                      />

                      {#if walletError}
                        <p class="text-error-600 text-xs">{walletError}</p>
                      {/if}

                      <div class="flex gap-2">
                        <button
                          class="flex-1 py-2 text-sm text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200"
                          on:click={() => {
                            showRotationForm = false;
                            walletError = "";
                          }}
                        >
                          Cancel
                        </button>
                        <button
                          class="flex-1 py-2 text-sm text-white bg-error-600 rounded-lg hover:bg-error-700 disabled:bg-gray-300"
                          disabled={!passphrasesMatch ||
                            passphrase.length < 8 ||
                            isGeneratingWallet}
                          on:click={handleRotateKey}
                        >
                          {isGeneratingWallet ? "Rotating..." : "Confirm Reset"}
                        </button>
                      </div>
                    </div>
                  </div>
                {/if}
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

          <!-- Create New Promise Card (spans full width) -->
          {#if representative?.hasWallet}
            <div class="dashboard-card new-promise-card">
              <div class="card-header">
                <h3>Create New Promise</h3>
                {#if !showNewPromiseForm}
                  <button
                    class="show-form-btn"
                    on:click={() => (showNewPromiseForm = true)}
                  >
                    <Plus class="w-4 h-4" />
                    New
                  </button>
                {:else}
                  <button
                    class="show-form-btn secondary"
                    on:click={() => {
                      showNewPromiseForm = false;
                      promiseSubmitError = "";
                    }}
                  >
                    Cancel
                  </button>
                {/if}
              </div>

              {#if promiseSubmitSuccess}
                <div
                  class="bg-success-50 border border-success-200 rounded-lg p-4 text-center"
                >
                  <CheckCircle class="w-6 h-6 text-success-600 mx-auto mb-2" />
                  <p class="text-success-800 font-medium text-sm">
                    Promise created successfully!
                  </p>
                </div>
              {:else if showNewPromiseForm}
                <div class="new-promise-form">
                  <div class="form-group">
                    <label class="form-label">Promise Title</label>
                    <input
                      type="text"
                      bind:value={newPromiseTitle}
                      placeholder="e.g., Improve Rural Healthcare"
                      class="form-input"
                    />
                  </div>

                  <div class="form-group">
                    <label class="form-label">Description</label>
                    <textarea
                      bind:value={newPromiseDescription}
                      placeholder="Describe your commitment and how it will be measured..."
                      rows="4"
                      class="form-textarea"
                    ></textarea>
                  </div>

                  <div class="signing-section">
                    <h4><Key class="w-4 h-4" /> Digital Signature</h4>

                    <div class="form-group">
                      <label class="form-label">Upload Keystore</label>
                      <label class="keystore-upload">
                        <input
                          type="file"
                          accept=".json"
                          on:change={handleKeystoreUpload}
                        />
                        <Upload class="w-4 h-4" />
                        <span
                          >{keystoreFile
                            ? keystoreFile.name
                            : "Select keystore.json"}</span
                        >
                      </label>
                    </div>

                    {#if keystoreData}
                      <div class="form-group">
                        <label class="form-label">Passphrase</label>
                        <div class="passphrase-input">
                          <Lock class="w-4 h-4" />
                          <input
                            type="password"
                            bind:value={signingPassphrase}
                            placeholder="Enter your wallet passphrase"
                          />
                        </div>
                      </div>
                    {/if}
                  </div>

                  {#if promiseSubmitError}
                    <div class="error-message">
                      <AlertCircle class="w-4 h-4" />
                      {promiseSubmitError}
                    </div>
                  {/if}

                  <button
                    class="submit-btn"
                    on:click={handleSubmitPromise}
                    disabled={isSubmittingPromise ||
                      !keystoreData ||
                      !signingPassphrase}
                  >
                    {#if isSubmittingPromise}
                      <Loader class="w-4 h-4 animate-spin" />
                      Signing & Submitting...
                    {:else}
                      <Shield class="w-4 h-4" />
                      Sign & Create Promise
                    {/if}
                  </button>
                </div>
              {:else}
                <p class="text-gray-500 text-sm">
                  Click "New" to create a new promise.
                </p>
              {/if}
            </div>
          {/if}

          <!-- Manifestos List Card (spans full width) -->
          <div class="dashboard-card manifestos-card">
            <div class="card-header">
              <h3>My Promises</h3>
              <span class="promise-count">{manifestos.length} total</span>
            </div>
            {#if manifestos.length > 0}
              <div class="manifestos-list">
                {#each manifestos as m}
                  <div class="manifesto-row">
                    <div class="manifesto-info">
                      <span class="manifesto-title">{m.title}</span>
                      <span class="manifesto-date"
                        >{m.created_at
                          ? new Date(m.created_at).toLocaleDateString()
                          : "N/A"}</span
                      >
                    </div>
                    <div class="manifesto-stats">
                      <span class="manifesto-status {m.status || 'pending'}"
                        >{m.status || "pending"}</span
                      >
                      <span class="manifesto-votes"
                        >{(m.vote_kept || 0) + (m.vote_broken || 0)} votes</span
                      >
                    </div>
                  </div>
                {/each}
              </div>
            {:else}
              <div class="empty-manifestos">
                <FileText class="w-10 h-10 text-gray-300 mx-auto mb-2" />
                <p class="text-gray-500 text-sm">No promises yet.</p>
                <p class="text-gray-400 text-xs mt-1">
                  Generate a wallet first to create promises.
                </p>
              </div>
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
      grid-template-columns: repeat(2, 1fr);
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

    .promise-count {
      font-size: 0.75rem;
      color: var(--gray-500);
      font-weight: 500;
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

    .reset-link {
      font-size: 0.75rem;
      color: var(--error-600);
      background: none;
      border: none;
      padding: 0;
      cursor: pointer;
      text-decoration: underline;
      margin-top: var(--space-1);
      text-align: left;
    }

    .reset-link:hover {
      color: var(--error-700);
    }

    .rotation-form {
      margin-top: var(--space-3);
      padding-top: var(--space-3);
      border-top: 1px solid var(--gray-200);
    }

    .rotation-form h4 {
      font-size: 0.85rem;
      font-weight: 600;
      color: var(--error-700);
      margin: 0 0 var(--space-1) 0;
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
      grid-column: span 2;
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

    /* New Promise Card */
    .new-promise-card {
      grid-column: span 2;
    }

    .show-form-btn {
      display: flex;
      align-items: center;
      gap: var(--space-1);
      padding: var(--space-2) var(--space-3);
      border: none;
      background: var(--primary-600);
      color: white;
      border-radius: var(--radius-lg);
      font-size: 0.8rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
    }

    .show-form-btn:hover {
      background: var(--primary-700);
    }

    .show-form-btn.secondary {
      background: var(--gray-200);
      color: var(--gray-700);
    }

    .show-form-btn.secondary:hover {
      background: var(--gray-300);
    }

    .new-promise-form {
      display: flex;
      flex-direction: column;
      gap: var(--space-4);
    }

    .new-promise-form .form-group {
      display: flex;
      flex-direction: column;
      gap: var(--space-2);
    }

    .new-promise-form .form-label {
      font-size: 0.8rem;
      font-weight: 600;
      color: var(--gray-700);
    }

    .new-promise-form .form-input {
      padding: var(--space-3);
      border: 1px solid var(--gray-300);
      border-radius: var(--radius-lg);
      font-size: 0.9rem;
    }

    .new-promise-form .form-input:focus {
      outline: none;
      border-color: var(--primary-500);
      box-shadow: 0 0 0 2px var(--primary-100);
    }

    .new-promise-form .form-textarea {
      padding: var(--space-3);
      border: 1px solid var(--gray-300);
      border-radius: var(--radius-lg);
      font-size: 0.9rem;
      resize: vertical;
      font-family: inherit;
    }

    .new-promise-form .form-textarea:focus {
      outline: none;
      border-color: var(--primary-500);
      box-shadow: 0 0 0 2px var(--primary-100);
    }

    .new-promise-form .signing-section {
      padding: var(--space-4);
      background: var(--gray-50);
      border-radius: var(--radius-lg);
    }

    .new-promise-form .signing-section h4 {
      display: flex;
      align-items: center;
      gap: var(--space-2);
      font-size: 0.9rem;
      font-weight: 600;
      margin-bottom: var(--space-3);
      color: var(--gray-800);
    }

    .keystore-upload {
      display: flex;
      align-items: center;
      gap: var(--space-2);
      padding: var(--space-3);
      border: 2px dashed var(--gray-300);
      border-radius: var(--radius-lg);
      cursor: pointer;
      color: var(--gray-600);
      font-size: 0.85rem;
      transition: all 0.2s;
    }

    .keystore-upload:hover {
      border-color: var(--primary-400);
      background: var(--primary-50);
    }

    .keystore-upload input[type="file"] {
      display: none;
    }

    .passphrase-input {
      display: flex;
      align-items: center;
      gap: var(--space-2);
      padding: var(--space-3);
      border: 1px solid var(--gray-300);
      border-radius: var(--radius-lg);
      background: white;
    }

    .passphrase-input input {
      flex: 1;
      border: none;
      outline: none;
      font-size: 0.9rem;
    }

    .error-message {
      display: flex;
      align-items: center;
      gap: var(--space-2);
      padding: var(--space-3);
      background: var(--error-50);
      color: var(--error-700);
      border-radius: var(--radius-lg);
      font-size: 0.85rem;
    }

    .submit-btn {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: var(--space-2);
      padding: var(--space-3);
      border: none;
      background: var(--success-600);
      color: white;
      border-radius: var(--radius-lg);
      font-size: 0.9rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
    }

    .submit-btn:hover:not(:disabled) {
      background: var(--success-700);
    }

    .submit-btn:disabled {
      background: var(--gray-300);
      cursor: not-allowed;
    }

    @media (max-width: 1024px) {
      .dashboard-grid {
        grid-template-columns: 1fr;
      }
      .manifestos-card,
      .new-promise-card {
        grid-column: span 1;
      }
    }
  </style>
{/if}
