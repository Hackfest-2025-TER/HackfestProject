<script lang="ts">
  import {
    Shield,
    Users,
    FileText,
    Menu,
    X,
    LogOut,
    History,
    LayoutDashboard,
    UserPlus,
    Activity,
  } from "lucide-svelte";
  import { authStore } from "$lib/stores";

  export let variant: string = "default";

  let menuOpen = false;

  // Reactive auth state
  $: isAuthenticated = $authStore.isAuthenticated;
  $: nullifierShort = $authStore.credential?.nullifierShort || "";
  $: isPolitician = $authStore.credential?.isPolitician;

  // Logo destination: authenticated users go to citizen portal, others to landing
  $: logoHref = isAuthenticated ? "/citizen" : "/";

  function handleLogout() {
    authStore.logout();
    menuOpen = false;
  }

  // Navigation items
  $: navItems = isAuthenticated
    ? [
        { href: "/manifestos", label: "Promises", icon: FileText },
        { href: "/representatives", label: "Representatives", icon: Users },
        { href: "/audit-trail", label: "Audit Trail", icon: Activity },
        { href: "/citizen/votes", label: "My Votes", icon: History },
        ...(isPolitician
          ? [
              {
                href: "/representative/dashboard",
                label: "Dashboard",
                icon: LayoutDashboard,
              },
            ]
          : []),
      ]
    : [
        // Unauthenticated users see core navigation
        { href: "/manifestos", label: "Promises", icon: FileText },
        { href: "/representatives", label: "Representatives", icon: Users },
        { href: "/audit-trail", label: "Audit Trail", icon: Activity },
      ];
</script>

<header
  class="sticky top-0 z-50 bg-white/95 backdrop-blur-md border-b border-gray-200"
>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex justify-between items-center h-20">
      <!-- Logo -->
      <a href={logoHref} class="flex items-center space-x-3 group">
        <div
          class="bg-primary-700 p-2 rounded-lg text-white transition-transform group-hover:scale-105"
        >
          <Shield class="w-6 h-6 fill-current" />
        </div>
        <span
          class="text-xl font-serif font-bold text-gray-900 group-hover:text-primary-700 transition-colors"
          >PromiseThread</span
        >
      </a>

      <!-- Desktop Navigation -->
      <nav class="hidden md:flex items-center space-x-1">
        {#each navItems as item}
          <a
            href={item.href}
            class="flex items-center space-x-2 px-4 py-2 rounded-lg text-gray-600 font-medium hover:text-primary-700 hover:bg-primary-50 transition-all"
          >
            <svelte:component this={item.icon} class="w-4 h-4" />
            <span>{item.label}</span>
          </a>
        {/each}
      </nav>

      <!-- Auth Button / User Info -->
      <div
        class="hidden md:flex items-center space-x-4 pl-4 border-l border-gray-200 ml-4"
      >
        {#if isAuthenticated}
          <span
            class="text-sm text-gray-500 font-mono bg-gray-100 px-3 py-1 rounded-full"
            >{nullifierShort}</span
          >
          <button
            on:click={handleLogout}
            class="flex items-center space-x-2 text-gray-500 hover:text-error-600 transition-colors px-3 py-2 rounded-lg hover:bg-error-50"
            aria-label="Logout"
          >
            <LogOut class="w-4 h-4" />
            <span class="text-sm font-medium">Logout</span>
          </button>
        {:else}
          <a
            href="/auth"
            class="px-5 py-2.5 bg-primary-700 hover:bg-primary-800 text-white font-semibold rounded-xl shadow-lg shadow-primary-700/20 transition-all hover:shadow-xl"
          >
            Verify Citizen
          </a>
        {/if}
      </div>

      <!-- Mobile Menu Button -->
      <button
        class="md:hidden p-2 text-gray-600 hover:text-primary-700 hover:bg-gray-100 rounded-lg transition-colors"
        on:click={() => (menuOpen = !menuOpen)}
        aria-label="Menu"
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
    <div
      class="md:hidden border-t border-gray-200 bg-white animate-fade-in shadow-lg absolute w-full left-0"
    >
      <div class="px-4 py-4 space-y-2">
        {#each navItems as item}
          <a
            href={item.href}
            class="flex items-center space-x-3 px-4 py-3 rounded-xl text-gray-700 hover:bg-primary-50 hover:text-primary-700 transition-colors"
            on:click={() => (menuOpen = false)}
          >
            <svelte:component this={item.icon} class="w-5 h-5" />
            <span class="font-medium">{item.label}</span>
          </a>
        {/each}
        {#if isAuthenticated}
          <div class="pt-4 mt-4 border-t border-gray-100">
            <div class="flex items-center justify-between px-4 mb-4">
              <span
                class="text-sm text-gray-500 font-mono bg-gray-100 px-3 py-1 rounded-full"
                >{nullifierShort}</span
              >
            </div>
            <button
              on:click={handleLogout}
              class="flex items-center space-x-3 w-full px-4 py-3 rounded-xl text-error-600 hover:bg-error-50 transition-colors"
            >
              <LogOut class="w-5 h-5" />
              <span class="font-medium">Logout</span>
            </button>
          </div>
        {:else}
          <div class="pt-4 mt-4 border-t border-gray-100">
            <a
              href="/auth"
              class="flex items-center justify-center w-full px-5 py-3 bg-primary-700 hover:bg-primary-800 text-white font-semibold rounded-xl shadow-lg shadow-primary-700/20 text-lg transition-all"
              on:click={() => (menuOpen = false)}
            >
              Verify Citizen
            </a>
          </div>
        {/if}
      </div>
    </div>
  {/if}
</header>
