<script lang="ts">
  import Header from '$lib/components/Header.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import { Shield, User, Mail, Lock, Eye, Info, ChevronRight } from 'lucide-svelte';
  
  let activeTab: 'login' | 'register' = 'register';
  let userRole: 'citizen' | 'politician' = 'citizen';
  let email = '';
  let password = '';
  let confirmPassword = '';
  let isLoading = false;
  
  const sessionId = '8F4A-9C2B';
  
  async function handleSubmit() {
    isLoading = true;
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500));
    isLoading = false;
    // Navigate to appropriate dashboard
    window.location.href = userRole === 'citizen' ? '/manifestos' : '/politician/dashboard';
  }
</script>

<svelte:head>
  <title>Login - PromiseThread</title>
</svelte:head>

<div class="auth-page">
  <header class="auth-header">
    <a href="/" class="logo">
      <div class="logo-icon">
        <Shield size={20} />
      </div>
      <div class="logo-text">
        <span class="logo-title">Election Trust</span>
        <span class="logo-subtitle">OFFICIAL PORTAL</span>
      </div>
    </a>
    
    <div class="header-right">
      <a href="/help" class="help-link">Help Center</a>
      <span class="divider">|</span>
      <span class="status">
        <span class="status-dot online"></span>
        SYSTEM_ONLINE
      </span>
    </div>
  </header>
  
  <div class="auth-decoration"></div>
  
  <main class="auth-main">
    <div class="auth-card card">
      <div class="auth-card-header">
        <h1>User Access Portal</h1>
        <p>Login to manage your profile or register a new identity on the ledger.</p>
      </div>
      
      <div class="tab-switcher">
        <button 
          class="tab-btn" 
          class:active={activeTab === 'login'}
          on:click={() => activeTab = 'login'}
        >
          Login
        </button>
        <button 
          class="tab-btn" 
          class:active={activeTab === 'register'}
          on:click={() => activeTab = 'register'}
        >
          Register
        </button>
      </div>
      
      <form on:submit|preventDefault={handleSubmit}>
        {#if activeTab === 'register'}
          <div class="role-selector">
            <span class="role-label">SELECT USER ROLE</span>
            <div class="role-options">
              <label class="role-option" class:selected={userRole === 'citizen'}>
                <input type="radio" bind:group={userRole} value="citizen" />
                <div class="role-content">
                  <div class="role-header">
                    <span class="role-title">Citizen</span>
                    <div class="role-check" class:checked={userRole === 'citizen'}></div>
                  </div>
                  <span class="role-desc">Vote & audit public ledgers.</span>
                </div>
              </label>
              
              <label class="role-option" class:selected={userRole === 'politician'}>
                <input type="radio" bind:group={userRole} value="politician" />
                <div class="role-content">
                  <div class="role-header">
                    <span class="role-title">Politician</span>
                    <div class="role-check" class:checked={userRole === 'politician'}></div>
                  </div>
                  <span class="role-desc">Publish manifestos & campaigns.</span>
                </div>
              </label>
            </div>
          </div>
        {/if}
        
        <div class="form-group">
          <label class="form-label">Email or Username</label>
          <div class="input-wrapper">
            <User size={18} />
            <input 
              type="email" 
              class="form-input" 
              placeholder="Enter your email or username"
              bind:value={email}
              required
            />
          </div>
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Password</label>
            <div class="input-wrapper">
              <Lock size={18} />
              <input 
                type="password" 
                class="form-input" 
                placeholder="Create password"
                bind:value={password}
                required
              />
            </div>
          </div>
          
          {#if activeTab === 'register'}
            <div class="form-group">
              <label class="form-label">Confirm Password</label>
              <div class="input-wrapper">
                <Eye size={18} />
                <input 
                  type="password" 
                  class="form-input" 
                  placeholder="Repeat password"
                  bind:value={confirmPassword}
                  required
                />
              </div>
            </div>
          {/if}
        </div>
        
        {#if activeTab === 'register'}
          <div class="info-banner">
            <Info size={18} />
            <p>
              Registration creates a cryptographic keypair. Your actions on the 
              platform will be signed and publicly verifiable on the audit log.
            </p>
          </div>
        {/if}
        
        <button type="submit" class="submit-btn" disabled={isLoading}>
          {#if isLoading}
            <span class="spinner"></span>
            Processing...
          {:else}
            {activeTab === 'login' ? 'Login' : 'Complete Registration'}
            <ChevronRight size={18} />
          {/if}
        </button>
      </form>
      
      <div class="auth-footer">
        <span class="session-id">SESSION: {sessionId}</span>
        <div class="footer-links">
          <a href="/privacy">Privacy</a>
          <span>•</span>
          <a href="/terms">Terms</a>
        </div>
      </div>
    </div>
  </main>
  
  <footer class="auth-page-footer">
    <p>© 2024 Election Trust Authority. Verified Government Service.</p>
  </footer>
</div>

<style>
  .auth-page {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    background: var(--gray-50);
  }
  
  .auth-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-4) var(--space-6);
    background: white;
    border-bottom: 1px solid var(--gray-200);
  }
  
  .logo {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    text-decoration: none;
    color: inherit;
  }
  
  .logo-icon {
    width: 40px;
    height: 40px;
    background: var(--primary-600);
    color: white;
    border-radius: var(--radius-lg);
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .logo-text {
    display: flex;
    flex-direction: column;
  }
  
  .logo-title {
    font-weight: 600;
    font-size: 1rem;
  }
  
  .logo-subtitle {
    font-size: 0.65rem;
    color: var(--gray-500);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  
  .header-right {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    font-size: 0.875rem;
  }
  
  .help-link {
    color: var(--gray-600);
    text-decoration: none;
  }
  
  .help-link:hover {
    color: var(--primary-600);
  }
  
  .divider {
    color: var(--gray-300);
  }
  
  .status {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    font-family: var(--font-mono);
    font-size: 0.75rem;
    color: var(--success-600);
  }
  
  .status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
  }
  
  .status-dot.online {
    background: var(--success-500);
  }
  
  .auth-decoration {
    height: 120px;
    background: linear-gradient(135deg, var(--primary-100) 0%, var(--gray-100) 100%);
    position: relative;
  }
  
  .auth-main {
    flex: 1;
    display: flex;
    justify-content: center;
    padding: 0 var(--space-4);
    margin-top: -60px;
    position: relative;
    z-index: 10;
  }
  
  .auth-card {
    width: 100%;
    max-width: 500px;
    padding: var(--space-8);
    margin-bottom: var(--space-8);
  }
  
  .auth-card-header {
    text-align: center;
    margin-bottom: var(--space-6);
  }
  
  .auth-card-header h1 {
    font-size: 1.5rem;
    margin-bottom: var(--space-2);
  }
  
  .auth-card-header p {
    color: var(--gray-500);
    font-size: 0.875rem;
  }
  
  .tab-switcher {
    display: grid;
    grid-template-columns: 1fr 1fr;
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-lg);
    overflow: hidden;
    margin-bottom: var(--space-6);
  }
  
  .tab-btn {
    padding: var(--space-3);
    border: none;
    background: white;
    font-weight: 500;
    color: var(--gray-600);
    cursor: pointer;
    transition: all 0.2s;
  }
  
  .tab-btn.active {
    background: var(--gray-100);
    color: var(--gray-900);
  }
  
  .role-selector {
    margin-bottom: var(--space-6);
  }
  
  .role-label {
    display: block;
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--gray-500);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: var(--space-3);
  }
  
  .role-options {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--space-3);
  }
  
  .role-option {
    border: 2px solid var(--gray-200);
    border-radius: var(--radius-lg);
    padding: var(--space-4);
    cursor: pointer;
    transition: all 0.2s;
  }
  
  .role-option:hover {
    border-color: var(--primary-300);
  }
  
  .role-option.selected {
    border-color: var(--primary-500);
    background: var(--primary-50);
  }
  
  .role-option input {
    display: none;
  }
  
  .role-content {
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
  }
  
  .role-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  
  .role-title {
    font-weight: 600;
    color: var(--gray-900);
  }
  
  .role-check {
    width: 18px;
    height: 18px;
    border: 2px solid var(--gray-300);
    border-radius: 50%;
    transition: all 0.2s;
  }
  
  .role-check.checked {
    border-color: var(--primary-500);
    background: var(--primary-500);
    position: relative;
  }
  
  .role-check.checked::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 6px;
    height: 6px;
    background: white;
    border-radius: 50%;
  }
  
  .role-desc {
    font-size: 0.75rem;
    color: var(--gray-500);
  }
  
  .form-group {
    margin-bottom: var(--space-4);
  }
  
  .form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--space-4);
  }
  
  .form-label {
    display: block;
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--gray-700);
    margin-bottom: var(--space-2);
  }
  
  .input-wrapper {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    border: 1px solid var(--gray-300);
    border-radius: var(--radius-lg);
    padding: 0 var(--space-3);
    background: white;
    transition: all 0.2s;
  }
  
  .input-wrapper:focus-within {
    border-color: var(--primary-500);
    box-shadow: 0 0 0 3px var(--primary-100);
  }
  
  .input-wrapper :global(svg) {
    color: var(--gray-400);
    flex-shrink: 0;
  }
  
  .form-input {
    flex: 1;
    padding: var(--space-3) 0;
    border: none;
    background: transparent;
    font-size: 0.875rem;
    outline: none;
  }
  
  .info-banner {
    display: flex;
    gap: var(--space-3);
    padding: var(--space-4);
    background: var(--primary-50);
    border-radius: var(--radius-lg);
    margin-bottom: var(--space-6);
  }
  
  .info-banner :global(svg) {
    color: var(--primary-600);
    flex-shrink: 0;
  }
  
  .info-banner p {
    font-size: 0.8rem;
    color: var(--gray-600);
    line-height: 1.5;
  }
  
  .submit-btn {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--space-2);
    padding: var(--space-4);
    background: var(--primary-600);
    color: white;
    border: none;
    border-radius: var(--radius-lg);
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }
  
  .submit-btn:hover:not(:disabled) {
    background: var(--primary-700);
  }
  
  .submit-btn:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }
  
  .spinner {
    width: 18px;
    height: 18px;
    border: 2px solid white;
    border-top-color: transparent;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }
  
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
  
  .auth-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: var(--space-6);
    padding-top: var(--space-4);
    border-top: 1px solid var(--gray-200);
    font-size: 0.75rem;
  }
  
  .session-id {
    font-family: var(--font-mono);
    color: var(--gray-400);
  }
  
  .footer-links {
    display: flex;
    gap: var(--space-2);
    color: var(--gray-400);
  }
  
  .footer-links a {
    color: var(--gray-500);
  }
  
  .auth-page-footer {
    text-align: center;
    padding: var(--space-4);
    font-size: 0.75rem;
    color: var(--gray-500);
  }
</style>
