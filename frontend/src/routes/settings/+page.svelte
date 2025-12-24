<script lang="ts">
  import Header from '$lib/components/Header.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import { Shield, Bell, Lock, Eye, Trash2, Download, ExternalLink, Moon, Sun, Globe } from 'lucide-svelte';
  
  let darkMode = false;
  let language = 'en';
  let notifications = {
    voteResults: true,
    newManifestos: true,
    discussionReplies: false,
    weeklyDigest: true
  };
  let privacy = {
    showActivity: false,
    showVoteHistory: false
  };
  
  function toggleDarkMode() {
    darkMode = !darkMode;
    // Apply to document
  }
</script>

<svelte:head>
  <title>Settings - PromiseThread</title>
</svelte:head>

<Header variant="citizen" />

<main class="settings-page">
  <div class="container">
    <h1>Settings</h1>
    <p class="subtitle">Manage your account preferences and privacy settings</p>
    
    <div class="settings-grid">
      <!-- Privacy & Security -->
      <section class="settings-section card">
        <div class="section-header">
          <Shield size={20} />
          <h2>Privacy & Security</h2>
        </div>
        
        <div class="setting-item">
          <div class="setting-info">
            <h3>Zero-Knowledge Identity</h3>
            <p>Your identity is protected by ZK-SNARK proofs. No personal data is stored.</p>
          </div>
          <span class="badge success">Protected</span>
        </div>
        
        <div class="setting-item">
          <div class="setting-info">
            <h3>Show Activity Status</h3>
            <p>Allow others to see when you're active on the platform</p>
          </div>
          <label class="toggle">
            <input type="checkbox" bind:checked={privacy.showActivity} />
            <span class="toggle-slider"></span>
          </label>
        </div>
        
        <div class="setting-item">
          <div class="setting-info">
            <h3>Show Vote History</h3>
            <p>Display your voting history on your public profile</p>
          </div>
          <label class="toggle">
            <input type="checkbox" bind:checked={privacy.showVoteHistory} />
            <span class="toggle-slider"></span>
          </label>
        </div>
        
        <div class="setting-item danger">
          <div class="setting-info">
            <h3>Delete Account</h3>
            <p>Permanently remove your account and all associated data</p>
          </div>
          <button class="btn-danger">
            <Trash2 size={16} />
            Delete
          </button>
        </div>
      </section>
      
      <!-- Notifications -->
      <section class="settings-section card">
        <div class="section-header">
          <Bell size={20} />
          <h2>Notifications</h2>
        </div>
        
        <div class="setting-item">
          <div class="setting-info">
            <h3>Vote Results</h3>
            <p>Get notified when voting ends on manifestos you've participated in</p>
          </div>
          <label class="toggle">
            <input type="checkbox" bind:checked={notifications.voteResults} />
            <span class="toggle-slider"></span>
          </label>
        </div>
        
        <div class="setting-item">
          <div class="setting-info">
            <h3>New Manifestos</h3>
            <p>Get notified when politicians you follow post new manifestos</p>
          </div>
          <label class="toggle">
            <input type="checkbox" bind:checked={notifications.newManifestos} />
            <span class="toggle-slider"></span>
          </label>
        </div>
        
        <div class="setting-item">
          <div class="setting-info">
            <h3>Discussion Replies</h3>
            <p>Get notified when someone replies to your comments</p>
          </div>
          <label class="toggle">
            <input type="checkbox" bind:checked={notifications.discussionReplies} />
            <span class="toggle-slider"></span>
          </label>
        </div>
        
        <div class="setting-item">
          <div class="setting-info">
            <h3>Weekly Digest</h3>
            <p>Receive a weekly summary of platform activity</p>
          </div>
          <label class="toggle">
            <input type="checkbox" bind:checked={notifications.weeklyDigest} />
            <span class="toggle-slider"></span>
          </label>
        </div>
      </section>
      
      <!-- Appearance -->
      <section class="settings-section card">
        <div class="section-header">
          <Eye size={20} />
          <h2>Appearance</h2>
        </div>
        
        <div class="setting-item">
          <div class="setting-info">
            <h3>Dark Mode</h3>
            <p>Switch between light and dark themes</p>
          </div>
          <button class="theme-toggle" on:click={toggleDarkMode}>
            {#if darkMode}
              <Moon size={18} />
              Dark
            {:else}
              <Sun size={18} />
              Light
            {/if}
          </button>
        </div>
        
        <div class="setting-item">
          <div class="setting-info">
            <h3>Language</h3>
            <p>Choose your preferred language</p>
          </div>
          <select bind:value={language} class="language-select">
            <option value="en">English</option>
            <option value="es">Español</option>
            <option value="fr">Français</option>
            <option value="de">Deutsch</option>
          </select>
        </div>
      </section>
      
      <!-- Data & Export -->
      <section class="settings-section card">
        <div class="section-header">
          <Download size={20} />
          <h2>Data & Export</h2>
        </div>
        
        <div class="setting-item">
          <div class="setting-info">
            <h3>Export Vote Records</h3>
            <p>Download a cryptographic proof of all your votes</p>
          </div>
          <button class="btn-secondary">
            <Download size={16} />
            Export
          </button>
        </div>
        
        <div class="setting-item">
          <div class="setting-info">
            <h3>Export Discussion History</h3>
            <p>Download all your comments and discussions</p>
          </div>
          <button class="btn-secondary">
            <Download size={16} />
            Export
          </button>
        </div>
        
        <div class="setting-item">
          <div class="setting-info">
            <h3>View on Blockchain</h3>
            <p>View your anonymized on-chain activity</p>
          </div>
          <a href="https://etherscan.io" target="_blank" class="btn-secondary">
            <ExternalLink size={16} />
            View
          </a>
        </div>
      </section>
    </div>
  </div>
</main>

<Footer />

<style>
  .settings-page {
    min-height: 100vh;
    background: var(--gray-50);
    padding-bottom: var(--space-12);
  }
  
  .container {
    max-width: 800px;
    margin: 0 auto;
    padding: var(--space-8) var(--space-4);
  }
  
  h1 {
    font-size: 1.75rem;
    margin-bottom: var(--space-2);
  }
  
  .subtitle {
    color: var(--gray-500);
    margin-bottom: var(--space-8);
  }
  
  .settings-grid {
    display: flex;
    flex-direction: column;
    gap: var(--space-6);
  }
  
  .settings-section {
    padding: var(--space-6);
  }
  
  .section-header {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    margin-bottom: var(--space-5);
    padding-bottom: var(--space-4);
    border-bottom: 1px solid var(--gray-200);
    color: var(--primary-600);
  }
  
  .section-header h2 {
    font-size: 1.1rem;
    color: var(--gray-900);
    margin: 0;
  }
  
  .setting-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-4);
    padding: var(--space-4) 0;
    border-bottom: 1px solid var(--gray-100);
  }
  
  .setting-item:last-child {
    border-bottom: none;
  }
  
  .setting-info {
    flex: 1;
  }
  
  .setting-info h3 {
    font-size: 0.95rem;
    margin-bottom: var(--space-1);
  }
  
  .setting-info p {
    font-size: 0.8rem;
    color: var(--gray-500);
    line-height: 1.4;
  }
  
  .badge {
    padding: var(--space-1) var(--space-3);
    border-radius: var(--radius-full);
    font-size: 0.75rem;
    font-weight: 600;
  }
  
  .badge.success {
    background: var(--success-100);
    color: var(--success-700);
  }
  
  /* Toggle Switch */
  .toggle {
    position: relative;
    display: inline-block;
    width: 48px;
    height: 26px;
    cursor: pointer;
  }
  
  .toggle input {
    opacity: 0;
    width: 0;
    height: 0;
  }
  
  .toggle-slider {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: var(--gray-300);
    border-radius: var(--radius-full);
    transition: 0.3s;
  }
  
  .toggle-slider::before {
    content: '';
    position: absolute;
    left: 3px;
    bottom: 3px;
    width: 20px;
    height: 20px;
    background: white;
    border-radius: 50%;
    transition: 0.3s;
  }
  
  .toggle input:checked + .toggle-slider {
    background: var(--primary-600);
  }
  
  .toggle input:checked + .toggle-slider::before {
    transform: translateX(22px);
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
  }
  
  .btn-danger {
    display: inline-flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-2) var(--space-4);
    border: 1px solid var(--error-300);
    background: var(--error-50);
    color: var(--error-700);
    border-radius: var(--radius-lg);
    font-size: 0.85rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
  }
  
  .btn-danger:hover {
    background: var(--error-100);
    border-color: var(--error-400);
  }
  
  .setting-item.danger {
    padding-top: var(--space-5);
    margin-top: var(--space-3);
    border-top: 1px dashed var(--error-200);
    border-bottom: none;
  }
  
  .theme-toggle {
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
    transition: all 0.2s;
  }
  
  .theme-toggle:hover {
    border-color: var(--primary-500);
  }
  
  .language-select {
    padding: var(--space-2) var(--space-4);
    border: 1px solid var(--gray-300);
    border-radius: var(--radius-lg);
    background: white;
    font-size: 0.85rem;
    color: var(--gray-700);
    cursor: pointer;
  }
  
  .language-select:hover {
    border-color: var(--primary-500);
  }
</style>
