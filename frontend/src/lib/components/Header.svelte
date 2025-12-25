<script lang="ts">
  import { Shield, Users, FileText, Menu, X, LogOut, History } from 'lucide-svelte';
  import { authStore } from '$lib/stores';
  
  export let variant: string = 'default';
  
  let menuOpen = false;
  
  // Reactive auth state
  $: isAuthenticated = $authStore.isAuthenticated;
  $: nullifierShort = $authStore.credential?.nullifierShort || '';
  
  // Logo destination: authenticated users go to citizen portal, others to landing
  $: logoHref = isAuthenticated ? '/citizen' : '/';
  
  function handleLogout() {
    authStore.logout();
    menuOpen = false;
  }
  
  // Navigation items - show Citizen Portal for authenticated users
  $: navItems = isAuthenticated 
    ? [
        { href: '/citizen', label: 'Citizen Portal', icon: Shield },
        { href: '/citizen/votes', label: 'My Votes', icon: History },
        { href: '/manifestos', label: 'Promises', icon: FileText },
        { href: '/politicians', label: 'Politicians', icon: Users },
      ]
    : [
        { href: '/manifestos', label: 'Promises', icon: FileText },
        { href: '/politicians', label: 'Politicians', icon: Users },
      ];
</script>

<header class="header-main {variant}">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex justify-between items-center h-16">
      <!-- Logo -->
      <a href={logoHref} class="flex items-center space-x-2">
        <Shield class="w-8 h-8 text-emerald-400" />
        <span class="text-xl font-bold text-white">PromiseThread</span>
      </a>
      
      <!-- Desktop Navigation -->
      <nav class="hidden md:flex items-center space-x-6">
        {#each navItems as item}
          <a 
            href={item.href} 
            class="flex items-center space-x-1 text-slate-200 hover:text-emerald-400 transition-colors"
          >
            <svelte:component this={item.icon} class="w-4 h-4" />
            <span>{item.label}</span>
          </a>
        {/each}
      </nav>
      
      <!-- Auth Button / User Info -->
      <div class="hidden md:flex items-center space-x-4">
        {#if isAuthenticated}
          <span class="text-sm text-slate-300 font-mono">{nullifierShort}</span>
          <button 
            on:click={handleLogout}
            class="flex items-center space-x-1 text-slate-200 hover:text-red-400 transition-colors"
          >
            <LogOut class="w-4 h-4" />
            <span>Logout</span>
          </button>
        {:else}
          <a href="/auth" class="bg-[var(--success-500)] hover:bg-[var(--success-600)] text-white px-4 py-2 rounded-lg transition-colors font-medium">
            Get Started
          </a>
        {/if}
      </div>
      
      <!-- Mobile Menu Button -->
      <button 
        class="md:hidden text-slate-200"
        on:click={() => menuOpen = !menuOpen}
      >
        {#if menuOpen}
          <X class="w-6 h-6" />
        {:else}
          <Menu class="w-6 h-6" />
        {/if}
      </button>
    </div>
  </div>
  
  <!-- Mobile Menu -->
  {#if menuOpen}
    <div class="md:hidden mobile-menu">
      <div class="px-4 py-3 space-y-2">
        {#each navItems as item}
          <a 
            href={item.href} 
            class="flex items-center space-x-2 text-slate-200 hover:text-emerald-400 py-2"
            on:click={() => menuOpen = false}
          >
            <svelte:component this={item.icon} class="w-5 h-5" />
            <span>{item.label}</span>
          </a>
        {/each}
        {#if isAuthenticated}
          <div class="pt-2 border-t border-slate-700">
            <span class="block text-sm text-slate-400 font-mono py-1">{nullifierShort}</span>
            <button 
              on:click={handleLogout}
              class="flex items-center space-x-2 text-red-400 hover:text-red-300 py-2 w-full"
            >
              <LogOut class="w-5 h-5" />
              <span>Logout</span>
            </button>
          </div>
        {:else}
          <a 
            href="/auth" 
            class="block bg-[var(--success-500)] hover:bg-[var(--success-600)] text-white px-4 py-2 rounded-lg text-center mt-4 font-medium"
            on:click={() => menuOpen = false}
          >
            Get Started
          </a>
        {/if}
      </div>
    </div>
  {/if}
</header>

<style>
  .header-main {
    position: sticky;
    top: 0;
    z-index: 50;
    transition: all 0.3s ease;
  }
  
  .header-main.default,
  .header-main.politician,
  .header-main.citizen {
    background: white;
    border-bottom: 1px solid var(--gray-200);
  }
  
  .header-main.default :global(.text-slate-200),
  .header-main.default :global(.text-white),
  .header-main.politician :global(.text-slate-200),
  .header-main.politician :global(.text-white),
  .header-main.citizen :global(.text-slate-200),
  .header-main.citizen :global(.text-white) {
    color: var(--gray-700) !important;
  }
  
  .header-main.default :global(.text-emerald-400),
  .header-main.politician :global(.text-emerald-400),
  .header-main.citizen :global(.text-emerald-400) {
    color: var(--success-600) !important;
  }
  
  .header-main.default a:hover :global(svg),
  .header-main.default a:hover span,
  .header-main.politician a:hover :global(svg),
  .header-main.politician a:hover span,
  .header-main.citizen a:hover :global(svg),
  .header-main.citizen a:hover span {
    color: var(--success-600) !important;
  }
  
  .header-main.transparent {
    position: fixed;
    width: 100%;
    background: rgba(15, 23, 42, 0.8);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  }
  
  .mobile-menu {
    background: white;
    border-top: 1px solid var(--gray-200);
  }
  
  .header-main.default .mobile-menu,
  .header-main.politician .mobile-menu,
  .header-main.citizen .mobile-menu {
    background: white;
  }
  
  .header-main.default .mobile-menu :global(.text-slate-200),
  .header-main.politician .mobile-menu :global(.text-slate-200),
  .header-main.citizen .mobile-menu :global(.text-slate-200) {
    color: var(--gray-700) !important;
  }
  
  .header-main.transparent .mobile-menu {
    background: #0f172a;
    border-top: 1px solid rgba(255, 255, 255, 0.05);
  }
</style>
