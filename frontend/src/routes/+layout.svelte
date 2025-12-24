<script lang="ts">
  import '../app.css';
  import { onMount } from 'svelte';
  import { authStore } from '$lib/stores';
  import Header from '$lib/components/Header.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import { page } from '$app/stores';
  
  // Determine header variant based on current route
  $: headerVariant = $page.url.pathname === '/' ? 'transparent' : 
                     $page.url.pathname.startsWith('/citizen') ? 'citizen' :
                     $page.url.pathname.startsWith('/politician') ? 'politician' : 'default';
  
  // Initialize auth state from localStorage on mount
  onMount(() => {
    // The auth store automatically initializes from localStorage
    // This component ensures it's available in the component tree
  });
</script>

<Header variant={headerVariant} />

<slot />

<Footer />
