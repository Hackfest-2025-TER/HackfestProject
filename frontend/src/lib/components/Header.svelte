<script lang="ts">
  import { Shield, Vote, Users, FileText, Activity, Settings, Menu, X, HelpCircle } from 'lucide-svelte';
  
  export let variant: string = 'default';
  
  let menuOpen = false;
  
  const navItems = [
    { href: '/', label: 'Home', icon: Shield },
    { href: '/manifestos', label: 'Promises', icon: FileText },
    { href: '/politicians', label: 'Politicians', icon: Users },
    { href: '/citizen', label: 'Citizen Portal', icon: Vote },
    { href: '/audit-trail', label: 'Audit Trail', icon: Activity },
    { href: '/guide', label: 'Guide', icon: HelpCircle },
  ];
</script>

<header class="header-main">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex justify-between items-center h-16">
      <!-- Logo -->
      <a href="/" class="flex items-center space-x-2">
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
      
      <!-- Auth Button -->
      <div class="hidden md:flex items-center space-x-4">
        <a href="/auth" class="bg-emerald-500 hover:bg-emerald-600 text-white px-4 py-2 rounded-lg transition-colors font-medium">
          Verify as Citizen
        </a>
        <a href="/settings" class="text-slate-300 hover:text-white transition-colors">
          <Settings class="w-5 h-5" />
        </a>
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
        <a 
          href="/auth" 
          class="block bg-emerald-500 hover:bg-emerald-600 text-white px-4 py-2 rounded-lg text-center mt-4 font-medium"
          on:click={() => menuOpen = false}
        >
          Verify as Citizen
        </a>
      </div>
    </div>
  {/if}
</header>

<style>
  .header-main {
    background: #082770;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    position: sticky;
    top: 0;
    z-index: 50;
  }
  
  .mobile-menu {
    background: #082770;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
  }
</style>
