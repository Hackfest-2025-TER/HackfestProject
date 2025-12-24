<script lang="ts">
  import '../app.css';
  import { onMount } from 'svelte';
  import { authStore } from '$lib/stores';
  
  // Initialize auth state from localStorage on mount
  onMount(() => {
    // The auth store automatically initializes from localStorage
    // This component ensures it's available in the component tree
  });
</script>

<slot />
